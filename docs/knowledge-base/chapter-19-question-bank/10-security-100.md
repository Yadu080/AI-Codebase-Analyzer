# AI Codebase Analyzer: 100 Security Questions

Project-specific questions based on the current implementation. Recommendations are explicitly labeled so they are not confused with existing behavior.

## Topics

- [Web and API Security (1–25)](#web-and-api-security-125)
- [RAG Attack Surface (26–50)](#rag-attack-surface-2650)
- [Secrets and Supply Chain (51–75)](#secrets-and-supply-chain-5175)
- [Hardening Roadmap (76–100)](#hardening-roadmap-76100)

## Web and API Security (1–25)

### 1. Security 1: XSS
- **Question:** Where is XSS?
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 2. Security 2: No auth
- **Question:** Risk of exposing API?
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 3. Security 3: Prompt injection
- **Question:** Example?
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 4. Security 4: Secret leakage
- **Question:** How secrets leak?
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 5. Security 5: SSRF
- **Question:** repo_url SSRF?
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

### 6. Security 6: Supply chain
- **Question:** Dependency risk?
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 7. Security 7: Tenant escape
- **Question:** With global pipeline?
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 8. Security 8: DoS
- **Question:** Cheap DoS?
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 9. Security 9: OWASP LLM
- **Question:** Relevant LLM Top risks?
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 10. Security 10: Logging PII
- **Question:** Log prompts?
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

### 11. Security 11: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 12. Security 12: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 13. Security 13: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 14. Security 14: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 15. Security 15: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

### 16. Security 16: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 17. Security 17: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 18. Security 18: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 19. Security 19: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 20. Security 20: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

### 21. Security 21: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 22. Security 22: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 23. Security 23: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 24. Security 24: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 25. Security 25: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

## RAG Attack Surface (26–50)

### 26. Security 26: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 27. Security 27: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 28. Security 28: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 29. Security 29: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 30. Security 30: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

### 31. Security 31: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 32. Security 32: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 33. Security 33: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 34. Security 34: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 35. Security 35: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

### 36. Security 36: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 37. Security 37: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 38. Security 38: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 39. Security 39: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 40. Security 40: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

### 41. Security 41: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 42. Security 42: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 43. Security 43: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 44. Security 44: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 45. Security 45: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

### 46. Security 46: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 47. Security 47: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 48. Security 48: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 49. Security 49: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 50. Security 50: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

## Secrets and Supply Chain (51–75)

### 51. Security 51: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 52. Security 52: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 53. Security 53: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 54. Security 54: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 55. Security 55: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

### 56. Security 56: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 57. Security 57: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 58. Security 58: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 59. Security 59: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 60. Security 60: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

### 61. Security 61: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 62. Security 62: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 63. Security 63: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 64. Security 64: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 65. Security 65: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

### 66. Security 66: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 67. Security 67: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 68. Security 68: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 69. Security 69: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 70. Security 70: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

### 71. Security 71: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 72. Security 72: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 73. Security 73: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 74. Security 74: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 75. Security 75: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

## Hardening Roadmap (76–100)

### 76. Security 76: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 77. Security 77: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 78. Security 78: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 79. Security 79: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 80. Security 80: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

### 81. Security 81: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 82. Security 82: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 83. Security 83: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 84. Security 84: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 85. Security 85: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

### 86. Security 86: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 87. Security 87: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 88. Security 88: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 89. Security 89: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 90. Security 90: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.

### 91. Security 91: XSS (scalability)
- **Question:** Where is XSS? Also discuss scalability implications.
- **Ideal Answer:** frontend inserts model answer with unsafe_allow_html. For scalability: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** No XSS in Python.
- **How to Impress Interviewer:** Show escaped render.

### 92. Security 92: No auth (latency)
- **Question:** Risk of exposing API? Also discuss latency implications.
- **Ideal Answer:** Anyone can analyze/ask, burn Groq $, fill disk with clones. For latency: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** API keys design?
- **Common Mistake:** Localhost forever safe if you port-forward.
- **How to Impress Interviewer:** Threat model.

### 93. Security 93: Prompt injection (cost)
- **Question:** Example? Also discuss cost implications.
- **Ideal Answer:** Question or retrieved comment instructing model to ignore policy. For cost: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Indirect?
- **Common Mistake:** RAG prevents.
- **How to Impress Interviewer:** Data vs instructions.

### 94. Security 94: Secret leakage (security)
- **Question:** How secrets leak? Also discuss security implications.
- **Ideal Answer:** Repo secrets embedded and sent to Groq; .env committed; logs. For security: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Scanning?
- **Common Mistake:** Only key in env matters.
- **How to Impress Interviewer:** DLP pipeline.

### 95. Security 95: SSRF (testing)
- **Question:** repo_url SSRF? Also discuss testing implications.
- **Ideal Answer:** If URL parser allows internal addresses, clone/fetch could hit metadata services — allowlist GitHub. For testing: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** DNS rebinding?
- **Common Mistake:** Git clone can't SSRF.
- **How to Impress Interviewer:** Defense layers.

### 96. Security 96: Supply chain (ops)
- **Question:** Dependency risk? Also discuss ops implications.
- **Ideal Answer:** Pin versions; audit; malicious package could steal GROQ_API_KEY. For ops: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** SBOM?
- **Common Mistake:** pip install latest.
- **How to Impress Interviewer:** Lockfiles.

### 97. Security 97: Tenant escape (UX)
- **Question:** With global pipeline? Also discuss UX implications.
- **Ideal Answer:** Trivial cross-user data bleed by overwriting index. For UX: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Fix?
- **Common Mistake:** Users won't collide.
- **How to Impress Interviewer:** Authz + isolation.

### 98. Security 98: DoS (data model)
- **Question:** Cheap DoS? Also discuss data model implications.
- **Ideal Answer:** Huge repo analyze; unbounded ask rate; giant graph render. For data model: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Quotas?
- **Common Mistake:** FAISS prevents.
- **How to Impress Interviewer:** Backpressure.

### 99. Security 99: OWASP LLM (API design)
- **Question:** Relevant LLM Top risks? Also discuss API design implications.
- **Ideal Answer:** Prompt injection, sensitive info disclosure, unbounded agency (low here), supply chain, vector weakness. For API design: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** Map to code.
- **Common Mistake:** Only XSS.
- **How to Impress Interviewer:** Cite mitigations.

### 100. Security 100: Logging PII (failure mode)
- **Question:** Log prompts? Also discuss failure mode implications.
- **Ideal Answer:** May contain secrets/code; need redaction and retention policy — currently barely logs. For failure mode: relate back to measured bottlenecks and explicit non-goals of the demo.
- **Expected Follow-up:** GDPR?
- **Common Mistake:** Log everything.
- **How to Impress Interviewer:** Privacy by design.
