# AI Codebase Analyzer: 100 Architecture Questions

Project-specific questions based on the current implementation. Recommendations are explicitly labeled so they are not confused with existing behavior.

## Topics

- [Structural Views (1–25)](#structural-views-125)
- [Quality Attributes (26–50)](#quality-attributes-2650)
- [Evolution (51–75)](#evolution-5175)
- [Tradeoff Drills (76–100)](#tradeoff-drills-76100)

## Structural Views (1–25)

### 1. Architecture 1: C4 context
- **Question:** C4 context elements?
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 2. Architecture 2: Modular monolith
- **Question:** Is this microservices?
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 3. Architecture 3: SRP modules
- **Question:** Example SRP?
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 4. Architecture 4: Stateful service smell
- **Question:** Why global pipeline smell?
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 5. Architecture 5: Sync coupling
- **Question:** UI-API coupling?
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

### 6. Architecture 6: Failure domain
- **Question:** If Groq down?
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 7. Architecture 7: Data flow vs control
- **Question:** Difference in your system?
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 8. Architecture 8: Idempotency
- **Question:** Is analyze idempotent?
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 9. Architecture 9: Backpressure
- **Question:** Where needed?
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 10. Architecture 10: Evolution
- **Question:** Strangler path to prod?
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

### 11. Architecture 11: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 12. Architecture 12: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 13. Architecture 13: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 14. Architecture 14: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 15. Architecture 15: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

### 16. Architecture 16: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 17. Architecture 17: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 18. Architecture 18: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 19. Architecture 19: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 20. Architecture 20: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

### 21. Architecture 21: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 22. Architecture 22: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 23. Architecture 23: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 24. Architecture 24: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 25. Architecture 25: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

## Quality Attributes (26–50)

### 26. Architecture 26: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 27. Architecture 27: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 28. Architecture 28: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 29. Architecture 29: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 30. Architecture 30: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

### 31. Architecture 31: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 32. Architecture 32: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 33. Architecture 33: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 34. Architecture 34: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 35. Architecture 35: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

### 36. Architecture 36: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 37. Architecture 37: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 38. Architecture 38: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 39. Architecture 39: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 40. Architecture 40: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

### 41. Architecture 41: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 42. Architecture 42: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 43. Architecture 43: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 44. Architecture 44: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 45. Architecture 45: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

### 46. Architecture 46: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 47. Architecture 47: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 48. Architecture 48: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 49. Architecture 49: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 50. Architecture 50: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

## Evolution (51–75)

### 51. Architecture 51: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 52. Architecture 52: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 53. Architecture 53: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 54. Architecture 54: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 55. Architecture 55: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

### 56. Architecture 56: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 57. Architecture 57: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 58. Architecture 58: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 59. Architecture 59: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 60. Architecture 60: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

### 61. Architecture 61: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 62. Architecture 62: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 63. Architecture 63: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 64. Architecture 64: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 65. Architecture 65: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

### 66. Architecture 66: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 67. Architecture 67: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 68. Architecture 68: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 69. Architecture 69: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 70. Architecture 70: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

### 71. Architecture 71: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 72. Architecture 72: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 73. Architecture 73: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 74. Architecture 74: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 75. Architecture 75: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

## Tradeoff Drills (76–100)

### 76. Architecture 76: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 77. Architecture 77: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 78. Architecture 78: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 79. Architecture 79: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 80. Architecture 80: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

### 81. Architecture 81: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 82. Architecture 82: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 83. Architecture 83: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 84. Architecture 84: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 85. Architecture 85: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

### 86. Architecture 86: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 87. Architecture 87: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 88. Architecture 88: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 89. Architecture 89: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 90. Architecture 90: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.

### 91. Architecture 91: C4 context (scalability)
- **Question:** C4 context elements? Also discuss scalability implications.
- **Ideal Answer:** User, Streamlit UI, FastAPI app, Git hosts, Groq, local disk; no DB. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Trust boundaries?
- **Common Mistake:** Include Kafka.
- **How to Impress Interviewer:** Draw live.

### 92. Architecture 92: Modular monolith (latency)
- **Question:** Is this microservices? Also discuss latency implications.
- **Ideal Answer:** No — modular monolith with UI/API processes; stages are modules. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When split?
- **Common Mistake:** Already microservices.
- **How to Impress Interviewer:** Split axes.

### 93. Architecture 93: SRP modules (cost)
- **Question:** Example SRP? Also discuss cost implications.
- **Ideal Answer:** chunker only splits; embedder only encodes — good separation. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Where violated?
- **Common Mistake:** Everything perfect.
- **How to Impress Interviewer:** Frontend graph duplication.

### 94. Architecture 94: Stateful service smell (security)
- **Question:** Why global pipeline smell? Also discuss security implications.
- **Ideal Answer:** module-global pipeline dict with chunks/index/summary couples HTTP tier to memory durability and single tenancy. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Hexagonal fix?
- **Common Mistake:** Fine at FAANG scale.
- **How to Impress Interviewer:** Repository pattern.

### 95. Architecture 95: Sync coupling (testing)
- **Question:** UI-API coupling? Also discuss testing implications.
- **Ideal Answer:** Hardcoded localhost URL; no OpenAPI client gen; graph duplicated. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** BFF?
- **Common Mistake:** Loose enough.
- **How to Impress Interviewer:** Contract tests.

### 96. Architecture 96: Failure domain (ops)
- **Question:** If Groq down? Also discuss ops implications.
- **Ideal Answer:** Ask fails entirely; analyze still works; no degraded mode. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Design degrade?
- **Common Mistake:** Whole app must die.
- **How to Impress Interviewer:** Bulkheads.

### 97. Architecture 97: Data flow vs control (UX)
- **Question:** Difference in your system? Also discuss UX implications.
- **Ideal Answer:** Control: HTTP route orchestration; data: text→chunks→vectors→prompt→answer. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DFD level 0?
- **Common Mistake:** Same thing.
- **How to Impress Interviewer:** Draw both.

### 98. Architecture 98: Idempotency (data model)
- **Question:** Is analyze idempotent? Also discuss data model implications.
- **Ideal Answer:** Partially — existing clone skips git; but re-embed overwrites pipeline; not SHA-aware. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Make idempotent?
- **Common Mistake:** POST always idempotent.
- **How to Impress Interviewer:** Idempotency-Key.

### 99. Architecture 99: Backpressure (API design)
- **Question:** Where needed? Also discuss API design implications.
- **Ideal Answer:** Analyze queue length; Groq rate; disk usage for clones. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Load shed?
- **Common Mistake:** Unlimited.
- **How to Impress Interviewer:** 429 + Retry-After.

### 100. Architecture 100: Evolution (failure mode)
- **Question:** Strangler path to prod? Also discuss failure mode implications.
- **Ideal Answer:** Keep API; extract ingest worker; add Postgres metadata; swap FAISS memory for durable store; replace Streamlit later. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Compatibility?
- **Common Mistake:** Big bang rewrite.
- **How to Impress Interviewer:** Incremental flags.
