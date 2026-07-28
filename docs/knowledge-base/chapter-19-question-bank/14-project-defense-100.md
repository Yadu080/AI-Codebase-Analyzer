# AI Codebase Analyzer: 100 Project Defense Questions

Project-specific questions based on the current implementation. Recommendations are explicitly labeled so they are not confused with existing behavior.

## Topics

- [Justify Decisions (1–25)](#justify-decisions-125)
- [Attack Your Design (26–50)](#attack-your-design-2650)
- [Roadmap Defense (51–75)](#roadmap-defense-5175)
- [Deep Ownership Drills (76–100)](#deep-ownership-drills-76100)

## Justify Decisions (1–25)

### 1. Defense 1: Defend chunking
- **Question:** Why 500 chars not AST?
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 2. Defense 2: Defend FAISS flat
- **Question:** Why not HNSW?
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 3. Defense 3: Defend Groq
- **Question:** Why Groq not local Llama?
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 4. Defense 4: Defend Streamlit
- **Question:** Why not React?
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 5. Defense 5: Defend no DB
- **Question:** Why no Postgres?
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

### 6. Defense 6: Attack your design
- **Question:** Strongest critique?
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 7. Defense 7: Metrics missing
- **Question:** Why no eval harness?
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 8. Defense 8: Duplicate graph
- **Question:** Why UI doesn't call /architecture?
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 9. Defense 9: Bare except
- **Question:** Defend bare except in parser?
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 10. Defense 10: Production ready?
- **Question:** Is it production ready?
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

### 11. Defense 11: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 12. Defense 12: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 13. Defense 13: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 14. Defense 14: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 15. Defense 15: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

### 16. Defense 16: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 17. Defense 17: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 18. Defense 18: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 19. Defense 19: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 20. Defense 20: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

### 21. Defense 21: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 22. Defense 22: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 23. Defense 23: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 24. Defense 24: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 25. Defense 25: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

## Attack Your Design (26–50)

### 26. Defense 26: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 27. Defense 27: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 28. Defense 28: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 29. Defense 29: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 30. Defense 30: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

### 31. Defense 31: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 32. Defense 32: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 33. Defense 33: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 34. Defense 34: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 35. Defense 35: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

### 36. Defense 36: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 37. Defense 37: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 38. Defense 38: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 39. Defense 39: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 40. Defense 40: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

### 41. Defense 41: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 42. Defense 42: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 43. Defense 43: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 44. Defense 44: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 45. Defense 45: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

### 46. Defense 46: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 47. Defense 47: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 48. Defense 48: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 49. Defense 49: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 50. Defense 50: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

## Roadmap Defense (51–75)

### 51. Defense 51: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 52. Defense 52: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 53. Defense 53: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 54. Defense 54: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 55. Defense 55: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

### 56. Defense 56: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 57. Defense 57: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 58. Defense 58: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 59. Defense 59: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 60. Defense 60: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

### 61. Defense 61: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 62. Defense 62: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 63. Defense 63: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 64. Defense 64: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 65. Defense 65: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

### 66. Defense 66: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 67. Defense 67: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 68. Defense 68: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 69. Defense 69: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 70. Defense 70: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

### 71. Defense 71: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 72. Defense 72: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 73. Defense 73: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 74. Defense 74: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 75. Defense 75: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

## Deep Ownership Drills (76–100)

### 76. Defense 76: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 77. Defense 77: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 78. Defense 78: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 79. Defense 79: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 80. Defense 80: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

### 81. Defense 81: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 82. Defense 82: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 83. Defense 83: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 84. Defense 84: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 85. Defense 85: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

### 86. Defense 86: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 87. Defense 87: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 88. Defense 88: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 89. Defense 89: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 90. Defense 90: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.

### 91. Defense 91: Defend chunking (scalability)
- **Question:** Why 500 chars not AST? Also discuss scalability implications.
- **Ideal Answer:** Fast language-agnostic MVP; known quality cost; roadmap to symbol chunking labeled as improvement. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Evidence of pain?
- **Common Mistake:** 500 is optimal scientifically.
- **How to Impress Interviewer:** Show split example.

### 92. Defense 92: Defend FAISS flat (latency)
- **Question:** Why not HNSW? Also discuss latency implications.
- **Ideal Answer:** Exact search fine at demo scale; zero training complexity; upgrade when C grows. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Numbers?
- **Common Mistake:** HNSW always.
- **How to Impress Interviewer:** Complexity math.

### 93. Defense 93: Defend Groq (cost)
- **Question:** Why Groq not local Llama? Also discuss cost implications.
- **Ideal Answer:** No local GPU; fast demo latency; accept data egress tradeoff. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Airgap?
- **Common Mistake:** Groq best model.
- **How to Impress Interviewer:** Clear threat model.

### 94. Defense 94: Defend Streamlit (security)
- **Question:** Why not React? Also discuss security implications.
- **Ideal Answer:** Optimize time-to-learning-demo; API still separable for future UI. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** XSS issue?
- **Common Mistake:** Streamlit scales to millions.
- **How to Impress Interviewer:** Separation of concerns.

### 95. Defense 95: Defend no DB (testing)
- **Question:** Why no Postgres? Also discuss testing implications.
- **Ideal Answer:** State fits memory for one repo demo; adding DB without multi-user needs is premature — but I know when required. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** When add?
- **Common Mistake:** Databases useless.
- **How to Impress Interviewer:** Trigger conditions.

### 96. Defense 96: Attack your design (ops)
- **Question:** Strongest critique? Also discuss ops implications.
- **Ideal Answer:** Single global mutable pipeline is the core correctness/scalability flaw. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix plan?
- **Common Mistake:** UI CSS weak.
- **How to Impress Interviewer:** Self-review maturity.

### 97. Defense 97: Metrics missing (UX)
- **Question:** Why no eval harness? Also discuss UX implications.
- **Ideal Answer:** Timeboxed MVP; I can design Recall@K harness as next step — absence is a gap I own. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Build in a day?
- **Common Mistake:** Don't need metrics.
- **How to Impress Interviewer:** Concrete sketch.

### 98. Defense 98: Duplicate graph (data model)
- **Question:** Why UI doesn't call /architecture? Also discuss data model implications.
- **Ideal Answer:** Historical convenience; violates DRY; should unify on API. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Risks?
- **Common Mistake:** Intentional genius.
- **How to Impress Interviewer:** Refactor plan.

### 99. Defense 99: Bare except (API design)
- **Question:** Defend bare except in parser? Also discuss API design implications.
- **Ideal Answer:** I wouldn't — it's a smell; should catch UnicodeDecodeError and log. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What hides?
- **Common Mistake:** Best practice.
- **How to Impress Interviewer:** Fix live.

### 100. Defense 100: Production ready? (failure mode)
- **Question:** Is it production ready? Also discuss failure mode implications.
- **Ideal Answer:** No. Demo of RAG pipeline. Missing auth, durability, quotas, tests, obs, multi-tenant. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** What is ready?
- **Common Mistake:** Yes production.
- **How to Impress Interviewer:** Crisp boundary.
