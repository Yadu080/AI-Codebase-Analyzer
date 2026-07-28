# AI Codebase Analyzer: 100 System Design Questions

Project-specific questions based on the current implementation. Recommendations are explicitly labeled so they are not confused with existing behavior.

## Topics

- [Ingest Path (1–25)](#ingest-path-125)
- [Query Path (26–50)](#query-path-2650)
- [Storage and State (51–75)](#storage-and-state-5175)
- [Scale and Reliability (76–100)](#scale-and-reliability-76100)

## Ingest Path (1–25)

### 1. SystemDesign 1: Multi-tenant indexes
- **Question:** Design multi-tenant storage for indexes.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 2. SystemDesign 2: Async ingest
- **Question:** Design analyze for large monorepos.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 3. SystemDesign 3: Hybrid search
- **Question:** When add BM25?
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 4. SystemDesign 4: Citations
- **Question:** Design citation UX.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 5. SystemDesign 5: SLO
- **Question:** Propose SLOs for ask.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

### 6. SystemDesign 6: Cache
- **Question:** Where put Redis?
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 7. SystemDesign 7: K8s when
- **Question:** When introduce Kubernetes?
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 8. SystemDesign 8: Embedding versioning
- **Question:** How version embeddings?
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 9. SystemDesign 9: Fanout
- **Question:** 100k repos design?
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 10. SystemDesign 10: Failure domains
- **Question:** Isolate LLM outages.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

### 11. SystemDesign 11: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 12. SystemDesign 12: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 13. SystemDesign 13: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 14. SystemDesign 14: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 15. SystemDesign 15: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

### 16. SystemDesign 16: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 17. SystemDesign 17: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 18. SystemDesign 18: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 19. SystemDesign 19: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 20. SystemDesign 20: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

### 21. SystemDesign 21: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 22. SystemDesign 22: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 23. SystemDesign 23: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 24. SystemDesign 24: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 25. SystemDesign 25: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

## Query Path (26–50)

### 26. SystemDesign 26: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 27. SystemDesign 27: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 28. SystemDesign 28: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 29. SystemDesign 29: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 30. SystemDesign 30: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

### 31. SystemDesign 31: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 32. SystemDesign 32: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 33. SystemDesign 33: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 34. SystemDesign 34: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 35. SystemDesign 35: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

### 36. SystemDesign 36: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 37. SystemDesign 37: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 38. SystemDesign 38: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 39. SystemDesign 39: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 40. SystemDesign 40: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

### 41. SystemDesign 41: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 42. SystemDesign 42: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 43. SystemDesign 43: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 44. SystemDesign 44: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 45. SystemDesign 45: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

### 46. SystemDesign 46: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 47. SystemDesign 47: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 48. SystemDesign 48: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 49. SystemDesign 49: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 50. SystemDesign 50: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

## Storage and State (51–75)

### 51. SystemDesign 51: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 52. SystemDesign 52: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 53. SystemDesign 53: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 54. SystemDesign 54: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 55. SystemDesign 55: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

### 56. SystemDesign 56: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 57. SystemDesign 57: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 58. SystemDesign 58: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 59. SystemDesign 59: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 60. SystemDesign 60: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

### 61. SystemDesign 61: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 62. SystemDesign 62: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 63. SystemDesign 63: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 64. SystemDesign 64: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 65. SystemDesign 65: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

### 66. SystemDesign 66: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 67. SystemDesign 67: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 68. SystemDesign 68: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 69. SystemDesign 69: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 70. SystemDesign 70: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

### 71. SystemDesign 71: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 72. SystemDesign 72: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 73. SystemDesign 73: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 74. SystemDesign 74: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 75. SystemDesign 75: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

## Scale and Reliability (76–100)

### 76. SystemDesign 76: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 77. SystemDesign 77: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 78. SystemDesign 78: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 79. SystemDesign 79: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 80. SystemDesign 80: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

### 81. SystemDesign 81: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 82. SystemDesign 82: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 83. SystemDesign 83: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 84. SystemDesign 84: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 85. SystemDesign 85: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

### 86. SystemDesign 86: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 87. SystemDesign 87: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 88. SystemDesign 88: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 89. SystemDesign 89: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 90. SystemDesign 90: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.

### 91. SystemDesign 91: Multi-tenant indexes (scalability)
- **Question:** Design multi-tenant storage for indexes. Also discuss scalability implications.
- **Ideal Answer:** Replace module-global pipeline dict with chunks/index/summary with object storage + metadata DB keyed by tenant_id/repo_sha; workers load or query remote ANN; authz on every ask. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cold start per tenant?
- **Common Mistake:** One global FAISS.
- **How to Impress Interviewer:** Discuss isolation + noisy neighbor.

### 92. SystemDesign 92: Async ingest (latency)
- **Question:** Design analyze for large monorepos. Also discuss latency implications.
- **Ideal Answer:** 202+job queue; shallow clone; ignore rules; incremental embed; progress events; deadline + budget. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Exactly-once?
- **Common Mistake:** Sync HTTP only.
- **How to Impress Interviewer:** Idempotency keys.

### 93. SystemDesign 93: Hybrid search (cost)
- **Question:** When add BM25? Also discuss cost implications.
- **Ideal Answer:** When exact identifiers/error strings matter; fuse with dense via RRF; evaluate. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Weights?
- **Common Mistake:** Dense always enough.
- **How to Impress Interviewer:** Show failure cases of dense-only.

### 94. SystemDesign 94: Citations (security)
- **Question:** Design citation UX. Also discuss security implications.
- **Ideal Answer:** Retriever returns path+span; LLM must quote; UI links; backend verifies spans subset of chunks. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hallucinated lines?
- **Common Mistake:** Trust model.
- **How to Impress Interviewer:** Constrained decoding / post-check.

### 95. SystemDesign 95: SLO (testing)
- **Question:** Propose SLOs for ask. Also discuss testing implications.
- **Ideal Answer:** e.g., availability 99.9%; P95 retrieve+embed <300ms; end-to-end depends on LLM budget; quality via groundedness. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Error budget?
- **Common Mistake:** No numbers.
- **How to Impress Interviewer:** Separate LLM SLO.

### 96. SystemDesign 96: Cache (ops)
- **Question:** Where put Redis? Also discuss ops implications.
- **Ideal Answer:** Cache embeddings by content hash; cache answers by repo_sha+question hash; rate limit counters — not present today. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Invalidation?
- **Common Mistake:** Cache forever.
- **How to Impress Interviewer:** TTL + version keys.

### 97. SystemDesign 97: K8s when (UX)
- **Question:** When introduce Kubernetes? Also discuss UX implications.
- **Ideal Answer:** Multiple services, GPU pools, complex autoscaling, multi-env — not for first cloud deploy of this demo. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cloud Run first?
- **Common Mistake:** K8s day one.
- **How to Impress Interviewer:** Operational cost honesty.

### 98. SystemDesign 98: Embedding versioning (data model)
- **Question:** How version embeddings? Also discuss data model implications.
- **Ideal Answer:** Index metadata includes model name/dim; never mix vectors from different models in one flat index. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Migration?
- **Common Mistake:** Just change model.
- **How to Impress Interviewer:** Dual-write reembed job.

### 99. SystemDesign 99: Fanout (API design)
- **Question:** 100k repos design? Also discuss API design implications.
- **Ideal Answer:** Shard metadata; per-repo ANN; shared embed fleet; tenancy quotas; lifecycle GC. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Cross-repo search?
- **Common Mistake:** One giant index.
- **How to Impress Interviewer:** ACL filtered search.

### 100. SystemDesign 100: Failure domains (failure mode)
- **Question:** Isolate LLM outages. Also discuss failure mode implications.
- **Ideal Answer:** LLM gateway with circuit breaker; cached answers; degraded mode retrieve-only; status page. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fallback model?
- **Common Mistake:** Crash hard.
- **How to Impress Interviewer:** Bulkhead patterns.
