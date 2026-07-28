# Chapter 11 — Metrics

## 0. WHY metrics matter

You cannot improve what you cannot measure. Interviewers expect you to separate **system metrics** (latency, cost) from **retrieval quality metrics** (Recall@K, MRR) from **generation quality** (human eval, rubrics) — this project currently measures **almost none** in code.

---

## 1. Latency, response time, P95, P99

### Definitions
- **Latency:** time for an operation (embed, search, LLM).
- **Response time:** end-to-end user perceived time.
- **P95/P99:** 95th/99th percentile of latency distribution — tail behavior.

### Formula
Sort N samples; P95 ≈ value at index `ceil(0.95·N)-1`.

### Good/bad for this demo (heuristic)
| Endpoint | Good | Bad | Ideal demo |
|---|---|---|---|
| `/ask` | < 3s | > 15s | < 2s |
| `/analyze` small repo | < 60s | > 10 min | < 30s |

### WHY tails matter
Users remember slow requests. Groq rate limits and GC spikes show in P99.

### Improve
Cache embeddings; async jobs for analyze; smaller context; warmer model; ANN if C huge.

### Tradeoffs
Lower latency via smaller top_k or shorter context can hurt answer quality.

---

## 2. Throughput

Requests completed per second. `/analyze` throughput near 0 under load because each request is heavy. `/ask` limited by Groq + embed CPU.

---

## 3. Retrieval metrics: Precision, Recall, F1, Recall@K, Hit Rate, MRR, MAP, NDCG

Assume a labeled set: for question q, relevant chunk IDs are gold.

| Metric | Formula intuition | Good | Bad |
|---|---|---|---|
| Precision@K | relevant_in_topK / K | >0.5 | <0.2 |
| Recall@K | relevant_in_topK / all_relevant | >0.7 | <0.3 |
| F1 | harmonic mean P/R | context-dependent | — |
| Hit Rate | 1 if ≥1 relevant in topK | >0.8 | <0.5 |
| MRR | mean 1/rank_first_relevant | >0.6 | <0.3 |
| MAP | mean average precision | higher better | — |
| NDCG | graded relevance discounted by rank | higher better | — |

**This project does not compute these.** You should say how you *would*.

### Cosine similarity / L2 distance
Similarity score between vectors — **not** a guaranteed answer quality metric. High similarity ≠ correct chunk.

---

## 4. Generation metrics: Accuracy, BLEU, ROUGE

| Metric | Use | Limitation for code QA |
|---|---|---|
| Accuracy | Closed answers | Rare in freeform |
| BLEU/ROUGE | n-gram overlap vs reference | Bad for paraphrased correct answers |
| LLM-as-judge | Scalable | Biased, costly |
| Human rubric | Gold standard | Expensive |

---

## 5. Resource metrics

| Metric | How measured | Ideal for demo |
|---|---|---|
| Memory | RSS of Uvicorn | Fits laptop RAM with model |
| CPU | encode+search | Not pegged 100% idle |
| GPU | N/A default | — |
| Index size | N*D*4 | Know your N |
| Cold start | time to first ready | < 30s acceptable demo |
| Token usage | prompt+completion tokens | Minimize unused context |
| Chunk size | 500 chars fixed | Tune via eval |
| Cache ratio | hits/total | 0 today (no cache) |
| Bandwidth | clone + API payloads | Avoid huge repos |
| Network calls | 1 Groq/ask + 1 HTTP UI | Batch where possible |
| Cost | Groq $/token + electricity | Track monthly |

---

## 6. Technology switch impact tables

### FAISS → Pinecone
| Metric | Likely change |
|---|---|
| Search latency | Network hop; may be similar/better at huge N |
| Ops complexity | ↓ (managed) |
| Cost | ↑ |
| Durability | ↑ |
| Cold start process | Index not rebuilt each boot if remote |

### SentenceTransformer → OpenAI Embeddings
| Metric | Change |
|---|---|
| Embedding quality | Often ↑ |
| Embedding cost | ↑↑ |
| Privacy | ↓ |
| Dim / index RAM | Often ↑ |
| Latency | Network variance |

### FastAPI → Flask
Little change to RAG metrics; ecosystem/docs differ; async story weaker.

### FastAPI → Spring Boot
Higher engineering cost; ML either out-of-process or JNI; cold start ↑; throughput potentially ↑ for pure IO.

### OpenAI LLM → Gemini (or Groq → X)
Latency/cost/quality shift by model; prompt may need retune; measure with same eval set.

### Cloud Run → Kubernetes
Ops complexity ↑; control ↑; scaling knobs ↑; not automatic quality win.

### Caching removed / never present
Cache ratio 0; repeat questions pay full LLM cost; latency stays high.

### Chunk size 500 → 200
| Metric | Change |
|---|---|
| C | ↑ |
| Index RAM | ↑ |
| Embed cost/time | ↑ |
| Boundary loss | ↓ mid-function? maybe ↑ fragmentation |
| Precision | often needs re-eval |

### Chunk size 500 → 2000
Fewer chunks; more coherent functions; may exceed useful embedding context; retrieval coarser.

### top_k 5 → 20
Recall↑ potential; tokens↑; latency↑; noise↑; cost↑.

### Embedding dim 384 → 1536
Index RAM ×4; sometimes quality↑; search slower roughly ×4 for flat.

---

## 7. UX impact

| Metric bad | User feels |
|---|---|
| High P99 ask | “AI is broken” |
| Low Recall@K | Confident wrong answers |
| Huge analyze latency | Abandon |
| High cost | Project dies in prod |

---

## Interview questions

### Beginner

#### 1. P95
**Question:** What is P95 latency?
**Ideal Answer:** Latency below which 95% of requests complete.
**Why interviewer asked it:** Tail literacy.
**Common mistakes:** Average only.
**Follow-up questions:** Why average lies?

#### 2. Recall@K
**Question:** Define Recall@5 for this app.
**Ideal Answer:** Fraction of relevant chunks found in the 5 retrieved.
**Why interviewer asked it:** RAG eval.
**Common mistakes:** Confusion with LLM accuracy.
**Follow-up questions:** How label relevance?


### Intermediate

#### 1. MRR
**Question:** Why MRR for code search?
**Ideal Answer:** Rewards putting first relevant chunk early — good when one key file matters.
**Why interviewer asked it:** Ranking quality.
**Common mistakes:** Using BLEU only.
**Follow-up questions:** MRR vs NDCG?

#### 2. Switch to Pinecone
**Question:** What metrics change?
**Ideal Answer:** Ops/durability improve; cost and network path change; quality only if retrieval config differs.
**Why interviewer asked it:** Systems thinking.
**Common mistakes:** Quality auto-improves.
**Follow-up questions:** How A/B?


### Advanced

#### 1. Eval harness
**Question:** Design offline eval for this repo.
**Ideal Answer:** Gold QA pairs; store relevant file spans; compute Recall@K/MRR; LLM-judge groundedness; latency budgets; regression CI.
**Why interviewer asked it:** ML eng maturity.
**Common mistakes:** Only vibe-check.
**Follow-up questions:** How prevent train/test leak?


### FAANG

#### 1. SLO design
**Question:** Propose SLOs.
**Ideal Answer:** e.g. ask P95 < 2s excluding LLM; groundedness ≥ X; cost < $Y/1k queries; analyze async with progress.
**Why interviewer asked it:** Production ownership.
**Common mistakes:** No numbers.
**Follow-up questions:** Error budget?


### Trick

#### 1. Cosine as accuracy
**Question:** Does high cosine mean correct answer?
**Ideal Answer:** No — only retrieval proximity; generation can still hallucinate.
**Why interviewer asked it:** Catch conflation.
**Common mistakes:** Yes.
**Follow-up questions:** How measure groundedness?



---

## Appendix A — How to measure in *this* codebase (proposed)

```python
# PROPOSED instrumentation sketch
import time
t0 = time.perf_counter()
# ... retrieve ...
retrieve_ms = (time.perf_counter() - t0) * 1000
```

Export: Prometheus histograms for `ask_embed_ms`, `ask_search_ms`, `ask_llm_ms`, `ask_total_ms`.

## Appendix B — Full switch-impact matrix (condensed)

| Change | Latency | Cost | Quality | Ops complexity | RAM |
|---|---|---|---|---|---|
| FAISS→Pinecone | network± | ↑ | ≈ (config) | ↓ | ↓ local |
| MiniLM→OpenAI emb | network± | ↑↑ | often ↑ | ↑ | ↑ if higher dim |
| Groq→OpenAI GPT | ± | ± | ± eval | ≈ | ≈ |
| FastAPI→Flask | ≈ | ≈ | ≈ | ≈ | ≈ |
| FastAPI→Spring | warm↑ | eng↑ | ≈ | ↑ | JVM↑ |
| Add Redis cache | ↓ repeat | ↓ LLM | ≈ | ↑ | ↑ Redis |
| Remove cache (N/A) | — | — | — | — | — |
| Dockerize | ≈ | ≈ | ≈ | ↑ initially then ↓ drift | image size |
| Chunk 500→200 | analyze↑ ask≈ | embed↑ | ? eval | ≈ | ↑ |
| Chunk 500→2000 | analyze↓ | embed↓ | ? eval | ≈ | ↓ |
| Dim 384→1536 | search↑ | ≈ local | ? | ≈ | ×4 vectors |
| top_k 5→20 | LLM↑ | ↑ | recall↑? | ≈ | ≈ |
| Flat→HNSW | search↓ | ≈ | recall≤1 | ↑ tune | ↑ graphs |

## Appendix C — Good/bad/ideal cheat sheet

| Metric | Bad | Acceptable demo | Strong prod target (example) |
|---|---|---|---|
| Ask P95 | >15s | <5s | <2s excl. LLM or budgeted |
| Recall@5 | <0.3 | >0.5 | >0.8 on golden set |
| Hit@5 | <0.5 | >0.7 | >0.9 |
| Groundedness | frequent invent | mostly cited | measured ≥ threshold |
| Monthly LLM $ | unknown | tracked | capped + alerted |

