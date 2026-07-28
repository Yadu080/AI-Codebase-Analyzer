# Chapter 7 — Every Technology In Depth

## How to use this chapter

Each section follows: **WHY it exists → WHAT it is → internal model → lifecycle in THIS project → memory/concurrency → performance → failure modes → production practices → when NOT to use → interview angles.**

Acronyms: ASGI (Async Server Gateway Interface), GIL (Global Interpreter Lock), ANN (Approximate Nearest Neighbor), SBERT (Sentence-BERT), LPU (Language Processing Unit — Groq marketing term for their inference hardware lineage).

---

## 1. FastAPI (+ Pydantic + Starlette)

### WHY
HTTP APIs need routing, validation, serialization. FastAPI packages Starlette (ASGI web) + Pydantic (schemas).

### WHAT in this project
`app/api.py` creates `app = FastAPI()`, defines `RepoRequest`/`QuestionRequest`, registers three POST routes.

### Internal architecture
```
Client → TCP → Uvicorn → ASGI callable (FastAPI)
  → routing → dependency injection (unused here)
  → Pydantic validation → endpoint function → JSONable response
```

### Request lifecycle for `/ask`
1. Parse HTTP
2. Match route
3. Validate JSON → `QuestionRequest`
4. Run sync `ask_question` (blocks worker)
5. Serialize dict → JSON

### Memory model
Framework overhead is small (tens of MB). Dominated by imported embedding model living in same process.

### Concurrency model
ASGI can multiplex IO-bound async endpoints. **This project uses sync `def`**, so heavy CPU/network work blocks the worker thread/event loop slot depending on server config. Uvicorn runs sync endpoints in a threadpool, but a small threadpool still saturates under many `/analyze` calls.

### Performance
Framework overhead ≪ embedding + LLM. Optimizing FastAPI microbenchmarks will not save you.

### Failure modes
Unhandled `KeyError` if `pipeline` empty; unhandled clone failures; no timeouts to Groq.

### Production practices
- Prefer `async def` + thread offload or job queue for long analyze
- Add middleware: timing, request IDs, CORS, auth
- Do not store durable state in module globals
- Use lifespan hooks for model load

### Company usage
Widely used for Python ML microservices (many startups; internal tools at large cos).

### When NOT to use
JVM shops; GraphQL-first platforms already on other stacks; ultra-simple scripts (use functions).

---

## 2. Uvicorn

### WHY
FastAPI is not a server; Uvicorn is.

### Lifecycle
`uvicorn app.api:app --reload` imports module (loads MiniLM!), binds port 8000, serves.

### `--reload` WARNING
Spawns reloader + server; in-memory `pipeline` resets on code change; do not use in prod.

### Multi-worker failure with this app
N workers ⇒ N isolated `pipeline` dicts. Sticky sessions do not fix cold workers without shared index store.

### Production
Gunicorn with `UvicornWorker`, or container orchestration with single responsibility process + external state.

---

## 3. Streamlit

### WHY
Python-centric interactive UI without JS build pipeline.

### Internal model: rerun
Every widget interaction re-executes script. Branching on `st.button` determines side effects (HTTP calls).

### Memory
One Python process; Matplotlib figures for graphs can be heavy; CSS injected each run.

### Concurrency
One user session model is simple; multi-user Streamlit needs careful session isolation — still not a replacement for a real API gateway under load.

### Security failure mode
`unsafe_allow_html=True` + LLM answer interpolation ⇒ XSS.

### When NOT
Complex authenticated SaaS frontends; offline mobile; pixel-perfect design systems.

---

## 4. requests

### Lifecycle
`requests.post(url, json=...)` opens HTTP connection, sends JSON, blocks until response.

### Gaps in project
No `timeout=`; no retries; no connection pooling tuning; assumes localhost.

### Production
Set timeouts `(connect, read)`; retry idempotent GETs carefully; for POST analyze use job IDs not blind retries.

---

## 5. GitPython

### Internal
Shells out / uses Git plumbing to clone into working directory.

### Memory / disk
Clone size ≈ repo size; history can be huge. No shallow clone in code.

### Failure modes
Auth failures; disk full; `git` missing; existing dirty partial dirs; name collisions.

### Production practices
Shallow clone, size quotas, virus scanning optional, isolate clones per job ID, delete after TTL, never execute cloned code.

---

## 6. SentenceTransformers + MiniLM-L6-v2

### WHY SBERT-like models
Map variable-length text to fixed vectors where semantic similarity ≈ vector proximity.

### Architecture (simplified)
Transformer encoder (MiniLM distilled) → pooling (mean) → 384-d embedding. Often L2-normalized.

### Memory
Weights ~ tens of MB to low hundreds including tokenizer + runtime; plus activation memory during batch encode.

### Threading
PyTorch/transformers underlying; GIL released in many native ops; still CPU-heavy. Parallel encode across threads has diminishing returns.

### Lifecycle in project
Loaded at import of `embedder.py` (pulled in by `api.py`) ⇒ cold start on Uvicorn boot.

### Performance drivers
Batch size, sequence length, CPU vs GPU, chunk count.

### Failure modes
OOM on huge batch; first-time model download needs network; domain mismatch (natural language model on code).

### Production
Separate embedding microservice; batch requests; cache embeddings by content hash; version embedding model ID with index.

### When NOT
Need best code retrieval quality → try code-specific embedders; need multilingual → different model.

---

## 7. FAISS IndexFlatL2

### WHY FlatL2
Exact search, no training, easy correctness.

### Internal
Contiguous float32 matrix N×D; query computes ∑(x_i − y_i)²; select k smallest (via linear scan / BLAS-ish routines).

### Memory
Raw vectors: `N * D * 4` bytes. Chunk text in Python usually dominates.

### Concurrency
FAISS index object not always safe for concurrent writers; readers often OK depending on version/ops — treat as single-threaded mutate in this app.

### Performance
Query ~ O(N·D). Fine for 10k–100k vectors on CPU; painful at many millions without ANN (IVF, HNSW).

### Failure modes
Empty add; dimension mismatch; process crash loses index.

### Production
`faiss.write_index` / `read_index`; or migrate to managed ANN with filters.

### Company usage
FAISS underlies many retrieval stacks; Meta open-sourced; used inside larger systems.

---

## 8. NumPy

Bridge between Python lists/ndarrays and FAISS. Vectorized ops; C-backed buffers.

### When NOT
Extreme GPU-only pipelines may use torch tensors end-to-end — still often convert for FAISS CPU.

---

## 9. Groq SDK + Llama 3.3 70B

### WHY hosted LLM
Avoid local GPU for generation.

### Lifecycle
Build prompt string → HTTPS API → completion text.

### Memory
Client is light; prompt size drives **cost and latency**, not local RAM.

### Failure modes
Missing `GROQ_API_KEY`; 429 rate limit; timeouts; model deprecation; prompt injection.

### Production
Gateway with auth, budgets, timeouts, fallback models, output filtering, logging of prompts with PII redaction policy.

### Temperature 0.2
Reduces randomness; does not guarantee factuality.

---

## 10. python-dotenv

Reads `.env` into `os.environ`. Local DX convenience — not a secret manager.

### Production
Cloud secret stores; IAM; never bake secrets into images.

---

## 11. NetworkX + Matplotlib + AST

### AST
Python parses source to tree; `ast.walk` yields nodes; collect import names.

### NetworkX
In-memory graph algorithms library; here used as DiGraph container + drawing layout.

### Matplotlib
Renders to figure; Streamlit displays.

### Limits
Basename collisions; non-Python ignored; large graphs unreadable; `plt.show()` not Streamlit-friendly (frontend uses `st.pyplot`).

---

## 12. Cross-technology request timeline (typical `/ask`)

| Step | Tech | Bound by |
|---|---|---|
| Click | Streamlit | User |
| HTTP POST | requests | localhost RTT |
| Validate | Pydantic | μs |
| Embed query | MiniLM | ~10–100ms CPU |
| Search | FAISS | ~ms for small N |
| Prompt+LLM | Groq | ~0.5–5s+ |
| Render | Streamlit HTML | ms–tens ms |

---

## Interview questions

### Beginner
### 1. What loads the embedding model?
**Question:** When is MiniLM loaded?
**Ideal Answer:** At import of embedder (when API process starts), not per request.
**Why interviewer asked it:** Cold start awareness.
**Common mistakes:** Saying every ask reloads the model.
**Follow-up questions:** How would you lazy-load?

### 2. What does Uvicorn do?
**Question:** Role of Uvicorn?
**Ideal Answer:** ASGI server hosting FastAPI on a port.
**Why interviewer asked it:** Server vs framework.
**Common mistakes:** Calling FastAPI the server.
**Follow-up questions:** Why avoid --reload in prod?


### Intermediate
### 1. Sync endpoints
**Question:** Why can sync FastAPI endpoints be a problem?
**Ideal Answer:** Long clone/embed/LLM work occupies worker capacity; throughput collapses under concurrent analyzes.
**Why interviewer asked it:** Concurrency.
**Common mistakes:** Async keyword alone fixes CPU.
**Follow-up questions:** Threadpool vs task queue?

### 2. FAISS memory
**Question:** Estimate RAM for 100k vectors.
**Ideal Answer:** 100k*384*4 ≈ 153.6MB raw + Python chunk strings often larger.
**Why interviewer asked it:** Back-of-envelope.
**Common mistakes:** Ignoring text storage.
**Follow-up questions:** How to persist?


### Advanced
### 1. Separate embedding service
**Question:** Why split embedding into its own service?
**Ideal Answer:** Independent scale, GPU pool, version pins, protect API workers from OOM, cache layer.
**Why interviewer asked it:** Service decomposition.
**Common mistakes:** Split for fashion.
**Follow-up questions:** API contract for vectors?


### FAANG
### 1. Multi-tenant isolation
**Question:** How would FAISS-in-process fail multi-tenant SaaS?
**Ideal Answer:** Shared memory index, no ACL, overwrite risk, noisy neighbor CPU. Need per-tenant indexes or filtered vector DB + authz.
**Why interviewer asked it:** SaaS readiness.
**Common mistakes:** Just add Kubernetes.
**Follow-up questions:** Encryption of vectors at rest?


### Trick
### 1. Is FAISS a database?
**Question:** Is FAISS a database?
**Ideal Answer:** No — similarity search library; durability/transactions/query language not its job.
**Why interviewer asked it:** Buzzword precision.
**Common mistakes:** Yes it is our MongoDB.
**Follow-up questions:** What would you add for durability?


---

## Study checklist
- [ ] Explain ASGI vs WSGI
- [ ] Explain why MiniLM load at import matters
- [ ] Compute IndexFlatL2 query complexity
- [ ] List failure modes of Groq dependency


---

## Appendix A — End-to-end memory budget (worked example)

Assume a medium Python repo after filtering:

| Item | Estimate |
|---|---|
| MiniLM weights + runtime | ~100–300 MB RSS contribution |
| 20,000 chunks × ~500 chars | ~10 MB raw text; Python objects often 3–10× → ~30–100 MB |
| 20,000 × 384 × 4 bytes FAISS | ~30.7 MB |
| NetworkX graph for ~200 files | small (MBs) |
| FastAPI + Uvicorn + Streamlit | tens of MB each process |

**Interview line:** “Vectors are not always the dominant RAM consumer — Python chunk strings and the embedding model often dominate at demo scale.”

### Threading / GIL notes for encode

`model.encode` releases the GIL during much of the underlying compute, but running many concurrent encodes in one process still contends for CPU caches and RAM. Prefer batching inside one encode call over naive thread storms.

### FAISS `search` return values

```python
distances, indices = index.search(query_embedding, top_k)
```

- `distances` shape `(nq, k)` — L2 distances (smaller = closer)
- `indices` shape `(nq, k)` — row ids into the order of `index.add`
- This project **throws away distances** — you cannot show confidence in the UI today

### Groq request lifecycle

```
TLS handshake → auth header with API key → JSON chat.completions
→ model scheduling on provider infra → tokens streamed or full
→ client reads choices[0].message.content
```

Failure modes: 401 bad key, 429 rate limit, 5xx, network timeout (not set in client code), model rename/deprecation.

### Streamlit + Matplotlib interaction

Each analyze success path builds a `fig` and calls `st.pyplot(fig)`. Large graphs: layout time + browser render dominate. For interviews: “I’d cap nodes or switch to interactive Plotly/CytoWeb for big repos.”

### Production best-practices checklist per tech

| Tech | Do | Don't |
|---|---|---|
| FastAPI | Lifespan model load; request IDs | Global mutable business state |
| Uvicorn | Multiple workers only with shared store | `--reload` in prod |
| Streamlit | Escape HTML | Blind `unsafe_allow_html` |
| GitPython | Shallow clone + quotas | Clone secrets-laden private repos to SaaS LLM blindly |
| ST/MiniLM | Version pin; warm pool | Silently change model under existing index |
| FAISS | Persist + checksum | Assume multi-writer safety |
| Groq | Timeouts, budgets, redaction | Infinite retries |
| dotenv | Local only | As cloud secret system |

---

## Appendix B — Company usage patterns (interview color)

| Tech | Typical real-world use |
|---|---|
| FastAPI | ML model wrappers, internal APIs |
| FAISS | Candidate retrieval inside ads/search/recsys prototypes and production with ANN variants |
| SentenceTransformers | Semantic search prototypes, clustering |
| Streamlit | Internal dashboards, research demos |
| NetworkX | Small/medium graph analytics; not web-scale graph DB |

