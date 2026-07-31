import gc
import logging
import os
import threading
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import index_cache
from app.repo_loader import (
    clone_repository,
    get_head_sha,
    InvalidRepoUrlError,
    CloneTimeoutError,
)
from app.code_parser import load_code_files
from app.chunker import chunk_code
from app.embedder import embed_chunks, embed_query, warm_up
from app.vector_store import build_index
from app.retriever import retrieve
from app.qa_engine import generate_answer
from app.architecture import build_dependency_graph
from app.repo_summary import generate_repo_summary

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("ai_codebase_analyzer")


def _limit(env_name, default):
    """Read a size limit from the environment. 0 (the default) means no limit."""
    value = int(os.getenv(env_name, str(default)))
    return value if value > 0 else None


# No caps by default — a local machine has the memory to index a whole
# repository. Set these env vars to a positive number only if you want to
# deliberately bound a very large run.
MAX_CHUNKS = _limit("MAX_CHUNKS", 0)
MAX_SOURCE_CHARS = _limit("MAX_SOURCE_CHARS", 0)
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "3"))
CLONE_TIMEOUT_SECONDS = int(os.getenv("CLONE_TIMEOUT_SECONDS", "600"))
USE_INDEX_CACHE = os.getenv("USE_INDEX_CACHE", "1") != "0"

# Anything that changes the vectors must change the cache key.
_CACHE_FINGERPRINT = "|".join(
    [
        os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        str(MAX_CHUNKS),
        str(MAX_SOURCE_CHARS),
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the embedding model in the background so the first /analyze isn't
    # paying for it — by the time a repo finishes cloning it's usually ready.
    def _warm():
        try:
            logger.info("Warming up embedding model in the background...")
            warm_up()
            logger.info("Embedding model warm and ready")
        except Exception:
            logger.warning("Model warm-up failed; will load on first use", exc_info=True)

    threading.Thread(target=_warm, daemon=True).start()
    yield


app = FastAPI(
    title="AI Codebase Analyzer API",
    description="RAG pipeline for GitHub repository analysis",
    version="1.0.0",
    lifespan=lifespan,
)

_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]
_extra = os.getenv("CORS_ORIGINS", "")
_origins = [o.strip() for o in _extra.split(",") if o.strip()] + _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if "*" not in _origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RepoRequest(BaseModel):
    repo_url: str
    refresh: bool = False


class QuestionRequest(BaseModel):
    question: str
    session_id: str


class ArchitectureRequest(BaseModel):
    session_id: str


sessions: dict = {}
_session_order: list = []
_sessions_lock = threading.Lock()


def _evict_session(session_id: str):
    # Only the in-memory index is released. The clone and its cached index
    # stay on disk so re-analyzing the same repo is near-instant.
    if sessions.pop(session_id, None) is not None:
        gc.collect()
        logger.info("Released session %s from memory", session_id)


def _store_session(session_id: str, data: dict):
    with _sessions_lock:
        sessions[session_id] = data
        _session_order.append(session_id)
        while len(_session_order) > MAX_SESSIONS:
            _evict_session(_session_order.pop(0))


def _get_session(session_id: str) -> dict:
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Analyze the repository again.",
        )
    return session


@app.get("/")
def root():
    return {
        "service": "AI Codebase Analyzer API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok", "active_sessions": len(sessions)}


@app.post("/analyze")
def analyze_repo(request: RepoRequest):
    repo_url = request.repo_url.strip()
    if not repo_url:
        raise HTTPException(status_code=400, detail="repo_url is required")

    started = time.time()

    try:
        repo_path = clone_repository(
            repo_url,
            timeout_seconds=CLONE_TIMEOUT_SECONDS,
            refresh=request.refresh,
        )
    except InvalidRepoUrlError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except CloneTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc))
    except Exception as exc:
        logger.exception("Clone failed for %s", repo_url)
        raise HTTPException(
            status_code=400, detail=f"Failed to clone repository: {exc}"
        )

    key = index_cache.cache_key(repo_path, get_head_sha(repo_path), _CACHE_FINGERPRINT)
    cached = index_cache.load(key) if (USE_INDEX_CACHE and not request.refresh) else None

    if cached is not None:
        index, chunks, summary = cached
        from_cache = True
        logger.info("Loaded %d chunks from cache", len(chunks))
    else:
        from_cache = False

        files = load_code_files(repo_path, max_total_chars=MAX_SOURCE_CHARS)
        logger.info("Loaded %d source files", len(files))

        chunks = chunk_code(files, max_chunks=MAX_CHUNKS)
        logger.info("Built %d chunks", len(chunks))

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No supported source files found (.py, .js, .ts, .java, .cpp, .c)",
            )

        logger.info("Embedding %d chunks (the slow part on large repos)...", len(chunks))
        embeddings = embed_chunks(chunks)
        index = build_index(embeddings)
        del embeddings
        gc.collect()

        summary = generate_repo_summary(repo_path, chunks)

        if USE_INDEX_CACHE:
            index_cache.save(key, index, chunks, summary)

    session_id = uuid.uuid4().hex
    _store_session(
        session_id,
        {
            "chunks": chunks,
            "index": index,
            "summary": summary,
            "repo_path": repo_path,
            "created_at": time.time(),
        },
    )

    elapsed = time.time() - started
    logger.info("Ready in %.1fs (session %s)", elapsed, session_id)

    if from_cache:
        message = f"Loaded cached index in {elapsed:.1f}s"
    else:
        message = f"Repository indexed in {elapsed:.0f}s"
        if MAX_CHUNKS is not None and len(chunks) >= MAX_CHUNKS:
            message += f" (stopped at the MAX_CHUNKS limit of {MAX_CHUNKS})"

    return {
        "message": message,
        "chunks": len(chunks),
        "summary": summary,
        "session_id": session_id,
        "cached": from_cache,
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    session = _get_session(request.session_id)

    query_embedding = embed_query(question)
    retrieved = retrieve(session["index"], query_embedding, session["chunks"])

    try:
        answer = generate_answer(question, retrieved)
    except RuntimeError as exc:
        logger.exception("Groq request failed")
        raise HTTPException(status_code=502, detail=str(exc))

    return {"answer": answer}


@app.post("/architecture")
def architecture(request: ArchitectureRequest):
    session = _get_session(request.session_id)
    graph = build_dependency_graph(session["repo_path"])
    return {"architecture": graph}
