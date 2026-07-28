# Chapter 8 — Algorithms

## 0. Scope

Algorithms **actually implemented** in this repo, plus the math interviewers expect you to know around them.

| Algorithm | File | Purpose |
|---|---|---|
| Fixed-size character chunking | `chunker.py` | Split source into 500-char windows |
| Dense bi-encoder embedding | `embedder.py` | Map text → R^384 |
| Exact L2 k-NN (flat scan) | `vector_store.py` + `retriever.py` | Find nearest chunks |
| Top-k selection | FAISS `search` | Return 5 neighbors |
| AST import extraction | `architecture.py` | Build import lists |
| Directed graph construction | NetworkX | Visualize dependencies |
| Repo summary heuristics | `repo_summary.py` | Counts + language set |

Notation: let `F` = files, `C` = chunks, `D = 384`, `K = 5`, `L` = chars in a file, `T` = tokens ≈ L/4 rough.

---

## 1. Fixed character chunking

### WHY
Embeddings need bounded inputs. Whole files can exceed practical lengths and mix unrelated concerns.

### WHAT
```
for i in range(0, len(text), chunk_size):  # chunk_size=500
    emit text[i:i+500]
```

### Complexity
| Case | Time | Space |
|---|---|---|
| Best/Avg/Worst | Θ(L) per file; Θ(Σ L) total | Θ(C) chunk strings |
| C | ≈ Σ ceil(L_f / 500) | |

### Edge cases
Empty file → empty chunk; mid-identifier splits; no overlap ⇒ boundary loss; binary misread as text (parser usually skips).

### Alternatives
| Strategy | Pros | Cons |
|---|---|---|
| Token chunks | Matches model limits | Needs tokenizer |
| Sliding window overlap | Better boundary recall | More chunks/cost |
| AST function chunks | Semantic units | Language-specific |
| Recursive markdown/code splitters | Structure-aware | Complexity |

### When NOT fixed chars
Production code search — prefer AST/symbol chunks + overlap.

### Math intuition
If average file 10KB → ~20 chunks/file. 500 files → ~10k chunks.

---

## 2. Dense embedding (MiniLM encode)

### WHY
Keyword search fails when user says “routing” but code says `@app.route`. Embeddings map paraphrases closer in vector space.

### WHAT (conceptual)
Tokenizer → transformer layers → pooling → `v ∈ R^384`.

### Complexity (practical)
| Step | Typical cost |
|---|---|
| Encode C chunks | ~O(C · S · Cost_model) where S sequence length |
| Encode 1 query | O(S · Cost_model) |

Worst case: huge C, long sequences truncated by model max length.

### Edge cases
Empty string embedding; non-English; code vs NL distribution shift.

### Optimization
Batch encode; GPU; cache by hash(file, mtime, model_id); incremental embed only changed files.

---

## 3. Exact L2 nearest neighbor (`IndexFlatL2`)

### WHY L2 here
FAISS default flat index API in code: `IndexFlatL2(dimension)`.

### Mathematics
For query `q` and vector `x`:
`d(q,x)^2 = Σ_i (q_i - x_i)^2`

Smaller distance ⇒ closer. FAISS returns smallest distances.

### Relation to cosine
If `||q||=||x||=1`, then `||q-x||^2 = 2 - 2⟨q,x⟩`. Ranking by L2 ≡ ranking by cosine similarity. SentenceTransformers often normalizes — **still say the code uses L2**.

### Complexity
| | Time | Space |
|---|---|---|
| Build `add` | Θ(C·D) | Θ(C·D) floats |
| Query | Θ(C·D) | Θ(D) + Θ(K) |
| Best/Avg/Worst query | All Θ(C·D) for flat | Exact |

### When Flat fails to scale
C = 10^7+, D=768+ → use HNSW/IVF/PQ (ANN). ANN trades exactness for speed.

### Edge cases
C < K → FAISS returns available; C=0 crash earlier; dimension mismatch crash.

---

## 4. Top-k retrieval mapping

### WHAT
FAISS gives indices; code maps to `chunks[idx]`. Distances discarded.

### Complexity
O(K) mapping after search.

### Alternatives
Score threshold; MMR diversity; rerank with cross-encoder; hybrid BM25+dense.

---

## 5. AST import extraction

### WHY
Static view of module coupling without running code.

### Algorithm
```
parse source → tree
for node in walk(tree):
  if Import: collect alias.names
  if ImportFrom: collect module
```

### Complexity
Time Θ(N_nodes) ≈ Θ(source size); Space Θ(imports).

### Edge cases
Syntax errors skipped; dynamic imports (`__import__`) missed; relative imports stored as module string; basename graph keys collide.

---

## 6. DiGraph construction

### WHAT
Edge `file → imported_name` for each import string.

### Complexity
Build Θ(E); drawing can be expensive layout O(worse than linear) visually.

### When NOT
Huge monorepos — graph unreadable; need clustering / hierarchical views.

---

## 7. Summary heuristics

Counting files + extension language tags + first 5 `.py` basenames.

### Complexity
Θ(files on disk walk).

### Not an ML algorithm
Important honesty in interviews.

---

## 8. End-to-end complexity of `/analyze`

`O(clone) + O(Σ L) + O(C · embed) + O(C · D)`

Dominant terms usually **clone** or **embed**, not FAISS add.

`/ask`: `O(embed query) + O(C·D) + O(LLM tokens)` — LLM usually dominates latency.

---

## Interview questions

### Beginner

#### 1. Chunk size meaning
**Question:** What does chunk_size=500 mean?
**Ideal Answer:** 500 characters, not tokens or lines.
**Why interviewer asked it:** Units matter.
**Common mistakes:** Saying 500 tokens.
**Follow-up questions:** How many tokens roughly?

#### 2. L2 meaning
**Question:** What distance does FAISS use here?
**Ideal Answer:** Euclidean L2 via IndexFlatL2.
**Why interviewer asked it:** Metric literacy.
**Common mistakes:** Cosine.
**Follow-up questions:** When equal to cosine rank?


### Intermediate

#### 1. Complexity search
**Question:** Time complexity of one query?
**Ideal Answer:** Θ(C·D) for flat L2 scan.
**Why interviewer asked it:** Scalability.
**Common mistakes:** O(1) or O(log n) wrongly.
**Follow-up questions:** When use HNSW?

#### 2. No overlap
**Question:** Why is no overlap a problem?
**Ideal Answer:** Logic spanning boundaries may never appear fully in one chunk; retrieval quality drops.
**Why interviewer asked it:** Chunking design.
**Common mistakes:** Ignoring.
**Follow-up questions:** How much overlap would you pick?


### Advanced

#### 1. ANN tradeoff
**Question:** When move from FlatL2 to HNSW?
**Ideal Answer:** When C grows so O(C·D) misses latency SLO; accept approximate neighbors; validate recall@k.
**Why interviewer asked it:** Systems ML.
**Common mistakes:** Always use ANN.
**Follow-up questions:** How measure recall vs exact?


### FAANG

#### 1. Design chunking for monorepo
**Question:** How chunk a 50M LOC monorepo?
**Ideal Answer:** Language-aware symbol chunking, incremental index, ownership filters, hierarchical summarization, doc+code hybrid, eval set of questions.
**Why interviewer asked it:** Hard design.
**Common mistakes:** Just 500 chars.
**Follow-up questions:** Cost model?


### Trick

#### 1. Best case FlatL2
**Question:** Is there a best case faster than O(C·D) for IndexFlatL2?
**Ideal Answer:** For true flat exact scan, still linear in C; early exit tricks aren't the FAISS Flat contract.
**Why interviewer asked it:** Catch fake optimizations.
**Common mistakes:** Claiming O(log n).
**Follow-up questions:** What index gives sublinear?



---

## Appendix A — Worked complexity examples

### Example 1: Analyze cost
- F = 800 files, average 8 KB = 6400 KB ≈ 6.4e6 chars
- C ≈ 6.4e6 / 500 = 12,800 chunks
- Embed ≈ 12,800 forward passes (batched, say batch 32 → 400 batches)
- FAISS add ≈ 12800 × 384 writes
- Dominant: embedding CPU or clone network

### Example 2: Ask cost
- Embed 1 query
- Search 12800 × 384 ≈ 4.9e6 subtract-multiply-adds — sub-10ms–tens of ms on modern CPU typically
- LLM 1–3 seconds typical → **LLM dominates ask latency**

### Example 3: When search dominates
- C = 5e6, D = 768 → ~3.8e9 ops/query — too slow for interactive CPU flat scan → ANN required

## Appendix B — Similarity metrics deep dive

| Metric | Formula | FAISS index | Use when |
|---|---|---|---|
| L2 | √Σ(q−x)² | IndexFlatL2 | Default geometric distance |
| Inner product | ⟨q,x⟩ | IndexFlatIP | Max IP; with normalized vectors ≈ cosine |
| Cosine | ⟨q,x⟩/(||q||||x||) | Often via normalize + IP | Angular similarity |

**When cosine fails:** magnitude carries meaning you care about; or embeddings not comparable across models; or short queries vs long chunks systematic bias.

## Appendix C — Top-k selection internals

After computing all distances, selecting k smallest can be done with:
- full sort O(C log C)
- partial select / heap O(C log K)
FAISS implements optimized selection; interview answer: “linear scan + efficient top-k, still Θ(C·D) distance work.”

## Appendix D — AST walk correctness limits

Misses:
- `importlib.import_module("x")`
- relative imports resolution to real files
- star imports expansion
- TYPE_CHECKING guarded imports still appear in AST

