# Chapter 16 — Testing

## 0. Current state

**No automated tests** ship with the project. Interviews: admit this, then describe the strategy you would implement.

---

## 1. Test pyramid for this app

| Layer | Goal | Examples |
|---|---|---|
| Unit | Pure functions | chunk boundaries, summary counts, AST imports on fixtures |
| Integration | Modules together | build_index+retrieve roundtrip |
| API | HTTP contract | `/analyze` `/ask` with mocks |
| UI | Optional smoke | Streamlit harder — prefer API tests |
| Load | Throughput/latency | Locust/k6 against `/ask` |
| Stress | Break points | Huge repo, tiny RAM |
| Chaos/failure injection | Resilience | Kill Groq, corrupt clone |

---

## 2. What to test per module

### `chunker.py`
- empty content; length 499/500/501; multiple files; unicode

### `code_parser.py`
- only supported extensions; skip binary; nested dirs

### `repo_loader.py`
- existing path short-circuit (tmp path); mock `git.Repo.clone_from`

### `embedder.py`
- mock `SentenceTransformer` to return deterministic vectors; shape (1,D) for query

### `vector_store.py` + `retriever.py`
- synthetic embeddings where query near chunk 2 → retrieve chunk 2; top_k

### `qa_engine.py`
- mock Groq client; assert prompt contains file path and question

### `architecture.py`
- fixture file with imports; syntax error file skipped; basename behavior documented

### `api.py`
- TestClient; mock pipeline stages; `/ask` without analyze → expect handled error (once you add handling)

---

## 3. Example pytest sketches

```python
# PROPOSED tests/test_chunker.py
from app.chunker import chunk_code

def test_chunk_split_500():
    files = [{"file_path": "a.py", "content": "x" * 1200}]
    chunks = chunk_code(files, chunk_size=500)
    assert len(chunks) == 3
    assert len(chunks[0]["chunk"]) == 500
```

```python
# PROPOSED mock Groq
def test_generate_answer(monkeypatch):
    class Fake:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    class R:
                        class choices:
                            pass
                    # simplified in real test with proper shape
                    ...
```

Use `fastapi.testclient.TestClient(app)`.

---

## 4. Mocking strategy

| Dependency | Mock technique |
|---|---|
| Git clone | monkeypatch `clone_from` |
| SentenceTransformer | fake encode → np.eye |
| Groq | fake completions.create |
| Network Streamlit | don't unit test; contract test API |

---

## 5. Load / stress / benchmarks

- Load: 50 concurrent `/ask` with prebuilt index
- Stress: analyze linux-sized repo until OOM
- Bench: embed C/s; search latency vs C; tokens/$ 

---

## 6. Failure injection

| Failure | Expectation (desired) |
|---|---|
| Groq 429 | retry/backoff or 503 |
| Groq timeout | error message, no hang |
| Empty pipeline | 400 "analyze first" |
| Corrupt PDF/N/A | N/A — code files |
| Disk full clone | clean error |

Today many failures are unhandled exceptions.

---

## Interview questions

### Beginner

#### 1. Any tests?
**Question:** Do you have unit tests?
**Ideal Answer:** Not yet; I'd add pytest for chunker and FAISS roundtrip first.
**Why interviewer asked it:** Honesty.
**Common mistakes:** 100% coverage claim.
**Follow-up questions:** First test?

#### 2. What is mocking?
**Question:** How mock Groq?
**Ideal Answer:** Replace client method to return fixed string; assert prompt content.
**Why interviewer asked it:** Testing literacy.
**Common mistakes:** Call real Groq in CI.
**Follow-up questions:** Cost issue?


### Intermediate

#### 1. Integration
**Question:** How test retrieve quality without LLM?
**Ideal Answer:** Fixed vectors; ensure geometric nearest neighbor returns expected chunk.
**Why interviewer asked it:** Separation.
**Common mistakes:** Only e2e.
**Follow-up questions:** Flaky?

#### 2. Load test
**Question:** What tool?
**Ideal Answer:** Locust/k6; pre-index; measure P95 ask.
**Why interviewer asked it:** Perf.
**Common mistakes:** Only unit tests.
**Follow-up questions:** SLOs?


### Advanced

#### 1. Eval CI
**Question:** How gate PRs on RAG quality?
**Ideal Answer:** Golden questions; Recall@K threshold; fail PR on regression.
**Why interviewer asked it:** ML CI.
**Common mistakes:** Only lint.
**Follow-up questions:** Non-determinism LLM?


### FAANG

#### 1. Test strategy
**Question:** Test plan for RAG service.
**Ideal Answer:** Unit+contract+retrieval eval+load+chaos+security scans; staging canaries.
**Why interviewer asked it:** Breadth.
**Common mistakes:** Only happy path.
**Follow-up questions:** Flaky LLM tests?


### Trick

#### 1. 100% coverage
**Question:** Is 100% coverage enough?
**Ideal Answer:** No — coverage ≠ quality; need eval metrics and failure tests.
**Why interviewer asked it:** Mature view.
**Common mistakes:** Yes.
**Follow-up questions:** Mutation testing?



---

## Appendix A — Priority test order (first week)

1. `chunk_code` boundaries  
2. FAISS retrieve nearest synthetic neighbor  
3. `/ask` without analyze returns controlled 400 (after you implement)  
4. Mock Groq prompt contains retrieved path  
5. Parser skips unsupported extensions  

## Appendix B — Failure injection matrix

| Inject | Layer | Expect |
|---|---|---|
| Groq timeout | qa_engine | 504/503 + log |
| clone Exception | repo_loader | 400/502 |
| empty embeddings | vector_store | precheck error |
| huge top_k | retriever | clamp |
| HTML script in answer | frontend | escaped |

## Appendix C — Benchmark harness sketch

```
for C in [1e3, 1e4, 1e5]:
  build flat index
  time 100 searches
  plot ms vs C  # should be ~linear for FlatL2
```

