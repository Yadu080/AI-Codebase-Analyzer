# Chapter 14 — Scalability

## 0. WHY scalability is a design conversation

Scalability means the system keeps meeting **latency, cost, and correctness goals** as load (users, repos, chunks, QPS) grows. This demo is optimized for **1 user on a laptop**, not 100k users.

Bottlenecks today:
1. Synchronous `/analyze` (clone+embed in request)
2. Global single-repo `pipeline`
3. CPU embedding
4. `IndexFlatL2` O(C·D) search
5. Groq rate limits / cost
6. Two single processes (Uvicorn + Streamlit)
7. Disk clones without quotas

---

## 1. Scale ladder

### 1 user
**Works** as designed. Risks: cold start, missing API key, large repo.

Architecture: monolith processes, in-memory FAISS.

### 100 users (same repo, sequential asks)
Likely OK if analyze done once. Concurrent asks compete for CPU embed + Groq.

Changes: timeouts, basic rate limit, persist index to disk to survive restart.

### 1,000 users
Global `pipeline` becomes unacceptable (cross-talk). Need:
- `repo_id` in requests
- per-repo indexes on disk/object storage
- analyze via **job queue** (Celery/RQ/Cloud Tasks)
- horizontal API workers **without** local-only state
- connection pooling; LLM gateway

Microservices? **Not mandatory yet** — modular monolith + queue may suffice.

### 10,000 users
Need:
- Autoscale workers for embed
- ANN index (HNSW) or managed vector DB
- CDN for static UI (if React)
- Caching frequent questions (Redis)
- Shard by tenant
- Observability (metrics, tracing)
- Possibly Kubernetes for bin-packing GPUs/CPUs

Kubernetes becomes attractive when: many services, autoscaling policies, multi-env, GPU pools.

### 100,000 users
- Multi-region
- Strong multi-tenant isolation
- Quotas/billing
- Async everything for ingest
- Approximate search + rerankers
- Dedicated LLM capacity / batching
- Chaos testing, SLOs, on-call
- Microservices usually justified by team ownership + scale axes (ingest vs query vs LLM)

CDN required when: global static assets / edge caching of public docs — less critical for private code QA API itself (APIs need edge auth carefully).

---

## 2. Horizontal vs vertical scaling

| | Vertical | Horizontal |
|---|---|---|
| What | Bigger VM | More machines |
| Helps here | Faster embed CPU/RAM | More concurrent asks **if state shared** |
| Fails when | Single machine limits; still one global pipeline | Workers with isolated memory without shared index |

---

## 3. Stateless vs stateful

API handlers should be **stateless**; indexes/metadata **stateful stores**.

Today: **stateful API process** — anti-pattern at scale.

---

## 4. Caching opportunities

| Cache | Key | Value | Win |
|---|---|---|---|
| Embed cache | hash(chunk)+model | vector | Re-analyze speed |
| Query cache | hash(question)+repo_version | answer | Repeat FAQs |
| HTTP CDN | static UI | assets | UI load |
| Clone cache | repo@sha | disk path | Ingest |

Redis: shared cache across workers — **not present now**.

---

## 5. Queues & async

```
POST /analyze → enqueue job → 202 job_id
worker: clone → chunk → embed → write index
POST /ask → read index by repo_id
```

WHY: HTTP timeouts; UX progress; retries; backpressure.

---

## 6. Capacity math sketches

Assume D=384, C=100,000 chunks:
- Vector RAM ≈ 153MB + text
- Flat search: 100k*384 ≈ 38M FLOPs/query — fine on CPU
- At C=50e6, flat search too slow → ANN

Assume `/ask` needs 1s Groq: one key limited to RPS by provider → need multi-key/enterprise tier or self-host.

---

## 7. When microservices become necessary

Not at line count — at **independent scaling/failure/team boundaries**:
- Ingest spikes vs query spikes
- GPU embed vs light API
- Different SLOs

---

## Interview questions

### Beginner

#### 1. Scale today
**Question:** How many users can you support?
**Ideal Answer:** Comfortably one local user; concurrent users fight over one in-memory index and CPU.
**Why interviewer asked it:** Honesty.
**Common mistakes:** Millions.
**Follow-up questions:** First bottleneck?

#### 2. Horizontal issue
**Question:** Why can't you just run 10 Uvicorn workers?
**Ideal Answer:** Each has separate pipeline memory; asks may miss indexes.
**Why interviewer asked it:** State.
**Common mistakes:** It just works.
**Follow-up questions:** Fix?


### Intermediate

#### 1. Queue
**Question:** Why queue analyze?
**Ideal Answer:** Long CPU/IO exceeds HTTP comfort; enables retries and scaling workers.
**Why interviewer asked it:** Async design.
**Common mistakes:** Threads enough always.
**Follow-up questions:** Idempotency?

#### 2. 1000 users
**Question:** Architecture changes?
**Ideal Answer:** Per-repo durable indexes, auth, rate limits, job queue, shared storage, no global dict.
**Why interviewer asked it:** Concrete plan.
**Common mistakes:** Only add Redis.
**Follow-up questions:** Data model?


### Advanced

#### 1. Search scale
**Question:** When is IndexFlatL2 the bottleneck?
**Ideal Answer:** When C·D/time exceeds latency SLO; measure; then ANN/sharding.
**Why interviewer asked it:** Perf diagnosis.
**Common mistakes:** Always at 1k chunks.
**Follow-up questions:** How validate recall?


### FAANG

#### 1. 100k design
**Question:** Design for 100k DAU code assistants.
**Ideal Answer:** Multi-tenant vector platform, async ingest, feature stores for embeddings, LLM gateway, eval + canary, regional failover, cost controls.
**Why interviewer asked it:** Senior SD.
**Common mistakes:** Buzzword salad.
**Follow-up questions:** Cost per query?


### Trick

#### 1. Streamlit scale
**Question:** Scale Streamlit to 100k?
**Ideal Answer:** Poor fit as sole frontend tier; use proper web app + API; Streamlit for internal tools.
**Why interviewer asked it:** FE scale.
**Common mistakes:** Streamlit Cloud magic.
**Follow-up questions:** What breaks first?



---

## Appendix A — Scaling decision tree

```
Need more concurrent asks?
  ├─ LLM bound → gateway + cache + larger quota / batch
  ├─ Embed bound → embed service + GPU/CPU autoscaling
  ├─ Search bound → ANN / shard indexes
  └─ State bugs → durable per-repo indexes BEFORE horizontal scale

Need faster analyze?
  ├─ Queue + workers
  ├─ Incremental embed
  ├─ Ignore vendor dirs
  └─ Shallow clone
```

## Appendix B — Microservices split plan

| Service | Scale trigger | State |
|---|---|---|
| API/BFF | RPS | Stateless |
| Ingest worker | Queue depth | Ephemeral disk |
| Embed service | Batch latency | Model weights |
| Search service | QPS | Indexes |
| LLM gateway | Token budget | Config |
| UI | Sessions | Stateless |

## Appendix C — Numbers to recite

- Vector bytes ≈ `C * D * 4`
- Flat query work ≈ `C * D`
- Ask latency ≈ `t_embed + t_search + t_llm` with `t_llm` usually largest
- Workers without shared store ⇒ incorrect answers (not just slow)

