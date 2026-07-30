from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gc
import os

from app.repo_loader import clone_repository
from app.code_parser import load_code_files
from app.chunker import chunk_code
from app.embedder import embed_chunks, embed_query
from app.vector_store import build_index
from app.retriever import retrieve
from app.qa_engine import generate_answer
from app.architecture import build_dependency_graph
from app.repo_summary import generate_repo_summary

app = FastAPI(
    title="AI Codebase Analyzer API",
    description="RAG pipeline for GitHub repository analysis",
    version="1.0.0",
)

# Allow local Next.js + any Vercel preview/production origins via env.
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
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Caps peak memory on RAM-constrained hosts (e.g. Render's 512MB free tier)
# by bounding how many chunks get embedded and held in memory at once.
MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "4000"))


class RepoRequest(BaseModel):
    repo_url: str


class QuestionRequest(BaseModel):
    question: str


pipeline = {}


@app.get("/")
def root():
    return {
        "service": "AI Codebase Analyzer API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "indexed": "index" in pipeline and "chunks" in pipeline,
        "chunks": len(pipeline.get("chunks", [])),
    }


@app.post("/analyze")
def analyze_repo(request: RepoRequest):
    if not request.repo_url.strip():
        raise HTTPException(status_code=400, detail="repo_url is required")

    repo_path = clone_repository(request.repo_url.strip())
    files = load_code_files(repo_path)
    chunks = chunk_code(files)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No supported source files found (.py, .js, .ts, .java, .cpp, .c)",
        )

    truncated = len(chunks) > MAX_CHUNKS
    if truncated:
        chunks = chunks[:MAX_CHUNKS]

    embeddings = embed_chunks(chunks)
    index = build_index(embeddings)
    del embeddings
    gc.collect()

    pipeline["chunks"] = chunks
    pipeline["index"] = index

    summary = generate_repo_summary(repo_path, chunks)
    pipeline["summary"] = summary

    message = "Repository indexed successfully"
    if truncated:
        message += f" (truncated to first {MAX_CHUNKS} chunks to stay within host memory limits)"

    return {
        "message": message,
        "chunks": len(chunks),
        "summary": summary,
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question is required")

    if "index" not in pipeline or "chunks" not in pipeline:
        raise HTTPException(
            status_code=400,
            detail="No repository indexed yet. Call /analyze first.",
        )

    query_embedding = embed_query(request.question.strip())
    retrieved = retrieve(
        pipeline["index"],
        query_embedding,
        pipeline["chunks"],
    )
    answer = generate_answer(request.question.strip(), retrieved)
    return {"answer": answer}


@app.post("/architecture")
def architecture(request: RepoRequest):
    if not request.repo_url.strip():
        raise HTTPException(status_code=400, detail="repo_url is required")

    repo_path = clone_repository(request.repo_url.strip())
    graph = build_dependency_graph(repo_path)
    return {"architecture": graph}
