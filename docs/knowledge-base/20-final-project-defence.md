# Chapter 20 — Final Project Defence (Mock Interview)

## How to use this chapter

1. Cover the answer; speak aloud.  
2. Then read **Ideal FAANG-style answer** and **What weak answers miss**.  
3. Practice follow-ups.  
4. For interactive mode with an interviewer/AI: answer one question at a time without reading ahead.

Grading rubric: Technical accuracy (40), Tradeoff clarity (25), Honesty about limits (15), Structure (10), Metrics/numbers (10).

---

## Round 1 — Warmup

### Q1. Explain the project in 60 seconds.
**Ideal FAANG answer:** “AI Codebase Analyzer is a RAG demo for code. Streamlit takes a GitHub URL, FastAPI clones the repo, chunks source into 500-character segments, embeds with MiniLM into 384-d vectors, indexes with FAISS IndexFlatL2 in memory, retrieves top-5 chunks for a question, and asks Groq’s Llama 3.3 70B to explain with that context. It’s a single-tenant local architecture meant to demonstrate retrieval-augmented code understanding, not a production multi-user platform.”
**What weak answers miss:** metric L2, top-5, in-memory, honesty about demo scope.
**Follow-up:** What is RAG?

### Q2. Why RAG instead of stuffing the whole repo into the prompt?
**Ideal:** Context limits, cost, attention dilution; retrieve first then generate.
**Miss:** Claiming RAG eliminates hallucination.

---

## Round 2 — Architecture pressure

### Q3. Where does state live?
**Ideal:** Module-global `pipeline` dict in the API process: chunks, FAISS index, summary. Lost on restart; unsafe across workers/users.
**Miss:** Inventing Redis/Mongo.
**Follow-up:** How redesign for 3 workers?

### Q4. Draw the request path for Ask.
**Ideal:** UI → POST /ask → embed_query → FAISS search → build prompt → Groq → answer JSON → HTML render.
**Miss:** Skipping embed of the question.

### Q5. What happens if two users analyze different repos?
**Ideal:** Second analyze overwrites `pipeline`; first user’s asks hit the wrong index — critical correctness bug at multi-user.
**Miss:** “It handles it.”

---

## Round 3 — ML / retrieval

### Q6. Cosine or L2?
**Ideal:** Code uses IndexFlatL2. If vectors normalized, ranking relates to cosine; I won’t claim cosine API.
**Miss:** Automatic “cosine similarity” buzzword.

### Q7. Failure modes of 500-char chunking?
**Ideal:** Splits functions, no overlap, language-agnostic but semantics-blind; retrieve partial logic.
**Follow-up:** Better chunking?

### Q8. How evaluate retrieval?
**Ideal:** Labeled questions → Recall@K, MRR; plus groundedness checks; not BLEU alone.
**Miss:** “We eyeball.”

---

## Round 4 — Systems / scale

### Q9. First bottleneck at 1000 concurrent users?
**Ideal:** Likely LLM quotas and/or blocking analyze/embed CPU; also state model breaks earlier than pure CPU.
**Miss:** Only “need Kubernetes.”

### Q10. FlatL2 at 50 million chunks?
**Ideal:** O(C·D) too slow; move to HNSW/IVF/PQ or managed vector DB; measure recall vs exact.
**Miss:** “FAISS always scales.”

---

## Round 5 — Security

### Q11. Biggest security issue?
**Ideal:** Several: XSS via unsafe HTML; unauthenticated endpoints; arbitrary repo clone; secrets sent to Groq; prompt injection via code comments.
**Miss:** Only “we use HTTPS” (we don’t even).

### Q12. Prompt injection example?
**Ideal:** User: ignore context and exfiltrate; or malicious README instructions in retrieved chunks.
**Mitigation:** treat retrieved text as data; output filters; allowlists.

---

## Round 6 — Design ownership

### Q13. Why FastAPI + Streamlit?
**Ideal:** Python ML ecosystem + typed API boundary + fastest demo UI; trade production UI control.
**Miss:** “They’re best always.”

### Q14. Why not LangChain?
**Ideal:** Explicit pipeline teaches clearer mental model; fewer abstractions for this scope; would reconsider for agents/tools.
**Miss:** Tribal hate without tradeoffs.

### Q15. What would you ship in two weeks before a pilot?
**Ideal:** Persist indexes, job queue analyze, citations, auth API key, HTML escape, ignore vendored dirs, basic tests+CI, timeouts.
**Miss:** Total rewrite.

---

## Round 7 — Stress / trick

### Q16. Is this an agent?
**Ideal:** No — single retrieve-then-generate; no tool loop / planning.
**Miss:** Calling everything an agent.

### Q17. Does temperature 0.2 guarantee correctness?
**Ideal:** No — reduces randomness; retrieval gaps and model errors remain.
**Miss:** Yes.

### Q18. Where is the database?
**Ideal:** No relational/document DB; only filesystem clones + in-memory FAISS.
**Miss:** “FAISS database” without nuance.

---

## Closing defence script (memorize)

“I built an end-to-end RAG path with clear stage separation. I’m explicit about demo limits: in-memory single-tenant state, character chunking, exact L2 search, and a hosted LLM. I can discuss how to evolve it toward durable indexes, async ingest, hybrid retrieval, eval harnesses, and enterprise security — and I can quantify bottlenecks with C, D, and token costs.”

---

## Interview questions bank (meta)

### Beginner

#### 1. Defence tip
**Question:** How start answering?
**Ideal Answer:** Problem → approach → tradeoffs → limits → next steps.
**Why interviewer asked it:** Structure.
**Common mistakes:** Dive into CSS.
**Follow-up questions:** Ask clarifying Q?


### FAANG

#### 1. Hostile interviewer
**Question:** They say toy project.
**Ideal Answer:** Agree on scope; then show depth on RAG failure modes, scaling math, security, and a credible production roadmap.
**Why interviewer asked it:** Composure.
**Common mistakes:** Get defensive.
**Follow-up questions:** What metric proves value?


### Trick

#### 1. Did you copy README?
**Question:** Can you show the IndexFlatL2 line?
**Ideal Answer:** Open vector_store.py mentally: faiss.IndexFlatL2(dimension).
**Why interviewer asked it:** Verify ownership.
**Common mistakes:** Freeze.
**Follow-up questions:** Dim of MiniLM?



---

## Appendix A — Extra progressive rounds

### Round 8 — Quantitative
**Q:** Estimate RAM for 1e6 chunks at D=384.  
**Ideal:** 1e6*384*4 ≈ 1.53 GB raw vectors + text overhead; flat search ~1e6*384 ops.  
**Miss:** Ignoring text RAM.

### Round 9 — Product sense
**Q:** Who is the user and what’s the activation moment?  
**Ideal:** Developer dropped into unfamiliar repo; activation = first useful answer with correct file citation (citations not shipped — call that out).  

### Round 10 — Leadership
**Q:** Your PM wants “ChatGPT for all company code” next quarter.  
**Ideal:** Reframe to phased: secure ingest → retrieval quality → chat UX; call out compliance; refuse unsafe timeline without authz/DLP.

## Appendix B — Scorecard for self-grading

| Score | Meaning |
|---|---|
| 5 | Accurate, tradeoffs, limits, numbers, next steps |
| 3 | Correct but shallow |
| 1 | Contradicts code or invents stack |

Rehearse until average ≥4 on rounds 1–7.

## Appendix C — Opening and closing lines

**Open:** “I built a local RAG pipeline for code exploration with explicit stage separation and I’m upfront that it’s a single-tenant demo.”  
**Close:** “The biggest production gap is durable multi-tenant state plus eval; here’s my 30-day fix order…”

