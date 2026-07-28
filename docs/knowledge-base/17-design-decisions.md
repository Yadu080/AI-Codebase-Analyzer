# Chapter 17 — Design Decisions and Trade-offs

## Scope and evidence standard

This chapter records decisions visible in the implementation, not an idealized architecture. A “decision” includes an explicit technology choice and an implicit choice caused by omission (for example, one process-wide mutable index instead of per-repository state). Rationales are inferred from the small demonstration-oriented codebase and are labeled honestly: the repository does not contain ADRs, benchmarks, tests, or production requirements that prove author intent.

## System-level decision summary

The application is a synchronous, single-node RAG demonstration:

`GitHub URL → local clone → extension filter → 500-character chunks → MiniLM embeddings → exact FAISS L2 index → top-5 retrieval → Groq-hosted Llama answer`

FastAPI exposes the pipeline, Streamlit calls it over HTTP, and a separate Python-AST path produces an import graph. This is easy to explain and demo, but its quality, isolation, security, observability, and scale properties are not production-ready.

## Implemented decisions

### D1. Retrieval-augmented generation instead of asking an LLM unaided

- **Evidence:** `api.py` retrieves indexed chunks before `qa_engine.py` builds the prompt.
- **Rationale:** Ground answers in repository text and fit a large repository into a limited model context.
- **Alternatives:** Full-repository prompting; lexical search only; fine-tuning; knowledge graph; agentic code navigation.
- **Pros:** Lower context cost than sending everything; repository-specific evidence; model can answer varied natural-language questions.
- **Cons:** Retrieval errors become answer errors; no citations or grounding verification; the UI’s “no hallucinations” claim is stronger than the implementation supports.
- **Cost/complexity:** Moderate conceptual and dependency cost, but a short linear implementation.
- **Maintainability:** Good module boundaries, weak contracts and no tests.
- **Performance:** Avoids huge prompts, but indexing is eager and repeated.
- **Honest critique:** Correct prototype architecture, incomplete trustworthy-RAG implementation.

### D2. A linear, synchronous indexing pipeline

- **Evidence:** `/analyze` clones, reads, chunks, embeds, indexes, and summarizes in one request.
- **Rationale:** Keep control flow obvious and return only when the repository is queryable.
- **Alternatives:** Background jobs; event-driven stages; workflow engine; streaming progress.
- **Pros:** Deterministic ordering; minimal infrastructure; simple local debugging.
- **Cons:** Long requests can time out; no progress, cancellation, retry, checkpoint, or partial recovery.
- **Cost/complexity:** Very low initial cost; high operational cost as repositories grow.
- **Maintainability:** Easy while stages stay small; cross-cutting timeout/error behavior will become tangled.
- **Performance:** Serializes independent work and occupies a web worker for the full analysis.
- **Honest critique:** Suitable only for small demos.

### D3. FastAPI as the backend boundary

- **Evidence:** `app/api.py` defines typed request models and three POST endpoints.
- **Rationale:** Lightweight Python API framework with automatic validation and documentation.
- **Alternatives:** Flask, Django, a Streamlit-only app, gRPC, CLI.
- **Pros:** Concise endpoints; Pydantic input parsing; clean separation from the UI.
- **Cons:** No response schemas, exception mapping, dependency injection, lifespan management, auth, or API versioning.
- **Cost/complexity:** Low.
- **Maintainability:** Framework choice scales well; current global state does not.
- **Performance:** Framework overhead is negligible relative to cloning, embeddings, and LLM calls; synchronous handlers can block workers.
- **Honest critique:** Strong framework choice used at prototype depth.

### D4. Streamlit as a separately running frontend

- **Evidence:** `frontend.py` posts to a fixed FastAPI URL.
- **Rationale:** Build an interactive Python UI quickly without a JavaScript toolchain.
- **Alternatives:** React/Next.js, server-rendered templates, FastAPI-hosted static UI, CLI.
- **Pros:** Rapid development; Python-only stack; native charts and status widgets.
- **Cons:** Limited application-state control; large inline CSS; backend URL is hard-coded; no timeout or network-exception handling.
- **Cost/complexity:** Very low prototype cost.
- **Maintainability:** A 481-line mixed CSS/UI/network module will become difficult to evolve.
- **Performance:** Fine for low concurrency; every interaction reruns Streamlit script logic.
- **Honest critique:** Excellent demo shell, weak long-term product frontend.

### D5. GitPython and local disk cloning

- **Evidence:** `repo_loader.py` calls `git.Repo.clone_from` into `data/<repo_name>`.
- **Rationale:** Preserve the repository tree and use Git’s mature transport behavior.
- **Alternatives:** GitHub archive/API, libgit2, shallow command-line clone, user upload.
- **Pros:** Simple; works for public Git URLs; local files support later analysis.
- **Cons:** Untrusted URL/large-repository risk; full clone cost; name collisions; stale clones are silently reused; no branch/commit selection, shallow clone, quota, cleanup, or private-repo auth.
- **Cost/complexity:** Low code cost, potentially high storage/network cost.
- **Maintainability:** Small wrapper, but lifecycle policy is absent.
- **Performance:** Full history may be downloaded unnecessarily.
- **Honest critique:** The largest security and resource-management gap at ingestion.

### D6. Repository identity derived from the URL’s last segment

- **Evidence:** URL splitting and `.git` removal determine `data/<name>`.
- **Rationale:** Human-readable, trivial cache key.
- **Alternatives:** Canonical owner/repo/commit key; URL hash; generated analysis ID.
- **Pros:** Easy to inspect.
- **Cons:** Forks and same-named repositories collide; query strings and trailing slashes can break naming; no path sanitization contract.
- **Cost/complexity:** Minimal now; migration cost later.
- **Maintainability:** Fragile implicit convention shared with `frontend.py`.
- **Performance:** Reuse avoids recloning, but may serve stale or wrong code.
- **Honest critique:** Convenience was chosen over correctness and isolation.

### D7. Extension allowlist for source discovery

- **Evidence:** `.py`, `.js`, `.ts`, `.java`, `.cpp`, and `.c` are accepted.
- **Rationale:** Avoid indexing every binary/generated file while covering common languages.
- **Alternatives:** Language detection; configurable include/exclude globs; Git-tracked files; parser registry.
- **Pros:** Cheap and predictable.
- **Cons:** Omits many languages and important config/docs; includes vendored/build directories; case-sensitive; conflicts with README’s “Python best results” framing.
- **Cost/complexity:** Very low.
- **Maintainability:** Central list is easy to edit but not extensible by users.
- **Performance:** Filtering is fast, but walking `.git`, virtual environments, and dependencies wastes I/O.
- **Honest critique:** A reasonable first filter without the ignore policy real repositories require.

### D8. Read whole files as UTF-8 and silently skip failures

- **Evidence:** `code_parser.py` uses `f.read()` and a bare `except`.
- **Rationale:** Simplify downstream chunking and tolerate unreadable files.
- **Alternatives:** Streaming reads; encoding detection; size limits; explicit error collection.
- **Pros:** Compact and resilient to a single bad file.
- **Cons:** Memory spikes, hidden permission/decoding/programming errors, no user-visible coverage report.
- **Cost/complexity:** Low implementation cost; high debugging cost.
- **Maintainability:** Bare exception handling masks regressions.
- **Performance:** Whole-file reads are acceptable only for bounded inputs.
- **Honest critique:** Fault tolerance without observability is silent data loss.

### D9. Fixed 500-character, non-overlapping chunks

- **Evidence:** `chunker.py` slices raw strings every 500 characters.
- **Rationale:** The simplest way to cap retrieval unit size.
- **Alternatives:** Token-aware overlap; AST/function/class chunks; line windows; language-specific splitting.
- **Pros:** Deterministic, language-agnostic, fast.
- **Cons:** Splits identifiers and syntax; loses line numbers and symbol boundaries; no overlap; character count does not map consistently to tokens.
- **Cost/complexity:** Minimal.
- **Maintainability:** Simple but quality improvements require a richer metadata model.
- **Performance:** Linear and cheap; may create more low-quality vectors/prompts than semantic chunking.
- **Honest critique:** This choice is the main retrieval-quality bottleneck.

### D10. Preserve only file path and chunk text

- **Evidence:** Chunk dictionaries have two fields.
- **Rationale:** Meet minimum retrieval and prompting needs.
- **Alternatives:** Add repository/commit, language, symbol, line span, chunk ID, hash, parent context.
- **Pros:** Small payload and straightforward code.
- **Cons:** No precise citations, incremental updates, deduplication, access control, or traceability.
- **Cost/complexity:** Low now; schema migration later.
- **Maintainability:** Untyped dictionaries invite key errors and contract drift.
- **Performance:** Small metadata footprint; lack of IDs prevents efficient update/delete.
- **Honest critique:** Under-modeled for a code intelligence system.

### D11. A module-global `all-MiniLM-L6-v2` embedder

- **Evidence:** `embedder.py` loads SentenceTransformer at import time.
- **Rationale:** Reuse one fast, compact local model with no embedding API fees.
- **Alternatives:** Code-specific models; hosted embeddings; lazy-loaded model; dependency-injected model.
- **Pros:** Low latency after startup; private local inference; widely used baseline; 384-dimensional compact vectors.
- **Cons:** Generic semantic model is not code-specialized; import/startup is heavy; model lifecycle/device/batching settings are implicit.
- **Cost/complexity:** No per-call vendor cost, but local CPU/RAM and package weight.
- **Maintainability:** Hard-coded model complicates experiments and upgrades.
- **Performance:** Good prototype throughput; CPU embedding blocks the request.
- **Honest critique:** Sensible baseline, not evidence-backed as best for code retrieval.

### D12. Eagerly embed all chunks in one model call

- **Evidence:** `model.encode(texts)` receives the complete list.
- **Rationale:** Let SentenceTransformers batch internally with minimal code.
- **Alternatives:** Bounded batches; async worker queue; incremental embedding/cache.
- **Pros:** Concise and often faster than one-by-one inference.
- **Cons:** Memory risk for large repositories; no progress or retry; an empty repository later crashes index creation.
- **Cost/complexity:** Low.
- **Maintainability:** Batching policy is absent rather than configurable.
- **Performance:** Efficient for small-to-medium inputs, unsafe when unbounded.
- **Honest critique:** Input limits are mandatory before exposing this publicly.

### D13. Exact in-memory FAISS `IndexFlatL2`

- **Evidence:** `vector_store.py` builds `faiss.IndexFlatL2`.
- **Rationale:** Exact nearest neighbors with no training or index-tuning complexity.
- **Alternatives:** Cosine/IP FAISS; HNSW/IVF/PQ; pgvector; Qdrant; Pinecone; Elasticsearch.
- **Pros:** Exact results; deterministic; simple; no external service.
- **Cons:** RAM-only, no metadata filtering/persistence, linear scan, single-process ownership.
- **Cost/complexity:** Minimal infrastructure and no service fees.
- **Maintainability:** Very easy at demo scale; operational features must be built around it.
- **Performance:** Excellent for small indexes; O(number of vectors) query work and full rebuilds.
- **Honest critique:** Right baseline, wrong destination for multi-tenant or large-scale use.

### D14. L2 distance without explicit vector normalization

- **Evidence:** Raw MiniLM outputs enter `IndexFlatL2`; no `normalize_embeddings=True`.
- **Rationale:** Likely FAISS tutorial simplicity, not a documented retrieval experiment.
- **Alternatives:** Normalize then inner product/cosine; learned reranking.
- **Pros:** Works mechanically and is easy to understand.
- **Cons:** Ranking includes embedding magnitude effects; semantic embedding guidance commonly uses cosine similarity.
- **Cost/complexity:** Tiny change to normalize, but relevance must be evaluated.
- **Maintainability:** Hidden metric assumption.
- **Performance:** Exact L2 is fast; normalization adds negligible indexing cost.
- **Honest critique:** Retrieval metric should be an evaluated configuration, not an accident.

### D15. Fixed top-5 retrieval with no threshold or reranker

- **Evidence:** `retrieve(..., top_k=5)` and all returned indices are accepted.
- **Rationale:** Bound prompt size and keep behavior predictable.
- **Alternatives:** Dynamic K; score threshold; lexical/vector hybrid; cross-encoder reranking; diversity selection.
- **Pros:** Simple latency and prompt-budget bound.
- **Cons:** Always returns five even when irrelevant; ignores distances; can duplicate adjacent fragments; FAISS `-1` sentinels can index the last chunk when fewer than five vectors exist.
- **Cost/complexity:** Minimal now; reranking adds inference latency.
- **Maintainability:** Hard-coded policy is difficult to tune.
- **Performance:** Search is cheap, but low-quality context wastes LLM tokens.
- **Honest critique:** Contains a concrete small-index correctness bug and no quality controls.

### D16. Hosted Groq chat completion with hard-coded Llama model

- **Evidence:** `llama-3.3-70b-versatile`, temperature `0.2`.
- **Rationale:** Fast hosted generation and relatively deterministic technical answers.
- **Alternatives:** OpenAI/Anthropic; local model; provider abstraction; configurable model routing.
- **Pros:** Strong model capability without hosting GPUs; low temperature reduces variation.
- **Cons:** Vendor/network/key dependency; model availability can change; no timeout, retry, rate-limit handling, cost tracking, or structured output.
- **Cost/complexity:** Low infrastructure cost; variable external usage cost and data-governance implications.
- **Maintainability:** Provider details leak into core QA logic.
- **Performance:** Network and generation dominate query latency.
- **Honest critique:** Fine for a demo; enterprise use needs policy, resilience, and abstraction.

### D17. One user prompt containing retrieved code and question

- **Evidence:** Context and instructions are interpolated into one user message.
- **Rationale:** Minimal prompting sufficient to generate an explanation.
- **Alternatives:** System policy plus delimited evidence; structured citations; tool calling; map-reduce synthesis.
- **Pros:** Transparent and short.
- **Cons:** Repository text can contain prompt injection; no explicit “say unknown,” citation requirement, token budget, or evidence ordering; HTML can later render unsafely in Streamlit.
- **Cost/complexity:** Low.
- **Maintainability:** Prompt is hard-coded and unversioned.
- **Performance:** Concatenates all five chunks regardless of relevance.
- **Honest critique:** The prompt does not justify the product claim of hallucination-free answers.

### D18. One process-wide mutable pipeline

- **Evidence:** `pipeline = {}` stores the latest index, chunks, and summary.
- **Rationale:** Share analysis state between `/analyze` and `/ask` without a database.
- **Alternatives:** Analysis IDs and persistent store; per-session state; dependency-managed cache.
- **Pros:** Extremely simple and fast.
- **Cons:** Last writer wins; users can query another user’s repository; restart loses state; multiple workers have divergent state; asking before analysis raises a server error.
- **Cost/complexity:** Lowest prototype cost, severe correctness/security cost.
- **Maintainability:** Global coupling hinders testing and concurrency.
- **Performance:** Fast single-user access; no safe horizontal scaling.
- **Honest critique:** The central blocker to production deployment.

### D19. Separate `/analyze`, `/ask`, and `/architecture` POST endpoints

- **Evidence:** Three action-oriented endpoints.
- **Rationale:** Reflect user workflow and isolate optional architecture work.
- **Alternatives:** Resource-oriented analyses with IDs and status; GraphQL; one composite endpoint.
- **Pros:** Easy UI integration and API discovery.
- **Cons:** `/ask` has no repository/analysis identifier; `/architecture` reclones/checks disk separately; POST is used for a read-like architecture operation because the URL is in a body.
- **Cost/complexity:** Low.
- **Maintainability:** Endpoint contracts will need breaking changes for multi-tenancy.
- **Performance:** Architecture can repeat repository access.
- **Honest critique:** API shape exposes the global-state assumption.

### D20. Minimal Pydantic request validation

- **Evidence:** Both fields are unrestricted strings.
- **Rationale:** Type validation with minimal ceremony.
- **Alternatives:** URL type, schemes/host allowlist, length limits, normalized repository locator, question constraints.
- **Pros:** Rejects missing/non-string fields.
- **Cons:** Empty, malformed, local-network, oversized, and unsupported inputs pass the schema.
- **Cost/complexity:** Low to improve.
- **Maintainability:** Explicit validators would centralize policy.
- **Performance:** Validation would prevent expensive invalid work.
- **Honest critique:** Type checking is not security validation.

### D21. Python AST import extraction for architecture

- **Evidence:** `architecture.py` parses only `.py` files and collects `Import`/`ImportFrom`.
- **Rationale:** Standard-library static analysis is safer and more accurate than regex for Python imports.
- **Alternatives:** Tree-sitter; language servers; dependency manifests; runtime tracing; semantic call graph.
- **Pros:** No code execution; handles standard Python syntax; easy to explain.
- **Cons:** Only imports, not calls/data flow; file basenames can collide; edges point to module strings rather than resolved files; syntax errors are silently omitted.
- **Cost/complexity:** Low.
- **Maintainability:** Clear isolated module, limited extensibility.
- **Performance:** Linear parse cost and generally fast.
- **Honest critique:** It is an import listing visualized as a dependency graph, not a full architecture model.

### D22. NetworkX and Matplotlib graph visualization

- **Evidence:** Both backend helper and frontend construct directed graphs; frontend renders a Matplotlib figure.
- **Rationale:** Familiar Python graph and plotting libraries.
- **Alternatives:** PyVis, Graphviz, Cytoscape, D3, textual graph.
- **Pros:** Quick static visualization; no frontend JavaScript.
- **Cons:** Labels overlap at modest scale; isolated files disappear because nodes are added only through edges; visualization logic is duplicated; `plt.show()` is server-hostile.
- **Cost/complexity:** Low development cost, sizable dependencies.
- **Maintainability:** Duplicate rendering paths can diverge.
- **Performance:** Layout becomes expensive and unreadable for large graphs.
- **Honest critique:** Demo visualization, not an architecture exploration UX.

### D23. A lightweight repository summary via filesystem walk

- **Evidence:** Counts every file, infers four languages, and reports first five Python filenames.
- **Rationale:** Give immediate, cheap feedback after indexing.
- **Alternatives:** Git-tracked file statistics; Linguist; parser-derived modules; richer metrics.
- **Pros:** Simple and fast enough for small trees.
- **Cons:** Counts `.git` and non-source files; language list order is nondeterministic; `.c/.cpp` are indexed but not reported; “main modules” means first traversal entries, not importance.
- **Cost/complexity:** Very low.
- **Maintainability:** Logic is easy to replace.
- **Performance:** Adds a second full tree walk.
- **Honest critique:** Labels overstate the semantic meaning of the data.

### D24. Recompute the dependency graph in the frontend

- **Evidence:** After `/analyze`, Streamlit derives a local path and calls `build_dependency_graph` directly instead of `/architecture`.
- **Rationale:** Avoid another HTTP call and reuse local code in a co-located demo.
- **Alternatives:** Backend returns graph; frontend calls architecture endpoint; background analysis artifact.
- **Pros:** Works when UI and API share one filesystem.
- **Cons:** Breaks deployment separation; duplicates path derivation; ignores `.git` stripping differences; bypasses backend ownership.
- **Cost/complexity:** Low local cost, high deployment coupling.
- **Maintainability:** Two sources of truth.
- **Performance:** Additional parse pass after indexing.
- **Honest critique:** Contradicts the intended frontend/backend boundary.

### D25. Extensive inline HTML/CSS and unsafe HTML rendering

- **Evidence:** Streamlit receives large `unsafe_allow_html=True` blocks, including an interpolated LLM answer.
- **Rationale:** Achieve a distinctive UI beyond standard Streamlit components.
- **Alternatives:** Native components; separate stylesheet/component; a conventional web frontend; sanitize dynamic HTML.
- **Pros:** Strong visual identity with rapid iteration.
- **Cons:** CSS depends on Streamlit internals; accessibility/responsiveness are only partially handled; dynamic answer HTML creates an injection/XSS risk.
- **Cost/complexity:** Low initial, growing maintenance and security cost.
- **Maintainability:** Styling and behavior are monolithic.
- **Performance:** Large CSS is tolerable, remote fonts add network dependency.
- **Honest critique:** Static markup is acceptable; unescaped model output must not be injected as HTML.

### D26. Environment-based API key loaded at import

- **Evidence:** `load_dotenv()` and `GROQ_API_KEY` initialize the client globally.
- **Rationale:** Keep secrets out of source and support local `.env`.
- **Alternatives:** Secret manager; runtime dependency; explicit application settings.
- **Pros:** Standard twelve-factor direction; easy local setup.
- **Cons:** Missing key fails late/unclearly; no startup validation or key rotation; global client complicates tests.
- **Cost/complexity:** Very low.
- **Maintainability:** A typed settings layer would scale better.
- **Performance:** Reusing the client is efficient.
- **Honest critique:** Correct secret location, incomplete configuration management.

### D27. Broad exception suppression and default framework errors

- **Evidence:** Bare `except` in file and AST parsing; endpoint calls are otherwise unguarded.
- **Rationale:** Continue analysis when individual files fail while avoiding boilerplate.
- **Alternatives:** Typed exceptions, structured warnings, partial-result report, centralized handlers.
- **Pros:** One malformed source file need not stop a scan.
- **Cons:** Diagnostic information disappears; clone, empty index, missing state, provider, and filesystem errors become generic 500 responses.
- **Cost/complexity:** Low initial, expensive support/debugging.
- **Maintainability:** Makes regressions hard to detect.
- **Performance:** Not material.
- **Honest critique:** Error policy is inconsistent: some failures vanish and others crash the request.

### D28. No persistence, cache invalidation, authentication, observability, or tests

- **Evidence:** No corresponding implementation is present.
- **Rationale:** Keep a learning project focused on the happy-path RAG pipeline.
- **Alternatives:** Persistent analysis records, content hashes, auth/RBAC, metrics/tracing/logging, unit/integration/evaluation suites.
- **Pros:** Small codebase and low setup burden.
- **Cons:** No durability, isolation, reproducibility, quality measurement, regression safety, or production diagnosis.
- **Cost/complexity:** These capabilities are substantial, but deferring all of them compounds redesign risk.
- **Maintainability:** Current changes cannot be validated automatically.
- **Performance:** No measurements exist; optimization claims would be speculative.
- **Honest critique:** The repository is a portfolio prototype, not yet a dependable service.

## Cross-cutting assessment

### What is well chosen

The module-per-stage decomposition, FastAPI/Streamlit speed of development, local SentenceTransformer, exact FAISS baseline, and AST rather than regex are coherent choices for teaching a RAG pipeline. The code is short enough that a reviewer can trace a request end-to-end.

### What must be defended carefully

Do not claim “any repository,” “large codebases,” “no hallucinations,” production scalability, or a complete dependency graph. The implementation supports selected extensions, a single active in-memory analysis, simplistic retrieval, and Python-only import extraction.

### Highest-risk debt

1. Untrusted repository cloning without limits or network policy.
2. Cross-user leakage and last-writer-wins global state.
3. Unsanitized LLM answer rendered as HTML.
4. Unbounded memory/CPU/disk work.
5. Retrieval without evaluation, score filtering, robust chunk metadata, or citations.

## Beginner

### Question: Why does this project split repository text into chunks?

**Ideal Answer:** Embedding and prompting an entire repository is often too large and too imprecise. Chunks create searchable units so the system can retrieve a small amount of likely relevant code. Here the chunks are fixed 500-character slices, which is simple but can break functions and should evolve toward token- and syntax-aware chunks.

**Why asked:** Tests whether the candidate understands the basic RAG decomposition and can distinguish purpose from implementation quality.

**Common mistakes:** Saying chunking eliminates hallucinations; confusing characters with tokens; claiming chunks preserve function boundaries.

**Follow-ups:** Why add overlap? What metadata should a chunk carry? How would chunk size affect recall and prompt cost?

## Intermediate

### Question: Why is `IndexFlatL2` reasonable here, and when would you replace it?

**Ideal Answer:** It is training-free, exact, deterministic, and operationally trivial, which is ideal for a small prototype. I would replace or augment it when vectors no longer fit comfortably in memory, exact linear scans miss latency targets, metadata filtering or persistence is required, or multiple service instances need shared state. I would first benchmark normalized cosine/IP and establish retrieval metrics.

**Why asked:** Evaluates whether the candidate can tie a data structure to scale and product requirements.

**Common mistakes:** Calling FAISS a persistent vector database; assuming approximate search is always faster overall; proposing migration without measurements.

**Follow-ups:** Compare Flat, IVF, HNSW, and PQ. How would you estimate memory? How would you validate recall after migration?

## Advanced

### Question: Identify the concurrency failure in the current API and redesign it.

**Ideal Answer:** The module-global `pipeline` stores only the latest analysis. Concurrent analyses race, every user’s `/ask` accesses whichever index was written last, multi-worker processes disagree, and restarts erase state. I would return an immutable analysis ID, key artifacts by tenant/repository/commit/model/chunker version, persist metadata and index location, require that ID on queries, use background jobs with explicit states, and enforce authorization at every lookup.

**Why asked:** Tests state ownership, distributed-system reasoning, and security awareness.

**Common mistakes:** Adding a lock and calling the problem solved; using user sessions without durable shared storage; ignoring worker/process boundaries.

**Follow-ups:** How would you make indexing idempotent? What consistency is required? How do you garbage-collect artifacts?

## FAANG

### Question: Design this analyzer for millions of repositories while preserving answer provenance.

**Ideal Answer:** Separate ingestion, artifact storage, indexing, retrieval, and generation. Canonicalize repository plus commit identity; process Git objects with quotas in isolated workers; emit syntax-aware chunks with immutable IDs and line spans; cache embeddings by content hash and model version; shard a filtered hybrid index; retrieve, rerank, and diversify evidence; require answers to cite chunk IDs; verify citation entailment; store prompt/model/index versions; and expose SLOs for indexing freshness, retrieval recall, grounded-answer rate, latency, cost, and tenant isolation. Use queues, backpressure, retries, dead-letter handling, and regional data-governance controls.

**Why asked:** Assesses architecture under scale, reliability, security, cost, and ML-quality constraints.

**Common mistakes:** Focusing only on a larger vector database; omitting commit/version provenance; treating LLM quality as unmeasurable; ignoring abusive repositories.

**Follow-ups:** What is the partition key? How do you handle monorepos? How do you roll out a new embedding model without downtime?

## Follow-up

### Question: What single change most improves answer trustworthiness?

**Ideal Answer:** There is no universal single fix, but the highest-leverage product change is evidence-backed answers with stable file/line citations plus an explicit abstention path, measured by a grounded-answer evaluation set. Better chunk metadata enables this; score thresholds and reranking improve the evidence supplied. Security isolation is separately non-negotiable.

**Why asked:** Forces prioritization while recognizing that “quality” has multiple failure modes.

**Common mistakes:** Answering only “use a bigger model”; promising zero hallucinations; ignoring measurement.

**Follow-ups:** Define grounded-answer rate. How do you test citation correctness? What should the UI show when evidence is weak?

## Trick

### Question: Does low temperature guarantee that answers are factual?

**Ideal Answer:** No. Temperature mainly changes sampling variability. A low temperature can make the same unsupported answer more repeatable. Factuality depends on evidence quality, prompt constraints, model behavior, citation verification, and abstention/evaluation—not temperature alone.

**Why asked:** Detects superficial LLM configuration knowledge.

**Common mistakes:** Saying temperature zero prevents hallucination; equating determinism with correctness.

**Follow-ups:** Why might outputs still vary at temperature zero? Which evaluations would expose unsupported answers?
