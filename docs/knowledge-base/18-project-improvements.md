# Chapter 18 — Project Improvements

## 0. Frame

Interviewers love: “If you had 4 more weeks / if FAANG built this, what changes?” Rank by **impact / effort**.

---

## 1. How FAANG would build this (reference architecture)

```
UI (web) → API Gateway → AuthZ
   ├─ Ingest Service → Object Storage (repos@sha) → Embed Workers → Vector DB
   ├─ Query Service → Retriever + Reranker → LLM Gateway → Answer + Citations
   ├─ Metadata DB (Postgres)
   ├─ Cache (Redis)
   ├─ Queue (Pub/Sub / SQS)
   ├─ Obs (metrics/logs/traces)
   └─ Eval service + experiment platform
```

Differences from yours: durable multi-tenant state, async ingest, citations, eval, security, SLOs.

---

## 2. Prioritized roadmap

### P0 — Correctness & safety (1–2 weeks)
- Handle empty `pipeline` with 400
- HTML-escape answers
- Timeouts on Groq + git
- Ignore `node_modules`/`.git`
- Persist FAISS + chunks to disk keyed by repo
- Basic logging

### P1 — Product quality (2–4 weeks)
- Overlapping or AST-aware chunking
- Return citations + distances
- Job queue for analyze + progress UI
- Config via env (chunk_size, top_k, model)
- pytest suite + CI
- Secret scanning before send to LLM

### P2 — Scale (1–2 months)
- Per-user/per-repo indexes
- Redis cache
- ANN index or Pinecone/pgvector
- Auth (API keys/OAuth)
- Docker Compose
- Metrics dashboards

### P3 — Research / enterprise
- Hybrid BM25 + dense
- Cross-encoder reranker
- Code-specialized embeddings
- Agent tools (jump to def)
- SSO, audit logs, VPC deploy
- Incremental index on git push webhook

---

## 3. Cost optimizations

| Lever | Effect |
|---|---|
| Cache answers | ↓ LLM $ |
| Smaller context / top_k | ↓ tokens |
| Local embed remain | avoid embed $ |
| Shallow clone | ↓ network/disk |
| Don't re-embed unchanged files | ↓ CPU |
| Cheaper model for easy Qs | ↓ $ |

---

## 4. Performance optimizations

- Batch encode
- Persist index
- Warm model pools
- Async ingest
- HNSW when C large
- Avoid Streamlit for HPA frontend at scale

---

## 5. Research improvements

- Repo-level hierarchical summaries (RAPTOR-like)
- Fine-tune embedder on code Q&A
- Execution-augmented answers in sandbox (high risk)
- Multilingual code

---

## 6. Maintainability

- Replace global dict with service class + repository pattern
- Typed chunk model
- Single graph builder used by API and UI
- Remove bare excepts

---

## Interview questions

### Beginner

#### 1. Next feature
**Question:** What would you add next?
**Ideal Answer:** Persist index + error if ask before analyze + escape HTML.
**Why interviewer asked it:** Prioritization.
**Common mistakes:** Rewrite in K8s first.
**Follow-up questions:** Why those?


### Intermediate

#### 1. FAANG gap
**Question:** Biggest gap vs production?
**Ideal Answer:** No multi-tenant durable state, auth, async ingest, eval, observability.
**Why interviewer asked it:** Self-awareness.
**Common mistakes:** UI CSS.
**Follow-up questions:** What first?


### Advanced

#### 1. Citations
**Question:** How add citations?
**Ideal Answer:** Return chunk metadata with answer; prompt require quotes; UI links to file paths; verify spans.
**Why interviewer asked it:** Grounding.
**Common mistakes:** Trust model.
**Follow-up questions:** Hallucinated citations?


### FAANG

#### 1. 18 month plan
**Question:** Platform vision?
**Ideal Answer:** Code intelligence platform: ingest, search, answer, agents, eval, enterprise controls; embedding versioning; cost SLOs.
**Why interviewer asked it:** Leadership.
**Common mistakes:** Feature laundry list.
**Follow-up questions:** Kill criteria?


### Trick

#### 1. Rewrite?
**Question:** Should you rewrite in Go?
**Ideal Answer:** Not first — bottlenecks are embed/LLM/state, not FastAPI. Rewrite when justified by measured limits.
**Why interviewer asked it:** Judgment.
**Common mistakes:** Always rewrite.
**Follow-up questions:** What measure?



---

## Appendix A — 30 / 60 / 90 day plan

| Day 30 | Day 60 | Day 90 |
|---|---|---|
| Persist index, errors, ignore dirs, tests+CI, HTML escape | Queue analyze, citations, auth API key, metrics | Hybrid search, reranker, multi-tenant, Docker cloud deploy |

## Appendix B — Research directions (with caveats)

| Idea | Upside | Risk |
|---|---|---|
| Hierarchical repo summaries | Better global questions | Stale summaries |
| Agent with tools | Multi-step debugging | Prompt injection↑ |
| Fine-tuned code embedder | Retrieval↑ | Train cost/ops |
| Execute code in sandbox | High trust answers | Catastrophic if sandbox escapes |

## Appendix C — What NOT to improve first

- Rewriting FastAPI in Spring/Go  
- Fancy CSS over correctness  
- Kubernetes before durable state  
- Adding LangChain without eval  

