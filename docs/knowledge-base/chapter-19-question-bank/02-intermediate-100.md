# AI Codebase Analyzer: 100 Intermediate Interview Questions

Project-specific questions based on the current implementation. Recommendations are explicitly labeled so they are not confused with existing behavior.

## Topics

- [State and Concurrency (1–20)](#state-and-concurrency-120)
- [Retrieval and Chunking (21–40)](#retrieval-and-chunking-2140)
- [API and Frontend (41–60)](#api-and-frontend-4160)
- [ML Systems Thinking (61–80)](#ml-systems-thinking-6180)
- [Production Gaps (81–100)](#production-gaps-81100)

## State and Concurrency (1–20)

### 1. Intermediate 1: Pipeline state race
- **Question:** What race exists between /analyze and /ask?
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 2. Intermediate 2: Stale clones
- **Question:** Why can answers be stale after GitHub updates?
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 3. Intermediate 3: Why not async def
- **Question:** Would making analyze async def fix blocking?
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 4. Intermediate 4: top_k tradeoff
- **Question:** Tradeoffs of top_k=5?
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 5. Intermediate 5: Basename collision
- **Question:** Bug in architecture graph keys?
- **Ideal Answer:** Uses file basename so duplicate names collide.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 6. Intermediate 6: Normalization
- **Question:** If MiniLM normalizes, why still say L2?
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 7. Intermediate 7: Empty supported files
- **Question:** What if repo has no supported extensions?
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 8. Intermediate 8: Prompt structure
- **Question:** How does the prompt reduce hallucination?
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 9. Intermediate 9: Streamlit rerun
- **Question:** Why might analyze run twice?
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 10. Intermediate 10: node_modules
- **Question:** Why can analyze explode on JS repos?
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

### 11. Intermediate 11: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 12. Intermediate 12: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 13. Intermediate 13: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 14. Intermediate 14: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 15. Intermediate 15: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 16. Intermediate 16: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 17. Intermediate 17: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 18. Intermediate 18: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 19. Intermediate 19: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 20. Intermediate 20: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

## Retrieval and Chunking (21–40)

### 21. Intermediate 21: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 22. Intermediate 22: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 23. Intermediate 23: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 24. Intermediate 24: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 25. Intermediate 25: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 26. Intermediate 26: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 27. Intermediate 27: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 28. Intermediate 28: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 29. Intermediate 29: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 30. Intermediate 30: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

### 31. Intermediate 31: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 32. Intermediate 32: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 33. Intermediate 33: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 34. Intermediate 34: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 35. Intermediate 35: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 36. Intermediate 36: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 37. Intermediate 37: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 38. Intermediate 38: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 39. Intermediate 39: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 40. Intermediate 40: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

## API and Frontend (41–60)

### 41. Intermediate 41: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 42. Intermediate 42: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 43. Intermediate 43: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 44. Intermediate 44: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 45. Intermediate 45: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 46. Intermediate 46: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 47. Intermediate 47: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 48. Intermediate 48: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 49. Intermediate 49: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 50. Intermediate 50: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

### 51. Intermediate 51: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 52. Intermediate 52: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 53. Intermediate 53: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 54. Intermediate 54: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 55. Intermediate 55: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 56. Intermediate 56: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 57. Intermediate 57: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 58. Intermediate 58: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 59. Intermediate 59: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 60. Intermediate 60: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

## ML Systems Thinking (61–80)

### 61. Intermediate 61: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 62. Intermediate 62: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 63. Intermediate 63: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 64. Intermediate 64: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 65. Intermediate 65: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 66. Intermediate 66: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 67. Intermediate 67: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 68. Intermediate 68: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 69. Intermediate 69: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 70. Intermediate 70: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

### 71. Intermediate 71: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 72. Intermediate 72: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 73. Intermediate 73: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 74. Intermediate 74: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 75. Intermediate 75: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 76. Intermediate 76: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 77. Intermediate 77: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 78. Intermediate 78: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 79. Intermediate 79: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 80. Intermediate 80: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

## Production Gaps (81–100)

### 81. Intermediate 81: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 82. Intermediate 82: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 83. Intermediate 83: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 84. Intermediate 84: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 85. Intermediate 85: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 86. Intermediate 86: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 87. Intermediate 87: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 88. Intermediate 88: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 89. Intermediate 89: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 90. Intermediate 90: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.

### 91. Intermediate 91: Pipeline state race (scalability)
- **Question:** What race exists between /analyze and /ask? Also discuss scalability implications.
- **Ideal Answer:** Concurrent analyze can mutate module-global pipeline dict with chunks/index/summary while ask reads, causing inconsistent retrieval or KeyError. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How would you lock or version indexes?
- **Common Mistake:** Saying Python GIL makes it safe.
- **How to Impress Interviewer:** Mention atomic swap of an immutable snapshot object.

### 92. Intermediate 92: Stale clones (latency)
- **Question:** Why can answers be stale after GitHub updates? Also discuss latency implications.
- **Ideal Answer:** repo_loader returns existing data/<name> without git pull. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When is that desirable?
- **Common Mistake:** Always fresh clone.
- **How to Impress Interviewer:** Propose cloning by commit SHA.

### 93. Intermediate 93: Why not async def (cost)
- **Question:** Would making analyze async def fix blocking? Also discuss cost implications.
- **Ideal Answer:** Not by itself; clone/embed still CPU/IO blocking unless offloaded to threads/processes/queue. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** run_in_threadpool vs Celery?
- **Common Mistake:** async always faster.
- **How to Impress Interviewer:** Separate ingest workers.

### 94. Intermediate 94: top_k tradeoff (security)
- **Question:** Tradeoffs of top_k=5? Also discuss security implications.
- **Ideal Answer:** Balances context vs noise/token cost; distances unused so irrelevant chunks still included. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How choose k with eval?
- **Common Mistake:** Higher k always better.
- **How to Impress Interviewer:** Cite Recall@K vs latency curve.

### 95. Intermediate 95: Basename collision (testing)
- **Question:** Bug in architecture graph keys? Also discuss testing implications.
- **Ideal Answer:** Uses file basename so duplicate names collide. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How fix?
- **Common Mistake:** Deny it.
- **How to Impress Interviewer:** Use repo-relative paths.

### 96. Intermediate 96: Normalization (ops)
- **Question:** If MiniLM normalizes, why still say L2? Also discuss ops implications.
- **Ideal Answer:** Because code constructs IndexFlatL2; ranking may correlate with cosine but API/metric is L2. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Show IndexFlatIP alternative.
- **Common Mistake:** We use cosine.
- **How to Impress Interviewer:** Discuss equivalence under unit norm.

### 97. Intermediate 97: Empty supported files (UX)
- **Question:** What if repo has no supported extensions? Also discuss UX implications.
- **Ideal Answer:** chunks empty; build_index hits embeddings[0] failure path. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** How handle UX?
- **Common Mistake:** Silently succeeds.
- **How to Impress Interviewer:** Validate and return 400.

### 98. Intermediate 98: Prompt structure (data model)
- **Question:** How does the prompt reduce hallucination? Also discuss data model implications.
- **Ideal Answer:** Injects retrieved file paths and chunks and asks which module handles functionality; temperature 0.2. Still not a guarantee. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What else?
- **Common Mistake:** Prompt fully solves it.
- **How to Impress Interviewer:** Require citations + refuse if insufficient context.

### 99. Intermediate 99: Streamlit rerun (API design)
- **Question:** Why might analyze run twice? Also discuss API design implications.
- **Ideal Answer:** Streamlit rerun model + button state; careful with side effects. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** session_state patterns?
- **Common Mistake:** Never happens.
- **How to Impress Interviewer:** Idempotent jobs by repo SHA.

### 100. Intermediate 100: node_modules (failure mode)
- **Question:** Why can analyze explode on JS repos? Also discuss failure mode implications.
- **Ideal Answer:** code_parser does not ignore node_modules; can create huge chunk sets. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Ignore list design?
- **Common Mistake:** Only Python matters so fine.
- **How to Impress Interviewer:** Default deny vendor dirs.
