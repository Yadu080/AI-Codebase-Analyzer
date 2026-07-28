# AI Codebase Analyzer — Complete Technical Knowledge Base

This handbook is the interview study guide for **your** project: a Retrieval-Augmented Generation (RAG) tool that clones a public Git repository, embeds code chunks with SentenceTransformers (`all-MiniLM-L6-v2`), indexes them with FAISS `IndexFlatL2`, and answers questions via Groq (`llama-3.3-70b-versatile`).

**How to study:** read chapters 1→20 in order once, then drill Chapter 19 question banks aloud. Use Chapter 20 for timed mock defence.

**Honesty rule used throughout:** features that are *not* in the repo (Docker, Redis, MongoDB, auth, tests, CI) are labeled as **not implemented** or **proposed**. Never claim them in an interview unless you build them.

---

## Chapter map

| Ch | File | Focus |
|---|---|---|
| 1 | [01-project-overview.md](01-project-overview.md) | Problem, users, value, limits, architecture snapshot |
| 2 | [02-system-design.md](02-system-design.md) | Components, data/request paths, bottlenecks, diagrams |
| 3 | [03-tech-stack.md](03-tech-stack.md) | Every library: why chosen, alternatives, comparison tables |
| 4 | [04-project-structure.md](04-project-structure.md) | Every folder/file/function and execution flow |
| 5 | [05-request-flow.md](05-request-flow.md) | Click-by-click UI → API → model → render |
| 6 | [06-data-pipeline.md](06-data-pipeline.md) | Input → chunk → embed → index → retrieve → generate |
| 7 | [07-technology-in-depth.md](07-technology-in-depth.md) | Internals: FastAPI, FAISS, MiniLM, Groq, Streamlit, … |
| 8 | [08-algorithms.md](08-algorithms.md) | Chunking, L2 k-NN, AST, complexity math |
| 9 | [09-database-and-storage.md](09-database-and-storage.md) | What “storage” means here (disk clones + RAM FAISS) |
| 10 | [10-ai-rag-pipeline.md](10-ai-rag-pipeline.md) | Embeddings, retrieval, prompts, hallucination, eval |
| 11 | [11-metrics.md](11-metrics.md) | Latency, Recall@K, cost, switch-impact tables |
| 12 | [12-security.md](12-security.md) | XSS, injection, secrets, RAG attacks, mitigations |
| 13 | [13-edge-cases.md](13-edge-cases.md) | Empty input, huge repos, failures, concurrency |
| 14 | [14-scalability.md](14-scalability.md) | 1 → 100k users; queues; K8s trigger points |
| 15 | [15-deployment.md](15-deployment.md) | `run.sh` today + proposed Docker/CI/cloud |
| 16 | [16-testing.md](16-testing.md) | Test strategy (none exist yet — proposed suite) |
| 17 | [17-design-decisions.md](17-design-decisions.md) | Decision records with tradeoffs |
| 18 | [18-project-improvements.md](18-project-improvements.md) | FAANG rebuild + prioritized roadmap |
| 19 | [19-interview-preparation.md](19-interview-preparation.md) | 1400 questions across 14 banks |
| 20 | [20-final-project-defence.md](20-final-project-defence.md) | Progressive mock interview |

---

## Chapter 19 question banks (100 each)

| # | File | Theme |
|---|---|---|
| 1 | [01-beginner-100.md](chapter-19-question-bank/01-beginner-100.md) | Beginner |
| 2 | [02-intermediate-100.md](chapter-19-question-bank/02-intermediate-100.md) | Intermediate |
| 3 | [03-advanced-100.md](chapter-19-question-bank/03-advanced-100.md) | Advanced |
| 4 | [04-system-design-100.md](chapter-19-question-bank/04-system-design-100.md) | System design |
| 5 | [05-backend-100.md](chapter-19-question-bank/05-backend-100.md) | Backend |
| 6 | [06-ai-100.md](chapter-19-question-bank/06-ai-100.md) | AI / RAG / LLM |
| 7 | [07-ml-100.md](chapter-19-question-bank/07-ml-100.md) | ML |
| 8 | [08-cloud-100.md](chapter-19-question-bank/08-cloud-100.md) | Cloud |
| 9 | [09-devops-100.md](chapter-19-question-bank/09-devops-100.md) | DevOps |
| 10 | [10-security-100.md](chapter-19-question-bank/10-security-100.md) | Security |
| 11 | [11-database-100.md](chapter-19-question-bank/11-database-100.md) | Database / storage |
| 12 | [12-architecture-100.md](chapter-19-question-bank/12-architecture-100.md) | Architecture |
| 13 | [13-hr-100.md](chapter-19-question-bank/13-hr-100.md) | HR / behavioral |
| 14 | [14-project-defense-100.md](chapter-19-question-bank/14-project-defense-100.md) | Project defence |

---

## One-page system truth

```
Browser → Streamlit (frontend.py)
        → HTTP POST → FastAPI (app/api.py) :8000
            /analyze: clone → load → chunk(500 chars) → embed(MiniLM 384d)
                      → FAISS IndexFlatL2 → pipeline{chunks,index,summary}
            /ask:     embed query → top_k=5 → Groq Llama 3.3 70B → answer
            /architecture: AST import graph (UI currently builds graph locally too)
```

**Critical interview facts**

- Similarity metric in code: **L2**, not a cosine API call  
- State: **one in-memory repo** in `pipeline = {{}}`  
- No MongoDB, Redis, Docker, auth, or automated tests in the current repo  
- LLM: Groq; embeddings: local SentenceTransformers  

---

## Suggested 7-day study plan

| Day | Focus |
|---|---|
| 1 | Ch 1–4 + draw architecture from memory |
| 2 | Ch 5–8 + complexity math |
| 3 | Ch 9–12 + security threat model |
| 4 | Ch 13–16 + failure drills |
| 5 | Ch 17–18 + roadmap pitch |
| 6 | Ch 19 banks (2–3 categories) aloud |
| 7 | Ch 20 full mock defence |

---

## Source of truth

If docs and code disagree, **trust the code** under `app/` and `frontend.py`, then fix the docs.
