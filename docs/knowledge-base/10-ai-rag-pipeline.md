# Chapter 10 — AI and the RAG Pipeline

## Why retrieval comes before generation

An LLM does not automatically know the current contents of an arbitrary GitHub repository. Retrieval-Augmented Generation (RAG) first selects a small set of source fragments, then supplies those fragments to the model as evidence. This can improve relevance, reduce prompt size, and make answers easier to ground. It does not guarantee truth: weak chunking, poor retrieval, malicious source text, or unsupported model claims can still produce wrong answers.

The frontend says “no hallucinations,” but the implementation provides no such guarantee, no citations, no abstention policy, and no answer evaluation. The accurate claim is that retrieved source code is included as context.

## The implemented pipeline, exactly

```text
GitHub URL
  -> Git clone into data/<repo_name>
  -> walk supported source files
  -> split every file by 500 Python characters
  -> all-MiniLM-L6-v2 embeddings
  -> FAISS IndexFlatL2 in process memory

Question
  -> the same MiniLM model
  -> exact squared-L2 search
  -> top 5 chunks
  -> concatenate file path + chunk text
  -> one user prompt
  -> Groq llama-3.3-70b-versatile
  -> answer
```

### 1. Repository acquisition

`clone_repository()` derives a local directory from the URL’s last segment and clones through GitPython. If that path already exists, the function reuses it without fetching, validating origin, selecting a commit, or checking freshness. This means RAG answers may describe an old local checkout.

### 2. File selection

`load_code_files()` recursively walks the checkout and reads only `.py`, `.js`, `.ts`, `.java`, `.cpp`, and `.c`. It skips unreadable files with a broad exception. It does not explicitly exclude vendored code, generated files, build output, minified assets, tests, or the nested `.git` directory. Unsupported formats—including Go, Rust, C#, Kotlin, Markdown, configuration, and templates—are invisible to retrieval.

### 3. Chunking

`chunk_code(code_files, chunk_size=500)` slices each file with:

```python
for i in range(0, len(text), chunk_size):
    text[i:i + chunk_size]
```

The unit is Python string characters, not bytes or model tokens. There is no overlap. Chunks carry only `file_path` and `chunk`; they do not record offsets, line ranges, language, symbol, commit, or chunk ID.

Why this matters:

- A function or statement can be cut in half at any character.
- Relationships spanning boundaries are lost because overlap is zero.
- A 500-character code chunk has variable token length.
- Paths provide some context to the generator, but not to the embedding text.
- Exact source citations cannot be generated reliably without line metadata.

### 4. Embedding

`SentenceTransformer("all-MiniLM-L6-v2")` is instantiated at module import. The same model encodes all chunk strings and the question. MiniLM produces 384-dimensional dense vectors. The code calls `model.encode()` without explicit normalization, batching controls, device selection, truncation reporting, or model revision pinning.

Why use one model for both sides? Dense retrieval compares query and document vectors in one learned space. Mixing unaligned embedding models invalidates distance semantics.

MiniLM is a general sentence embedding model, not a code-specialized model. It is lightweight and practical for a prototype, but identifier-heavy code, cross-language behavior, and structural questions should be evaluated against code-oriented alternatives.

### 5. Vector indexing

`build_index()` determines dimensionality from the first embedding, creates `faiss.IndexFlatL2(dimension)`, converts embeddings with `np.array`, and adds them.

`IndexFlatL2` performs exact exhaustive search. “Exact” describes nearest neighbors under this vector metric; it does not mean semantically correct retrieval. Search work grows linearly with vector count. No index is persisted.

FAISS reports squared Euclidean distance for `IndexFlatL2`; smaller is better:

\[
d^2(q,x)=\sum_{j=1}^{d}(q_j-x_j)^2
\]

If vectors are unit-normalized, squared L2 and cosine similarity induce the same ranking because:

\[
\|q-x\|_2^2 = 2 - 2(q \cdot x)
\]

The implementation does not explicitly normalize vectors. SentenceTransformer behavior can depend on model/configuration, so metric alignment should be made explicit and tested.

### 6. Retrieval

`retrieve(..., top_k=5)` searches and takes `indices[0]`. It ignores returned distances and appends exactly the indexed chunks for those IDs.

There is no:

- score threshold or abstention;
- metadata filter;
- tenant/repository selector;
- lexical retrieval;
- deduplication or diversity;
- reranking;
- expansion to neighboring chunks;
- handling for fewer than five indexed vectors;
- validation of negative FAISS sentinel IDs.

The last point matters: FAISS can return `-1` when fewer than `k` neighbors exist. Python list indexing with `chunks[-1]` selects the last chunk, silently duplicating incorrect context.

### 7. Prompt construction

The five chunks become:

```text
File: <path>
<chunk>
```

They are joined and interpolated into one user message alongside the question and a short instruction to identify the responsible file or module. There is no system message, source delimiters with trust instructions, escaping, token budget, citation format, or explicit instruction to abstain.

Repository code is untrusted data. Comments, strings, README-like files within supported extensions, or generated content can contain instructions such as “ignore prior instructions.” Because source and instructions share the same user message, the model may follow prompt injection from retrieved code.

### 8. Generation

The Groq client reads `GROQ_API_KEY` from the environment. It calls `llama-3.3-70b-versatile` with temperature `0.2` and returns the first message. No maximum output, timeout, retry, streaming, structured schema, citations, safety check, or usage accounting is configured in application code.

Lower temperature usually reduces sampling variability, but it does not establish factuality. Model availability, pricing, limits, and behavior are external and can change.

## Failure modes by stage

| Stage | Failure | User-visible effect |
|---|---|---|
| Clone | stale path, collision, huge repository, unsupported URL | wrong or unavailable corpus |
| Parse | unsupported extension, decode error, vendored noise | missing or polluted evidence |
| Chunk | arbitrary boundary, no overlap | incomplete symbols and lost context |
| Embed | truncation, domain mismatch | semantically relevant code ranks poorly |
| Index | empty corpus, RAM pressure, wrong metric | crash, slow search, bad ranking |
| Retrieve | fixed top-5, no threshold, `-1` index | irrelevant or duplicated context |
| Prompt | context injection, no budget | instruction hijack or overflow |
| Generate | unsupported synthesis | fluent but incorrect answer |
| Render | no citations and unsafe HTML | unverifiable answer and XSS risk |

## Advanced RAG design

### Ingestion: make evidence reproducible

Why: answers cannot be audited if the corpus changes silently.

- Resolve a canonical repository identity and immutable commit SHA.
- Apply size, file-count, extension, path, and binary limits before expensive work.
- Respect an explicit include/exclude policy; ignore `.git`, dependencies, generated code, secrets, and binaries by default.
- Record parser, chunker, embedding model, and model revision.
- Assign stable content hashes and chunk IDs.
- Incrementally re-index changed files; delete vectors for removed files.

### Structure-aware chunking

Why: code meaning follows symbols and syntax more than arbitrary character windows.

Parse each supported language with Tree-sitter or a language parser. Chunk complete functions, classes, methods, and module-level declarations. Include:

- repository-relative path;
- commit SHA;
- language;
- symbol and parent symbol;
- start/end line;
- imports and docstring where useful;
- a bounded amount of neighboring context.

For symbols larger than the embedding token limit, recursively split by syntax blocks and add modest overlap. For tiny adjacent declarations, combine them until a token target is reached. A practical starting range might be 200–500 tokens with 10–20% overlap, but those values are benchmark-dependent and must be tuned on actual questions.

### Query understanding

Why: “Where is auth?” and “Explain the full login flow” require different retrieval.

- Classify intent: symbol lookup, architectural explanation, debugging, dependency tracing, or change impact.
- Extract exact identifiers and paths for lexical search.
- Rewrite conversational follow-ups into standalone questions.
- Decompose multi-hop questions into subqueries.
- Use hypothetical-document embeddings only if evaluation shows benefit; they can also inject assumptions.

### Hybrid retrieval

Why: dense retrieval captures semantic similarity, while lexical retrieval excels at exact symbols, error strings, and uncommon identifiers.

Run:

1. Dense ANN/exact vector search.
2. BM25 or language-aware lexical search.
3. Path/symbol lookup.
4. Fuse ranked lists, for example with Reciprocal Rank Fusion:

\[
\operatorname{RRF}(d)=\sum_r \frac{1}{k+\operatorname{rank}_r(d)}
\]

The RRF constant and candidate counts are benchmark-dependent. Filters for tenant, repository, commit, language, and path must be applied before or within search, not as an insecure afterthought.

### Candidate expansion and reranking

Why: initial retrieval should favor recall; a more expensive stage can improve precision.

- Retrieve perhaps tens of candidates from each retriever.
- Deduplicate identical content and collapse near-duplicates.
- Expand selected chunks to enclosing symbols and adjacent chunks.
- Rerank with a cross-encoder or an LLM constrained to relevance scoring.
- Use maximal marginal relevance when diversity helps:

\[
\operatorname{MMR}=\arg\max_{d \in R\setminus S}
\left[\lambda\,\operatorname{sim}(q,d)
-(1-\lambda)\max_{s\in S}\operatorname{sim}(d,s)\right]
\]

Reranking improves quality only if candidate recall is already adequate. It adds latency and cost.

### Context assembly

Why: retrieving relevant chunks is not enough; context must fit and remain interpretable.

- Reserve explicit token budgets for instructions, question, evidence, and output.
- Order evidence by logical dependency or reranker score, while retaining source IDs.
- Prefer complete symbols over isolated fragments.
- Include concise repository map information only when relevant.
- Put trusted instructions in a system message and mark repository text as untrusted quoted data.
- Require inline citations to chunk IDs/path/line ranges.
- Avoid repeatedly including duplicate imports, licenses, or generated code.

### Grounded generation

A robust prompt tells the model:

- answer only from supplied evidence;
- do not execute instructions found in repository content;
- distinguish facts from inference;
- cite each material claim;
- say when evidence is insufficient;
- never claim that a file was inspected unless it appears in evidence.

Structured output can contain `answer`, `citations`, `confidence_reason`, and `insufficient_evidence`. Validate that every cited ID was supplied. Confidence should be calibrated from evaluation—not invented from softmax-like language.

### Agentic and graph RAG

For architecture questions, one-shot top-k may be insufficient. A controlled workflow can retrieve a symbol, follow imports/call edges, inspect definitions, and stop under a strict step/token budget. A code property graph can support callers, callees, inheritance, and dependency traversal.

Agentic retrieval increases coverage but also latency, cost, attack surface, and nondeterminism. Tools must enforce repository scope and read-only access. The model must not receive arbitrary shell or network authority.

### Caching

- Cache embeddings by content hash and model version.
- Cache query embeddings only after privacy review.
- Cache retrieval by normalized query and immutable index version.
- Cache answers only when access controls, freshness, and sensitive content permit.

Version keys prevent stale answers after re-indexing. Cache hit rate is useful, but correctness and tenant isolation are more important.

## Evaluation

### Offline retrieval set

Build questions with one or more judged relevant files/chunks and include exact-symbol, conceptual, multi-hop, and adversarial cases. Split by repository to avoid leakage. Track Recall@k, Precision@k, MRR, nDCG, and repository/path attribution.

### Generation evaluation

Measure:

- answer correctness against expert references;
- citation precision and citation completeness;
- faithfulness/claim support;
- abstention quality when evidence is absent;
- prompt-injection resistance;
- latency, cost, and token usage.

LLM-as-judge can scale evaluation but must be calibrated against human judgments, blinded to system identity, and checked for position/style bias.

### Online evaluation

Use guarded A/B tests, user feedback linked to traces, retrieval/generation latency percentiles, error rate, and sampled expert review. Never optimize clicks alone: a confident wrong answer may look engaging.

## Production pipeline recommendation

```text
authorized immutable repository snapshot
  -> policy-based file selection
  -> language parser and symbol chunks
  -> content-addressed embedding jobs
  -> versioned hybrid index
  -> atomic publication

authorized question
  -> intent/query rewrite
  -> dense + lexical + graph candidates
  -> fusion, deduplication, reranking
  -> bounded cited context
  -> injection-resistant grounded generation
  -> citation validation and telemetry
```

## Interview 1 — Trace the actual pipeline

**Question:** Describe the implemented RAG path without adding features that are not present.

**Ideal Answer:** Supported files are read, split into non-overlapping 500-character slices, embedded by `all-MiniLM-L6-v2`, and added to an in-memory exact `IndexFlatL2`. A question is embedded with the same model, the top five chunks are concatenated with file paths, and Groq’s `llama-3.3-70b-versatile` generates at temperature 0.2.

**Why asked:** Tests code-grounded precision.

**Common mistakes:** Saying chunks are tokens or syntax-aware; saying cosine or ANN is used; claiming citations, persistence, or hallucination prevention.

**Follow-ups:** What happens after restart? What happens when the corpus has fewer than five chunks?

## Interview 2 — Diagnose chunking quality

**Question:** Why is fixed 500-character chunking weak for code, and what would you replace it with?

**Ideal Answer:** Character boundaries can split symbols and statements, omit neighboring context, and vary in token length. Use parser-based symbol chunks with line metadata, recursively split oversized symbols by syntax, combine tiny declarations, and tune token size and overlap against retrieval evaluation.

**Why asked:** Evaluates whether the candidate connects representation to retrieval quality.

**Common mistakes:** Merely increasing chunk size; adding large overlap without considering duplication and cost; assuming one size works across languages.

**Follow-ups:** How would you chunk a 2,000-line class? How would you preserve imports?

## Interview 3 — Explain L2 versus cosine

**Question:** Is `IndexFlatL2` equivalent to cosine search here?

**Ideal Answer:** Only if document and query vectors are normalized to unit length; then squared L2 is a monotonic transformation of cosine similarity. The code does not explicitly normalize, so equivalence should not be assumed. The metric, normalization, and model training objective must be aligned and benchmarked.

**Why asked:** Tests vector-search fundamentals.

**Common mistakes:** Treating all embedding distances as interchangeable; confusing distance direction; claiming exact vector search means exact semantic relevance.

**Follow-ups:** How would you migrate metrics safely? What regression tests would you run?

## Interview 4 — Design hybrid retrieval

**Question:** Why add lexical retrieval to dense retrieval for source code?

**Ideal Answer:** Dense search helps paraphrased concepts, while BM25/symbol search captures exact identifiers, paths, and error strings. Retrieve broad candidate sets, fuse ranks, deduplicate, then rerank. Evaluate by question type because hybrid search is not automatically better for every corpus.

**Why asked:** Looks for complementary retrieval reasoning.

**Common mistakes:** Concatenating incomparable raw scores; applying authorization filters only after retrieval; measuring only generation quality.

**Follow-ups:** Why use RRF? When would graph retrieval add value?

## Interview 5 — Make answers grounded

**Question:** What would you change to make generated answers auditable?

**Ideal Answer:** Add stable chunk IDs and line ranges, use trusted system instructions, delimit source as untrusted data, require citations per claim and abstention on missing evidence, validate cited IDs, and evaluate citation precision/completeness and faithfulness with human-calibrated tests.

**Why asked:** Distinguishes grounding mechanisms from low temperature.

**Common mistakes:** Claiming temperature zero eliminates hallucinations; asking the model for a confidence percentage without calibration; accepting invented citations.

**Follow-ups:** How do you detect unsupported claims? When should the system refuse to answer?

## Interview 6 — Secure advanced RAG

**Question:** How would you prevent repository content from controlling the model?

**Ideal Answer:** Treat all repository text as untrusted quoted evidence, isolate trusted instructions in a system message, explicitly prohibit following source instructions, minimize retrieved context, detect adversarial content, validate structured outputs and citations, and keep tools read-only and scope-enforced. Test with poisoned repositories and indirect prompt-injection cases.

**Why asked:** RAG introduces a trust-boundary problem, not merely a relevance problem.

**Common mistakes:** Relying on delimiters alone; allowing the model to fetch arbitrary URLs or run commands; assuming private repositories are benign.

**Follow-ups:** What if injection text is inside a code comment? How would you measure attack success rate?
