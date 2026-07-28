# Advanced Interview Question Bank — 100 Questions

`Current demo` describes behavior present in this repository. `Proposal` describes an improvement, not an implemented feature.

## 1. What distance function does the current FAISS index use, and what does a smaller score mean?
**Ideal Answer:** Current demo: `build_index` creates `faiss.IndexFlatL2`, so search returns squared Euclidean distances and lower is better.
**Expected Follow-up:** How would cosine similarity change preprocessing?
**Common Mistake:** Calling the returned values similarity scores or saying larger is better.
**How to Impress Interviewer:** Note that normalized vectors make squared L2 ranking equivalent to cosine ranking.

## 2. Derive the relationship between cosine similarity and squared L2 distance for normalized embeddings.
**Ideal Answer:** For unit vectors, `||x-y||² = ||x||² + ||y||² - 2x·y = 2 - 2 cos(x,y)`, so either metric gives identical ordering.
**Expected Follow-up:** Are the current MiniLM embeddings normalized?
**Common Mistake:** Assuming normalization without requesting it from `model.encode`.
**How to Impress Interviewer:** Propose `normalize_embeddings=True` and test ranking parity.

## 3. What are the time and space costs of `IndexFlatL2` here?
**Ideal Answer:** Current demo: exact search scans all `N` vectors, costing roughly `O(Nd)` per query and `O(Nd)` memory for dimension `d`.
**Expected Follow-up:** When would an approximate index be justified?
**Common Mistake:** Claiming FAISS automatically makes search sublinear.
**How to Impress Interviewer:** Connect the threshold to measured corpus size, latency, recall, and memory.

## 4. Why can `len(embeddings[0])` fail in `build_index`?
**Ideal Answer:** Current demo: an empty repository or no supported files yields no chunks and an empty embedding batch; indexing then dereferences element zero.
**Expected Follow-up:** Where should validation occur?
**Common Mistake:** Catching every exception and returning an empty index.
**How to Impress Interviewer:** Define an explicit no-indexable-code domain error before embedding.

## 5. What numerical dtype risk exists when adding embeddings to FAISS?
**Ideal Answer:** Current demo passes `np.array(embeddings)` without explicitly enforcing contiguous `float32`, which FAISS expects in common Python bindings.
**Expected Follow-up:** What conversion would you use?
**Common Mistake:** Converting to `float64` for “precision.”
**How to Impress Interviewer:** Use `np.ascontiguousarray(embeddings, dtype=np.float32)` and assert shape.

## 6. What happens when `top_k=5` but the index contains fewer than five vectors?
**Ideal Answer:** FAISS may pad missing neighbors with index `-1`; current `chunks[idx]` then selects the final chunk, producing duplicates or false evidence.
**Expected Follow-up:** How would you prevent it?
**Common Mistake:** Assuming FAISS shortens the result list.
**How to Impress Interviewer:** Bound `k` by `index.ntotal` and reject negative indices.

## 7. Why is fixed 500-character chunking mathematically crude for retrieval?
**Ideal Answer:** Current demo slices code by character offsets, unrelated to tokens or syntax, so semantic units split unpredictably and chunk information density varies.
**Expected Follow-up:** What chunking objective would you optimize?
**Common Mistake:** Treating 500 characters as 500 model tokens.
**How to Impress Interviewer:** Discuss token budget, boundary coherence, overlap, and retrieval recall together.

## 8. How can chunk boundaries lower recall even when embeddings are good?
**Ideal Answer:** A relevant symbol signature and its body can land in separate chunks; neither embedding fully represents the question, lowering nearest-neighbor rank.
**Expected Follow-up:** Would overlap solve every case?
**Common Mistake:** Increasing `top_k` as the only remedy.
**How to Impress Interviewer:** Propose AST-aware units with bounded token windows and parent context.

## 9. What duplicate-information effect would overlapping chunks introduce?
**Ideal Answer:** Proposal: overlap improves boundary coverage but creates correlated vectors that can occupy several top results, reducing evidence diversity.
**Expected Follow-up:** How would you diversify results?
**Common Mistake:** Assuming each nearest chunk adds independent information.
**How to Impress Interviewer:** Mention MMR, per-file caps, or deduplication by span overlap.

## 10. Why might L2 distance be poorly calibrated across the current embeddings?
**Ideal Answer:** Current demo does not explicitly normalize vectors; magnitude can affect L2 distance independently of semantic angle.
**Expected Follow-up:** How would you evaluate this claim?
**Common Mistake:** Saying SentenceTransformer always returns normalized outputs.
**How to Impress Interviewer:** Inspect norm distribution and compare retrieval metrics before and after normalization.

## 11. Is the current retrieval deterministic?
**Ideal Answer:** Current demo: embedding inference and exact flat search are generally stable, but ties, library kernels, model versions, and repository traversal order can affect results.
**Expected Follow-up:** How would you make tests reproducible?
**Common Mistake:** Equating temperature `0.2` with end-to-end determinism.
**How to Impress Interviewer:** Pin versions, fixtures, ordering, model revision, and expected neighbor IDs.

## 12. What concurrency hazard exists in the module-level `pipeline` dictionary?
**Ideal Answer:** Current demo: all users share one mutable dictionary; concurrent analyses can overwrite `chunks`, `index`, and `summary` without isolation.
**Expected Follow-up:** Can readers observe mixed state?
**Common Mistake:** Assuming Python’s GIL makes a multi-key update atomic.
**How to Impress Interviewer:** Explain a query can pair repository B’s index with repository A’s chunks.

## 13. How can `/analyze` publish a partially updated pipeline?
**Ideal Answer:** Current demo assigns `chunks` and `index` before computing and assigning `summary`; concurrent requests can observe an intermediate state.
**Expected Follow-up:** What publication pattern is safer?
**Common Mistake:** Adding a lock only around individual assignments.
**How to Impress Interviewer:** Build an immutable snapshot locally, then swap one reference atomically under a lock.

## 14. What race occurs when two users analyze different repositories simultaneously?
**Ideal Answer:** Both CPU-bound pipelines execute against shared global state; whichever writes last becomes active, and interleaving can corrupt logical index-to-chunk correspondence.
**Expected Follow-up:** How should repository identity be modeled?
**Common Mistake:** Keying only the summary by repository.
**How to Impress Interviewer:** Use immutable index records keyed by normalized repo URL plus commit SHA.

## 15. Why does multiple-worker deployment break the global-pipeline assumption?
**Ideal Answer:** Current demo state is process-local. Different FastAPI workers can hold different or empty pipelines, so `/ask` may hit a worker that never handled `/analyze`.
**Expected Follow-up:** What state should leave process memory?
**Common Mistake:** Using sticky sessions as the complete solution.
**How to Impress Interviewer:** Separate durable metadata/object storage from a loadable vector-index service.

## 16. What failure does `/ask` produce before any repository is analyzed?
**Ideal Answer:** Current demo indexes missing dictionary keys and raises `KeyError`, likely surfacing as HTTP 500 rather than a clear readiness error.
**Expected Follow-up:** Which status code would you return?
**Common Mistake:** Returning an empty LLM answer.
**How to Impress Interviewer:** Use a typed 409/404 domain response with an index identifier.

## 17. Why are the synchronous FastAPI handlers a throughput concern?
**Ideal Answer:** Current demo performs cloning, filesystem I/O, embedding, and LLM calls synchronously; these long tasks consume worker threads and increase queueing.
**Expected Follow-up:** Would changing `def` to `async def` fix it?
**Common Mistake:** Calling blocking libraries directly inside async handlers.
**How to Impress Interviewer:** Separate jobs, use bounded executors, and keep async only around truly async I/O.

## 18. Which current operation is most likely CPU-heavy?
**Ideal Answer:** SentenceTransformer embedding is the major local compute stage; FAISS exact search is also CPU work but usually smaller per query.
**Expected Follow-up:** How would batching affect throughput?
**Common Mistake:** Identifying the Groq network call as local CPU work.
**How to Impress Interviewer:** Profile clone, parse, encode, add, search, and generation separately.

## 19. What backpressure is missing from `/analyze`?
**Ideal Answer:** Current demo accepts expensive analyses without queue limits, admission control, size limits, or per-user quotas.
**Expected Follow-up:** What overload response is appropriate?
**Common Mistake:** Letting every request start and relying on memory exhaustion.
**How to Impress Interviewer:** Propose bounded queues, 429/503 responses, and cost-aware admission.

## 20. How would cancellation behave if a client disconnects during cloning?
**Ideal Answer:** Current demo has no explicit cancellation propagation; the synchronous clone can continue consuming disk/network after the client disappears.
**Expected Follow-up:** How would jobs become cancellable?
**Common Mistake:** Assuming HTTP disconnect automatically terminates GitPython.
**How to Impress Interviewer:** Track job state and terminate isolated clone subprocesses safely.

## 21. What repository-name collision exists in `clone_repository`?
**Ideal Answer:** Current demo derives storage solely from the last URL segment, so different owners’ repositories with the same name map to one directory.
**Expected Follow-up:** What key would avoid collisions?
**Common Mistake:** Appending a random suffix and losing cache identity.
**How to Impress Interviewer:** Hash canonical URL and include commit SHA for immutable versions.

## 22. Why can a cached clone become stale?
**Ideal Answer:** Current demo returns immediately whenever the directory exists; it does not fetch, validate remote origin, or checkout a requested revision.
**Expected Follow-up:** Is automatic pull always safe?
**Common Mistake:** Mutating a possibly dirty working tree with `pull`.
**How to Impress Interviewer:** Cache bare objects and create immutable worktrees per commit.

## 23. What URL-parsing edge case affects clone paths?
**Ideal Answer:** Current demo uses string splitting; trailing slashes can produce an empty repo name, and nonstandard Git URL forms are not robustly parsed.
**Expected Follow-up:** How should URLs be validated?
**Common Mistake:** Using regex alone as the security boundary.
**How to Impress Interviewer:** Parse, allowlist schemes/hosts as required, normalize, and verify resolved destinations.

## 24. What security failure can unrestricted repository URLs cause?
**Ideal Answer:** Current demo passes user input to GitPython, enabling access attempts to local paths or internal network Git endpoints depending on environment.
**Expected Follow-up:** What threat category is this?
**Common Mistake:** Calling it SQL injection.
**How to Impress Interviewer:** Identify SSRF/local-file exposure and require scheme, host, DNS, and egress controls.

## 25. Why is repository content itself untrusted input?
**Ideal Answer:** Cloned files can be huge, malformed, adversarially encoded, or contain prompt-injection text that enters the LLM context.
**Expected Follow-up:** Does the system execute repository code?
**Common Mistake:** Claiming cloning is safe because no code is imported.
**How to Impress Interviewer:** Separate execution risk from resource exhaustion and indirect prompt injection.

## 26. What resource-exhaustion paths exist during repository loading?
**Ideal Answer:** Current demo recursively reads every supported file fully, with no repository, file, depth, symlink, or aggregate byte limits.
**Expected Follow-up:** What limits belong at each stage?
**Common Mistake:** Limiting only chunk count after files are already loaded.
**How to Impress Interviewer:** Enforce clone, traversal, per-file, aggregate, chunk, and embedding-batch budgets.

## 27. Why is bare `except` in `load_code_files` dangerous?
**Ideal Answer:** Current demo silently discards encoding, permission, and unexpected programming errors, making index completeness unknowable.
**Expected Follow-up:** Which errors should be recoverable?
**Common Mistake:** Removing all error handling.
**How to Impress Interviewer:** Catch expected I/O/Unicode errors, emit structured diagnostics, and report skipped files.

## 28. What symlink issue can arise during traversal?
**Ideal Answer:** Current `os.walk` defaults to not following directory symlinks, but file symlinks may still be opened and could point outside the clone boundary.
**Expected Follow-up:** How would you contain reads?
**Common Mistake:** Assuming path prefix strings safely enforce containment.
**How to Impress Interviewer:** Resolve real paths and verify they remain beneath the repository root.

## 29. Why can a single minified JavaScript file dominate the index?
**Ideal Answer:** Current character slicing creates many chunks proportional to file bytes, so a huge generated file contributes many vectors and crowds retrieval.
**Expected Follow-up:** How would you identify generated artifacts?
**Common Mistake:** Excluding all large files without measurement.
**How to Impress Interviewer:** Combine path rules, entropy/line heuristics, manifests, and per-file chunk caps.

## 30. How does traversal order affect `main_modules`?
**Ideal Answer:** Current demo appends Python filenames in `os.walk` order and returns the first five, so “main” means first encountered, not architecturally important.
**Expected Follow-up:** What ranking could be better?
**Common Mistake:** Sorting alphabetically and calling that importance.
**How to Impress Interviewer:** Rank by entry-point evidence, import centrality, and package structure.

## 31. What does `total_files` actually count?
**Ideal Answer:** Current demo counts every filesystem entry returned as a file, not only supported source files or successfully indexed files.
**Expected Follow-up:** Why is that misleading?
**Common Mistake:** Equating it to the number of embedded files.
**How to Impress Interviewer:** Report discovered, eligible, read, skipped, and indexed counts separately.

## 32. Which advertised language is omitted from summary detection?
**Ideal Answer:** Current parser supports `.cpp` and `.c`, but `generate_repo_summary` only recognizes Python, JavaScript, TypeScript, and Java.
**Expected Follow-up:** How would you avoid such drift?
**Common Mistake:** Duplicating another extension list.
**How to Impress Interviewer:** Centralize a language registry consumed by parser and summary.

## 33. Why can file paths leak environment details to the LLM?
**Ideal Answer:** Current chunks retain clone-relative construction that may be relative today but can include deployment path details depending on `save_dir`; paths are inserted into prompts.
**Expected Follow-up:** What path representation is sufficient?
**Common Mistake:** Removing filenames entirely.
**How to Impress Interviewer:** Store normalized repository-relative paths and reject traversal.

## 34. What dependency-analysis precision issue comes from using filenames as graph keys?
**Ideal Answer:** Current demo uses `file` rather than relative path, so two `utils.py` files in different packages overwrite each other.
**Expected Follow-up:** What should node identity be?
**Common Mistake:** Using only imported module strings for both sides.
**How to Impress Interviewer:** Use canonical module names plus repository-relative paths and resolution metadata.

## 35. Why are AST import strings not yet dependency edges between files?
**Ideal Answer:** Current demo records names such as `os` or `app.chunker` without resolving them to local modules, external packages, or standard library nodes.
**Expected Follow-up:** How would relative imports work?
**Common Mistake:** Assuming every import name maps to a repository file.
**How to Impress Interviewer:** Resolve with package context and classify unresolved/external dependencies.

## 36. What does `ast.walk` lose about imports?
**Ideal Answer:** It finds imports anywhere but does not preserve useful context such as scope, conditional branches, `TYPE_CHECKING`, or dynamic import semantics.
**Expected Follow-up:** Why does context matter?
**Common Mistake:** Treating an optional import as an unconditional runtime dependency.
**How to Impress Interviewer:** Attach location, scope, and condition metadata to edges.

## 37. Which Python dependencies cannot the current AST analyzer see?
**Ideal Answer:** Dynamic imports through `importlib`, `__import__`, plugin discovery, string-based entry points, and runtime path manipulation are missed.
**Expected Follow-up:** Can static analysis be complete?
**Common Mistake:** Promising perfect dependency recovery.
**How to Impress Interviewer:** State conservative limits and combine static evidence with runtime traces where needed.

## 38. Why can `/architecture` clone work duplicate `/analyze` work?
**Ideal Answer:** Current demo invokes `clone_repository` independently and reparses Python files instead of reusing an analysis artifact or job result.
**Expected Follow-up:** What cache key would be safe?
**Common Mistake:** Caching only by mutable URL.
**How to Impress Interviewer:** Key artifacts by normalized URL, commit SHA, analyzer version, and configuration.

## 39. What error-handling gap exists in `build_dependency_graph`?
**Ideal Answer:** Syntax errors are silently skipped, while file-open errors are uncaught; clients receive neither partial-result metadata nor a clear failure.
**Expected Follow-up:** Should one malformed file fail the graph?
**Common Mistake:** Returning success with no skipped-file accounting.
**How to Impress Interviewer:** Return graph plus structured parse diagnostics and completeness metrics.

## 40. Why is `plt.show()` unsuitable in a backend helper?
**Ideal Answer:** Current demo’s `visualize_graph` can block or require a display; it mixes analysis with interactive rendering and is not used by the API.
**Expected Follow-up:** What should the boundary return?
**Common Mistake:** Rendering PNGs inside every request unconditionally.
**How to Impress Interviewer:** Keep graph data pure and let clients choose rendering.

## 41. What thread-safety concern exists around model inference?
**Ideal Answer:** Current demo shares one module-level SentenceTransformer instance. Whether concurrent `encode` calls are safe and efficient depends on backend/device behavior and must be tested.
**Expected Follow-up:** How would you control concurrency?
**Common Mistake:** Assuming read-only Python access proves native-library thread safety.
**How to Impress Interviewer:** Use a bounded inference queue and benchmark one model worker versus parallel calls.

## 42. What startup cost comes from constructing the embedding model at import time?
**Ideal Answer:** Current demo loads `all-MiniLM-L6-v2` while importing `app.embedder`, increasing startup latency and potentially downloading model assets.
**Expected Follow-up:** How does reload mode amplify this?
**Common Mistake:** Lazy-loading without synchronization.
**How to Impress Interviewer:** Prepackage a pinned model and initialize it in an explicit application lifecycle.

## 43. What availability risk exists if model download fails?
**Ideal Answer:** Current demo can fail application import before serving health endpoints because model construction occurs globally.
**Expected Follow-up:** Should readiness and liveness differ?
**Common Mistake:** Reporting healthy while embeddings cannot run.
**How to Impress Interviewer:** Expose process liveness separately from dependency/model readiness.

## 44. What Groq-client initialization failure is hidden until runtime?
**Ideal Answer:** Current demo creates the client with `GROQ_API_KEY` from the environment; a missing or invalid key can prevent useful generation behavior.
**Expected Follow-up:** When should configuration be validated?
**Common Mistake:** Logging the key during diagnostics.
**How to Impress Interviewer:** Validate presence at startup, redact secrets, and expose safe readiness details.

## 45. Why does temperature `0.2` not guarantee grounded answers?
**Ideal Answer:** Temperature controls sampling randomness, not factual grounding; the model can still infer beyond retrieved code or obey malicious context.
**Expected Follow-up:** What grounding controls would help?
**Common Mistake:** Setting temperature to zero and claiming hallucinations are solved.
**How to Impress Interviewer:** Require citations, abstention, evidence checks, and retrieval evaluation.

## 46. How can repository text perform prompt injection?
**Ideal Answer:** Current demo concatenates raw code into a prompt; comments or strings can instruct the model to ignore the user or reveal unrelated data.
**Expected Follow-up:** Is delimiting context sufficient?
**Common Mistake:** Trusting code because it is “data.”
**How to Impress Interviewer:** Use strong instruction hierarchy, delimiters, provenance, output validation, and least-privilege context.

## 47. What prompt-size failure can occur?
**Ideal Answer:** Five fixed-character chunks usually fit, but large paths, Unicode, and future chunk sizes can exceed provider token limits; no token budgeting exists.
**Expected Follow-up:** Where should truncation happen?
**Common Mistake:** Truncating the generated answer only.
**How to Impress Interviewer:** Budget system text, question, metadata, evidence, and output before the call.

## 48. Why is raw newline joining weak evidence formatting?
**Ideal Answer:** Current demo separates chunks with blank lines but includes no stable chunk IDs, line ranges, language tags, or explicit boundaries.
**Expected Follow-up:** What metadata should citations use?
**Common Mistake:** Citing only a basename.
**How to Impress Interviewer:** Preserve relative path, symbol, line span, commit SHA, and chunk ID.

## 49. What XSS risk exists in rendering the answer?
**Ideal Answer:** Current frontend inserts model output into HTML with `unsafe_allow_html=True`; untrusted repository-derived output may contain executable markup depending on Streamlit sanitization behavior.
**Expected Follow-up:** How would you render safely?
**Common Mistake:** Trusting the LLM as a sanitizer.
**How to Impress Interviewer:** Escape output or use safe Markdown components and test attack payloads.

## 50. What similar HTML-injection risk exists in summary module names?
**Ideal Answer:** Current demo interpolates repository filenames directly into HTML module pills, so crafted names can break markup or inject content.
**Expected Follow-up:** Where should escaping occur?
**Common Mistake:** Sanitizing only the repo URL.
**How to Impress Interviewer:** Escape at the output sink and retain raw values internally.

## 51. Why can the frontend-generated `repo_path` disagree with the backend?
**Ideal Answer:** Backend strips `.git`; frontend merely takes the final URL segment, so a `.git` URL makes the frontend inspect a different directory.
**Expected Follow-up:** What other URL case fails?
**Common Mistake:** Fixing both with duplicated string logic.
**How to Impress Interviewer:** Have the backend return an opaque analysis ID and architecture data.

## 52. What deployment-boundary violation exists in the frontend?
**Ideal Answer:** Current demo directly reads the backend’s local `data` directory to build a graph, so frontend and backend must share filesystem and code.
**Expected Follow-up:** Why does this fail under containers?
**Common Mistake:** Mounting one writable volume as the permanent architecture.
**How to Impress Interviewer:** Make the frontend an API client with no repository filesystem access.

## 53. What request reliability controls are absent from frontend HTTP calls?
**Ideal Answer:** Current demo sets no timeout, retry policy, cancellation, or structured exception handling for `requests.post`.
**Expected Follow-up:** Which requests are safe to retry?
**Common Mistake:** Retrying `/analyze` blindly without idempotency.
**How to Impress Interviewer:** Use deadlines, idempotency keys, status polling, and retry only safe transitions.

## 54. Why can HTTP 200 still conceal a semantically poor analysis?
**Ideal Answer:** Current demo reports success if functions return, even when files were silently skipped, chunks are low quality, or summary metadata is incomplete.
**Expected Follow-up:** What quality indicators belong in the response?
**Common Mistake:** Treating absence of exceptions as correctness.
**How to Impress Interviewer:** Return coverage, skipped reasons, model/index versions, and warnings.

## 55. What invariant must hold between `index` and `chunks`?
**Ideal Answer:** Vector row `i` must always correspond exactly to `chunks[i]`; any filtering, reordering, partial add, or mixed snapshot breaks retrieval correctness.
**Expected Follow-up:** How would you encode the invariant?
**Common Mistake:** Matching by list length only.
**How to Impress Interviewer:** Assign immutable chunk IDs and store row-to-ID mapping with checksums.

## 56. How would an embedding exception midway affect state?
**Ideal Answer:** Current demo builds embeddings before mutating the pipeline, so the previous state remains; however, cloned files may remain and callers get an untyped server error.
**Expected Follow-up:** Is retaining old state desirable?
**Common Mistake:** Clearing the current index at analysis start.
**How to Impress Interviewer:** Use explicit job failure while preserving the last known-good immutable snapshot.

## 57. How would a summary exception affect state consistency?
**Ideal Answer:** Current demo has already replaced `chunks` and `index` when summary generation runs, so failure can leave a new searchable index with an old summary.
**Expected Follow-up:** How would transactions help?
**Common Mistake:** Rolling back by mutating several globals again.
**How to Impress Interviewer:** Publish one completed analysis object only after every required stage succeeds.

## 58. Why is no provenance returned with answers?
**Ideal Answer:** Current demo returns only `{"answer": answer}` even though retrieved chunks contain paths; callers cannot independently verify which evidence was used.
**Expected Follow-up:** What should the API include?
**Common Mistake:** Asking the LLM to invent citations in prose.
**How to Impress Interviewer:** Return structured source spans directly from retrieval alongside generated claims.

## 59. How would you calculate retrieval recall@k for this project?
**Ideal Answer:** Build labeled questions with relevant chunk IDs; recall@k is the fraction whose relevant set intersects the top-k results, or use set-level recall when multiple chunks are required.
**Expected Follow-up:** Why is answer quality alone insufficient?
**Common Mistake:** Grading only fluent LLM output.
**How to Impress Interviewer:** Separate retrieval, context sufficiency, faithfulness, and final-answer metrics.

## 60. What does mean reciprocal rank measure here?
**Ideal Answer:** MRR averages `1/rank` of the first relevant chunk per query, emphasizing whether useful code appears early.
**Expected Follow-up:** When is MRR misleading?
**Common Mistake:** Using MRR for questions requiring several evidence chunks.
**How to Impress Interviewer:** Pair it with recall@k and multi-hop coverage.

## 61. How would you test whether `top_k=5` is optimal?
**Ideal Answer:** Current demo hard-codes five. Proposal: sweep k on labeled queries and measure recall, prompt cost, latency, redundancy, and answer faithfulness.
**Expected Follow-up:** Could k vary by query?
**Common Mistake:** Choosing the largest k because recall rises.
**How to Impress Interviewer:** Use confidence/margin signals and a token-budget-aware adaptive k.

## 62. What does a small gap between the first and fifth distances suggest?
**Ideal Answer:** It may indicate ambiguity or many near-equivalent chunks, but raw L2 gaps are not calibrated confidence without validation.
**Expected Follow-up:** How would you calibrate abstention?
**Common Mistake:** Treating a fixed distance threshold as universal.
**How to Impress Interviewer:** Fit thresholds on held-out queries by repository/domain.

## 63. Why might code-specific embeddings outperform MiniLM?
**Ideal Answer:** Current demo uses general-purpose `all-MiniLM-L6-v2`; code-trained models may better represent identifiers, syntax, and code-text alignment.
**Expected Follow-up:** Is a larger model automatically better?
**Common Mistake:** Selecting by benchmark reputation alone.
**How to Impress Interviewer:** Evaluate on this project’s question-to-code retrieval set and serving constraints.

## 64. What asymmetry exists between embedding documents and queries?
**Ideal Answer:** Current demo uses the same encoder without task prefixes; some retrieval models require distinct query/document instructions to align representations.
**Expected Follow-up:** How would migration affect old indexes?
**Common Mistake:** Re-embedding queries only.
**How to Impress Interviewer:** Version encoder plus preprocessing and rebuild all document vectors.

## 65. Why are exact character chunks poor for line-level citations?
**Ideal Answer:** Current chunk metadata stores text and path but no starting offset or line range, so exact source locations cannot be reconstructed reliably after transformations.
**Expected Follow-up:** What metadata would you add?
**Common Mistake:** Searching for chunk text and assuming uniqueness.
**How to Impress Interviewer:** Preserve byte offsets, line spans, symbol IDs, and content hashes.

## 66. How could Unicode affect 500-character chunks?
**Ideal Answer:** Python slicing counts Unicode code points, not UTF-8 bytes or model tokens; visually similar chunks can have very different storage and token costs.
**Expected Follow-up:** Can slicing split a code point?
**Common Mistake:** Claiming Python splits a Unicode code point in the middle.
**How to Impress Interviewer:** Distinguish code points, grapheme clusters, bytes, and tokenizer tokens.

## 67. What issue arises from splitting inside identifiers or strings?
**Ideal Answer:** Current demo can cut an identifier, comment, or literal across chunks, degrading syntax and semantic embedding quality.
**Expected Follow-up:** What parser strategy supports six languages?
**Common Mistake:** Proposing Python AST for every supported language.
**How to Impress Interviewer:** Use language-aware parsers such as tree-sitter with a fallback text splitter.

## 68. Why is Python currently “best” despite multi-language loading?
**Ideal Answer:** Current demo loads six extensions, but architecture analysis uses only Python AST and summaries omit C/C++; language-aware semantic parsing is absent.
**Expected Follow-up:** Does retrieval itself require parsing?
**Common Mistake:** Saying non-Python files are not indexed.
**How to Impress Interviewer:** Separate generic text retrieval support from language-specific structural analysis.

## 69. What consistency issue appears if files change after indexing?
**Ideal Answer:** Current demo’s cloned directory can be externally modified while vectors and chunks remain in memory, so answers no longer represent the on-disk graph.
**Expected Follow-up:** How would commit identity help?
**Common Mistake:** Watching files and mutating the index without versioning.
**How to Impress Interviewer:** Treat each analysis as an immutable snapshot tied to a commit SHA.

## 70. How would incremental indexing preserve correctness?
**Ideal Answer:** Proposal: hash files/chunks, re-embed changed content, remove obsolete vector IDs, and publish a new snapshot only after metadata and index agree.
**Expected Follow-up:** Can `IndexFlatL2` delete arbitrary rows easily?
**Common Mistake:** Appending changed vectors and leaving stale duplicates.
**How to Impress Interviewer:** Discuss ID-mapped indexes or full rebuilds below a size threshold.

## 71. What cache invalidation dimensions matter beyond commit SHA?
**Ideal Answer:** Chunking rules, supported extensions, embedding model/revision, normalization, analyzer code, and exclusion settings all affect artifacts.
**Expected Follow-up:** How would you represent them?
**Common Mistake:** Keying solely by repository URL.
**How to Impress Interviewer:** Compute a deterministic analysis-configuration fingerprint.

## 72. What is the memory footprint formula for vectors?
**Ideal Answer:** With `N` float32 vectors of dimension `d`, raw storage is about `4Nd` bytes, excluding FAISS and Python metadata.
**Expected Follow-up:** Estimate MiniLM at one million chunks.
**Common Mistake:** Using 8 bytes per float32.
**How to Impress Interviewer:** Calculate roughly 1.5 GB for `d=384`, before metadata.

## 73. What additional memory dominates before indexing?
**Ideal Answer:** Current demo holds full file contents, chunk strings, embedding arrays, and the FAISS copy simultaneously, causing substantial peak-memory amplification.
**Expected Follow-up:** How would streaming help?
**Common Mistake:** Measuring only final index size.
**How to Impress Interviewer:** Profile peak RSS and release/batch intermediate objects deliberately.

## 74. Why can embedding all chunks in one `model.encode` call fail?
**Ideal Answer:** Current demo materializes every chunk text and resulting embedding batch at once; a large repository can exhaust RAM or accelerator memory.
**Expected Follow-up:** What batch design is safer?
**Common Mistake:** Setting a model batch size while still retaining every intermediate.
**How to Impress Interviewer:** Stream bounded batches into durable artifact storage/index construction.

## 75. How would GPU use alter concurrency design?
**Ideal Answer:** Proposal: GPU embedding raises throughput but memory is bounded; concurrent requests can trigger OOM, so one or a few batching workers should own the device.
**Expected Follow-up:** What metric drives batching?
**Common Mistake:** Giving each web worker its own full model.
**How to Impress Interviewer:** Use dynamic batching constrained by tokens and device memory.

## 76. Why can exact FAISS search still be fast enough?
**Ideal Answer:** For demo-scale `N` and 384-dimensional MiniLM vectors, optimized contiguous brute-force distance calculations may meet latency targets without approximate-index complexity.
**Expected Follow-up:** When would you switch?
**Common Mistake:** Introducing HNSW before measuring.
**How to Impress Interviewer:** Establish p95 latency and memory thresholds through benchmarks.

## 77. What trade-off would HNSW introduce?
**Ideal Answer:** Proposal: HNSW offers faster approximate queries at larger scale, trading memory and build cost for tunable recall via construction/search parameters.
**Expected Follow-up:** Which parameter affects query recall?
**Common Mistake:** Claiming approximate search has exact recall.
**How to Impress Interviewer:** Discuss `efSearch`, `efConstruction`, graph degree, and measured recall.

## 78. What trade-off would IVF introduce?
**Ideal Answer:** Proposal: IVF searches selected clusters, reducing scan work but requiring training and tuning `nlist`/`nprobe`; poor training can hurt recall.
**Expected Follow-up:** What data trains the quantizer?
**Common Mistake:** Training on an unrepresentative tiny sample.
**How to Impress Interviewer:** Version the trained quantizer with the embedding distribution.

## 79. Why might reranking improve this pipeline?
**Ideal Answer:** Proposal: retrieve a broader candidate set cheaply, then use a cross-encoder or LLM reranker to model detailed query-code interactions.
**Expected Follow-up:** What is the latency cost?
**Common Mistake:** Reranking only the same five candidates.
**How to Impress Interviewer:** Tune candidate width and batch reranking against recall and p95.

## 80. What is maximal marginal relevance useful for?
**Ideal Answer:** Proposal: MMR balances query relevance against similarity to already selected chunks, reducing redundant evidence from the same file region.
**Expected Follow-up:** What parameter controls the balance?
**Common Mistake:** Describing MMR as a new embedding model.
**How to Impress Interviewer:** Relate lambda tuning to context diversity and answer coverage.

## 81. Why would hybrid lexical-semantic retrieval help code questions?
**Ideal Answer:** Proposal: exact identifiers, error strings, and API names favor lexical search, while conceptual questions favor embeddings; fusion captures both.
**Expected Follow-up:** How would you combine ranks?
**Common Mistake:** Adding incomparable raw BM25 and L2 scores directly.
**How to Impress Interviewer:** Use reciprocal-rank fusion or calibrated scores.

## 82. How can identifier casing affect retrieval?
**Ideal Answer:** Current general embeddings may blur or fragment `build_dependency_graph` and similar symbols; lexical matching preserves exact names.
**Expected Follow-up:** Would lowercasing help?
**Common Mistake:** Lowercasing all source and losing case-sensitive distinctions.
**How to Impress Interviewer:** Keep raw code and add identifier-aware tokenization/features.

## 83. What query-expansion failure mode should be guarded against?
**Ideal Answer:** Proposal: generated synonyms or symbols can drift from user intent and retrieve plausible but irrelevant modules.
**Expected Follow-up:** How would you constrain expansion?
**Common Mistake:** Always replacing the original query.
**How to Impress Interviewer:** Search original and expansions separately, then fuse with provenance.

## 84. Why are answers vulnerable to stale external model behavior?
**Ideal Answer:** Current demo specifies a model name but not a provider-side immutable revision; output can change despite unchanged code.
**Expected Follow-up:** What can be made reproducible?
**Common Mistake:** Promising bit-for-bit cloud LLM reproducibility.
**How to Impress Interviewer:** Record model identifier, parameters, prompt version, evidence IDs, and request timestamp.

## 85. What observability is missing around retrieval?
**Ideal Answer:** Current demo records no latency, distances, selected chunk IDs, index version, token counts, or failure-stage metrics.
**Expected Follow-up:** What must not be logged?
**Common Mistake:** Logging full private code and API credentials.
**How to Impress Interviewer:** Emit redacted structured traces linked by analysis and request IDs.

## 86. How would you decompose `/ask` latency?
**Ideal Answer:** Measure validation, query embedding, vector search, context assembly, provider queue/network, generation, and serialization separately.
**Expected Follow-up:** Which dominates today?
**Common Mistake:** Guessing without instrumentation.
**How to Impress Interviewer:** Track p50/p95/p99 and payload/token dimensions per stage.

## 87. What SLO would be meaningful for indexing?
**Ideal Answer:** Proposal: define completion latency and success/coverage targets by repository size class, rather than one latency bound for all repositories.
**Expected Follow-up:** How are canceled jobs counted?
**Common Mistake:** Using average duration only.
**How to Impress Interviewer:** Separate platform failures, user cancellations, and policy rejections.

## 88. How would you detect retrieval-quality regression after a model change?
**Ideal Answer:** Run a versioned offline benchmark of project-specific questions and compare recall@k, MRR, latency, memory, and downstream faithfulness.
**Expected Follow-up:** What online signal helps?
**Common Mistake:** Relying solely on thumbs-up rates.
**How to Impress Interviewer:** Shadow traffic with privacy controls and inspect rank changes.

## 89. What property-based test fits `chunk_code`?
**Ideal Answer:** For every input string, concatenating its chunks in order should reproduce the original exactly, with each chunk length at most the positive chunk size.
**Expected Follow-up:** What invalid input should be rejected?
**Common Mistake:** Testing only a 500-character ASCII fixture.
**How to Impress Interviewer:** Include empty, Unicode, and boundary lengths 499/500/501.

## 90. What invariant test fits retrieval?
**Ideal Answer:** Every returned item must map to a valid index row, contain required metadata, and never include padded `-1` neighbors.
**Expected Follow-up:** How would you test ties?
**Common Mistake:** Asserting one fixed order for equal distances.
**How to Impress Interviewer:** Validate result sets or deterministic tie-breaking explicitly.

## 91. How would you test concurrent snapshot publication?
**Ideal Answer:** Proposal: repeatedly analyze two distinguishable corpora while querying; assert each response’s index version and all chunks belong to one corpus only.
**Expected Follow-up:** What tool is required?
**Common Mistake:** Unit-testing dictionary assignment in isolation.
**How to Impress Interviewer:** Use barriers to force the dangerous interleavings.

## 92. What chaos test targets provider failure?
**Ideal Answer:** Inject timeouts, 429s, 5xx responses, malformed responses, and slow streams from Groq; verify bounded retries, deadlines, and safe errors.
**Expected Follow-up:** Which failures are retryable?
**Common Mistake:** Retrying every 4xx response.
**How to Impress Interviewer:** Respect `Retry-After`, jitter, idempotency, and a total retry budget.

## 93. How should rate limiting differ between endpoints?
**Ideal Answer:** Proposal: `/analyze` needs cost/size-weighted limits, while `/ask` needs request/token limits; `/architecture` also consumes clone and parse resources.
**Expected Follow-up:** What key identifies a caller?
**Common Mistake:** Trusting client-supplied IP headers directly.
**How to Impress Interviewer:** Combine authenticated tenant quotas with infrastructure-aware source controls.

## 94. Why are retries dangerous for `/analyze`?
**Ideal Answer:** Current endpoint is synchronous and lacks idempotency; client retries can duplicate expensive work or race on the same clone path.
**Expected Follow-up:** How would an idempotency key work?
**Common Mistake:** Deduplicating only after processing completes.
**How to Impress Interviewer:** Atomically reserve a canonical job key before work starts.

## 95. What filesystem race occurs when two requests clone the same repo?
**Ideal Answer:** Both can observe the path as absent and attempt cloning into it concurrently, causing failure or a partially created directory later treated as valid.
**Expected Follow-up:** How would you lock it?
**Common Mistake:** Using only an in-process lock in a multi-worker deployment.
**How to Impress Interviewer:** Use distributed job deduplication and atomic temp-directory promotion.

## 96. Why is checking only `os.path.exists` insufficient cache validation?
**Ideal Answer:** A directory may be incomplete, unrelated, or left by a failed clone; existence does not prove repository integrity or origin.
**Expected Follow-up:** What validation is needed?
**Common Mistake:** Deleting any existing directory automatically.
**How to Impress Interviewer:** Verify Git metadata, origin, commit, completion marker, and ownership before reuse.

## 97. What failure semantics should partial indexing have?
**Ideal Answer:** Proposal: define whether skipped files produce a usable degraded artifact or a failed job; expose coverage and never silently label partial work complete.
**Expected Follow-up:** What threshold would you choose?
**Common Mistake:** Requiring 100% despite harmless unsupported files.
**How to Impress Interviewer:** Make thresholds policy-driven by eligible bytes/files and critical paths.

## 98. How would you prevent one tenant from querying another tenant’s repository?
**Ideal Answer:** Current demo has no authentication or tenant isolation. Proposal: bind analysis IDs to principals and authorize every analysis, ask, and artifact operation.
**Expected Follow-up:** Are unguessable IDs sufficient?
**Common Mistake:** Treating UUID secrecy as authorization.
**How to Impress Interviewer:** Enforce ownership server-side and encrypt/isolate stored artifacts.

## 99. What deletion challenge arises once indexes are persisted?
**Ideal Answer:** Proposal: deleting metadata alone leaves code in vector files, object storage, caches, logs, and backups.
**Expected Follow-up:** How would deletion be verified?
**Common Mistake:** Promising immediate physical deletion from immutable backups.
**How to Impress Interviewer:** Track artifact lineage, cryptographic erasure options, retention, and tombstone audits.

## 100. What is the highest-priority correctness fix in the current internals?
**Ideal Answer:** Replace the shared multi-key global pipeline with validated immutable analysis snapshots keyed by repository/version; this prevents cross-user and mixed-state answers.
**Expected Follow-up:** What would you fix immediately after?
**Common Mistake:** Starting with a more sophisticated vector index.
**How to Impress Interviewer:** Prioritize state isolation, input limits, errors, provenance, then retrieval sophistication.
