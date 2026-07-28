# Chapter 19 — Interview Preparation

## Purpose

This chapter is a **drill gym**, not a summary. It contains **1,400** project-grounded questions (14 × 100) spanning internship through FAANG senior loops.

Every question file uses the same answer schema:

- **Question**
- **Ideal Answer**
- **Expected Follow-up**
- **Common Mistake**
- **How to Impress Interviewer**

## How to practice

1. Pick a bank (e.g. Backend).  
2. Answer out loud in ≤90 seconds without opening code.  
3. Only then read the ideal answer.  
4. Speak the follow-up answer too.  
5. Mark weak topics and re-read the matching chapters 1–18.

**Anti-patterns**

- Memorizing buzzwords not in the repo (Redis, LangChain, cosine-as-implemented, Docker-as-shipped).  
- Claiming production readiness.  
- Skipping “I would improve X by …”.  

## Question banks

| # | Theme | Path |
|---|---|---|
| 1 | Beginner | [chapter-19-question-bank/01-beginner-100.md](chapter-19-question-bank/01-beginner-100.md) |
| 2 | Intermediate | [chapter-19-question-bank/02-intermediate-100.md](chapter-19-question-bank/02-intermediate-100.md) |
| 3 | Advanced | [chapter-19-question-bank/03-advanced-100.md](chapter-19-question-bank/03-advanced-100.md) |
| 4 | System Design | [chapter-19-question-bank/04-system-design-100.md](chapter-19-question-bank/04-system-design-100.md) |
| 5 | Backend | [chapter-19-question-bank/05-backend-100.md](chapter-19-question-bank/05-backend-100.md) |
| 6 | AI / RAG / LLM | [chapter-19-question-bank/06-ai-100.md](chapter-19-question-bank/06-ai-100.md) |
| 7 | ML | [chapter-19-question-bank/07-ml-100.md](chapter-19-question-bank/07-ml-100.md) |
| 8 | Cloud | [chapter-19-question-bank/08-cloud-100.md](chapter-19-question-bank/08-cloud-100.md) |
| 9 | DevOps | [chapter-19-question-bank/09-devops-100.md](chapter-19-question-bank/09-devops-100.md) |
| 10 | Security | [chapter-19-question-bank/10-security-100.md](chapter-19-question-bank/10-security-100.md) |
| 11 | Database / Storage | [chapter-19-question-bank/11-database-100.md](chapter-19-question-bank/11-database-100.md) |
| 12 | Architecture | [chapter-19-question-bank/12-architecture-100.md](chapter-19-question-bank/12-architecture-100.md) |
| 13 | HR / Behavioral | [chapter-19-question-bank/13-hr-100.md](chapter-19-question-bank/13-hr-100.md) |
| 14 | Project Defence | [chapter-19-question-bank/14-project-defense-100.md](chapter-19-question-bank/14-project-defense-100.md) |

## Must-memorize facts (cheat sheet)

| Fact | Value |
|---|---|
| UI | Streamlit `frontend.py` |
| API | FastAPI `app/api.py` on `:8000` |
| Endpoints | `POST /analyze`, `/ask`, `/architecture` |
| Chunking | 500 **characters**, no overlap |
| Embeddings | `all-MiniLM-L6-v2`, 384 dimensions |
| Index | `faiss.IndexFlatL2` (exact L2) |
| top_k | 5 |
| LLM | Groq `llama-3.3-70b-versatile`, temperature `0.2` |
| State | `pipeline = {}` in API process memory |
| Graph | Python `ast` imports → NetworkX; basename keys |
| Not present | Auth, Redis, Mongo/Postgres, Docker, CI, tests, reranker |

## Interview section mapping

| Interview type | Start with banks | Then read chapters |
|---|---|---|
| Internship | 01, 13, 14 | 1, 3, 5 |
| SDE-1 backend | 05, 02, 11 | 2, 4, 9, 15 |
| ML / AI eng | 06, 07, 03 | 8, 10, 11 |
| Senior / staff | 04, 12, 10, 14 | 14, 17, 18, 20 |
| Behavioral | 13 | 18, 20 |

## After Chapter 19

Proceed to [20-final-project-defence.md](20-final-project-defence.md) and run a full mock interview without notes.

## Meta interview questions

### Beginner
**Question:** How should you use a 1400-question bank without burning out?  
**Ideal Answer:** Spaced repetition by weak topic; 20–30 questions/day aloud; always tie answers to files in `app/`.  
**Why asked:** Learning strategy.  
**Common mistakes:** Passive reading only.  
**Follow-ups:** How do you know you’re ready?

### FAANG
**Question:** An interviewer says your answers sound memorized.  
**Ideal Answer:** Pivot to a live walkthrough of `vector_store.py` / failure demo (two-user overwrite), and quantify with C×D complexity.  
**Why asked:** Ownership vs script.  
**Common mistakes:** Recite README.  
**Follow-ups:** Change a design decision on the fly.

### Trick
**Question:** “Your docs say cosine similarity.”  
**Ideal Answer:** “The handbook discusses cosine as theory; the implementation uses IndexFlatL2. Under unit-norm embeddings rankings relate, but I describe the code accurately.”  
**Why asked:** Doc/code discipline.  
**Common mistakes:** Panic or invent.  
**Follow-ups:** Show the line.
