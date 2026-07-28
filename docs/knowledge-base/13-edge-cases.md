# Chapter 13 — Edge Cases and Failure Semantics

## Scope and evidence

This chapter documents the behavior of the code as it exists today. It is not a claim that the current behavior is safe for production. Each case records:

- **Current behavior:** what the checked-in implementation does.
- **Root cause:** the exact design or implementation choice behind it.
- **Ideal handling:** a production-oriented target.
- **Tests:** checks that should lock in the target behavior.
- **User impact:** what a user or operator experiences.

The relevant execution path is `frontend.py` → `app/api.py` → repository loading, parsing, chunking, embedding, FAISS retrieval, and Groq generation. The API is synchronous and stores one mutable process-wide `pipeline` dictionary.

## Edge-case catalog

### 1. Empty repository URL

- **Current behavior:** the frontend sends `{"repo_url": ""}`. `clone_repository` derives an empty repository name and resolves the target to `data/`. Because that directory normally exists, it returns it as an “already existing” repository. The analyzer may then index whatever repositories already exist beneath `data/`, not an empty input. If no supported files exist, embedding or index construction fails.
- **Root cause:** neither Pydantic nor the frontend validates URL syntax or non-emptiness; repository identity is inferred with string splitting.
- **Ideal handling:** reject before cloning with HTTP 422 and a stable code such as `INVALID_REPOSITORY_URL`; disable the frontend action while input is empty.
- **Tests:** API test for blank and whitespace-only values; unit tests for URL normalization; UI test asserting no request is sent.
- **User impact:** misleading success, accidental analysis of unrelated local data, or an opaque server error.

### 2. Malformed, unsupported, or non-Git URL

- **Current behavior:** `git.Repo.clone_from` raises an exception. FastAPI converts the unhandled exception to a generic HTTP 500; the frontend displays only “Failed to analyze repository.”
- **Root cause:** no URL allowlist, parser, exception translation, or structured error response.
- **Ideal handling:** accept only explicit schemes and supported hosts, normalize the URL, catch GitPython errors, and return 400/422 with actionable text.
- **Tests:** malformed URL, FTP URL, local path, SCP-style Git URL, and valid HTTPS Git URL.
- **User impact:** users cannot tell whether the URL, permissions, network, or server is at fault.

### 3. Private repository

- **Current behavior:** cloning fails unless ambient Git credentials happen to be available to the server process. There is no token field or provider integration.
- **Root cause:** the request model contains only `repo_url`; credentials and ownership boundaries are not modeled.
- **Ideal handling:** either explicitly support public repositories only or add a short-lived, encrypted credential flow with provider-scoped tokens, redaction, audit logging, and immediate disposal.
- **Tests:** private repository without credentials, invalid token, valid read-only token, and log-redaction assertions.
- **User impact:** unexplained failure today; careless future support could leak valuable source code or tokens.

### 4. Repository URL ending in slash or query/fragment

- **Current behavior:** a trailing slash produces an empty `repo_name`; query strings and fragments become part of the local name. `.git` is removed with a broad string replacement rather than suffix handling.
- **Root cause:** `repo_url.split("/")[-1].replace(".git", "")` is not URL parsing.
- **Ideal handling:** use a URL parser, strip trailing slashes, reject unexpected query/fragment components, and derive a sanitized canonical repository identifier.
- **Tests:** trailing slash, `.git`, `.git/`, query string, fragment, percent encoding, Unicode, and repeated separators.
- **User impact:** wrong cache hits, invalid paths, or analysis of the entire `data/` directory.

### 5. Repository-name collision

- **Current behavior:** two URLs whose final path component is the same share the same `data/<name>` directory. The second request silently reuses the first clone.
- **Root cause:** local identity excludes owner, host, and revision; existence is treated as proof of correctness.
- **Ideal handling:** key storage by canonical host/owner/name plus revision or a URL hash; verify the existing clone’s remote before reuse.
- **Tests:** same repository name under two owners and two hosts; assert isolated content and indexes.
- **User impact:** confidently wrong summaries and answers sourced from another repository.

### 6. Existing clone is stale

- **Current behavior:** an existing directory is returned without fetch, pull, branch validation, or commit comparison.
- **Root cause:** the loader is a clone-once cache with no freshness policy.
- **Ideal handling:** let users select a commit, tag, or branch; fetch safely; record the resolved commit SHA in every analysis.
- **Tests:** update remote after first analysis, analyze again, and verify either refresh or explicit immutable-cache semantics.
- **User impact:** answers may describe old code while appearing current.

### 7. Existing path is not a Git repository

- **Current behavior:** any existing path is accepted, even if it is a normal directory, partial clone, or corrupted checkout.
- **Root cause:** `os.path.exists` is the only cache validation.
- **Ideal handling:** verify a valid Git worktree and matching origin; quarantine or rebuild corrupt entries.
- **Tests:** plain directory, missing `.git`, interrupted clone, and mismatched origin.
- **User impact:** partial or unrelated files are indexed without warning.

### 8. Clone interrupted midway

- **Current behavior:** GitPython raises. A partially created directory may remain; the next request can treat it as a completed repository.
- **Root cause:** cloning occurs directly into the final path with no transactional rename or cleanup.
- **Ideal handling:** clone to a unique temporary directory, validate checkout, then atomically rename; delete temporary data on failure.
- **Tests:** injected network interruption and disk-full conditions, followed by a retry.
- **User impact:** one transient failure can poison all later attempts for that repository name.

### 9. Branch, tag, commit, submodule, and Git LFS semantics

- **Current behavior:** the default branch is cloned. There is no revision selection. Git submodules are not initialized explicitly, and LFS behavior depends on local Git configuration.
- **Root cause:** `clone_from` receives only URL and destination.
- **Ideal handling:** make revision explicit, resolve and report SHA, define submodule/LFS policy, cap checkout size, and surface omitted content.
- **Tests:** non-default branch, detached commit, nested submodule, missing LFS client, and oversized LFS object.
- **User impact:** analysis can omit important code with no indication.

### 10. Huge repository

- **Current behavior:** the whole checkout is walked, all supported files are read fully, all chunks are accumulated, embeddings are generated in one call, and a flat in-memory FAISS index is built.
- **Root cause:** no file, byte, chunk, duration, memory, or concurrency limits; no streaming or background job.
- **Ideal handling:** preflight size, enforce quotas, ignore generated/vendor directories, stream bounded batches, persist progress, and allow cancellation.
- **Tests:** repositories at configured boundaries, memory profiling, timeout, cancellation, and rejection above quota.
- **User impact:** long requests, out-of-memory termination, server-wide outage, and unpredictable model cost.

### 11. Empty repository or no supported source files

- **Current behavior:** `load_code_files` returns an empty list, `chunk_code` returns no chunks, model encoding may return an empty result, and `build_index` attempts `embeddings[0]`, usually raising `IndexError`.
- **Root cause:** index construction assumes at least one embedding.
- **Ideal handling:** return a successful analysis with zero indexable files plus a clear warning, and make `/ask` unavailable for that analysis.
- **Tests:** empty repository; Markdown-only repository; repository containing only unsupported languages.
- **User impact:** a valid repository appears broken.

### 12. Empty source files

- **Current behavior:** a zero-length file contributes no chunk because `range(0, 0, 500)` is empty, but it is still included in the summary’s total file count and may appear as a Python main module.
- **Root cause:** summary and indexability use different definitions of “file.”
- **Ideal handling:** expose total, supported, indexed, skipped, and empty-file counts separately.
- **Tests:** mix empty and non-empty supported files; assert internally consistent metrics.
- **User impact:** totals look plausible but do not explain what was actually searchable.

### 13. Unsupported languages and file naming

- **Current behavior:** only `.py`, `.js`, `.ts`, `.java`, `.cpp`, and `.c` are indexed, with case-sensitive suffix checks. JSX, TSX, Go, Rust, C#, Kotlin, notebooks, templates, configuration, and uppercase suffixes are ignored.
- **Root cause:** a small fixed extension list.
- **Ideal handling:** configurable language detection, explicit skipped-language reporting, and parsers appropriate to each language.
- **Tests:** every supported extension, uppercase variants, extensionless scripts, `.d.ts`, `.tsx`, and generated files.
- **User impact:** users may ask about code that was silently excluded.

### 14. Binary, non-UTF-8, permission-denied, and disappearing files

- **Current behavior:** any read exception is swallowed by a bare `except`; the file is skipped silently.
- **Root cause:** broad exception suppression and no diagnostics collection.
- **Ideal handling:** catch expected exceptions individually, continue safely, and return redacted skipped-file reasons and counts.
- **Tests:** invalid UTF-8, unreadable file, symlink race, deleted file, and a binary file with a supported suffix.
- **User impact:** incomplete analysis is presented as complete.

### 15. Symlinks and path escape

- **Current behavior:** `os.walk` does not follow directory symlinks by default, but a supported file symlink can be opened and may point outside the checkout.
- **Root cause:** no resolved-path containment check.
- **Ideal handling:** reject any file whose resolved path is outside the repository root; define a safe symlink policy.
- **Tests:** file symlink inside root, file symlink outside root, broken link, and directory loop.
- **User impact:** unintended local files or secrets could be embedded and sent to downstream services.

### 16. Generated, vendored, dependency, and secret files

- **Current behavior:** all matching extensions beneath the checkout are indexed, including vendored dependencies, build outputs, minified code, tests, and supported-suffix secret files. `.gitignore` is not consulted by the walker.
- **Root cause:** there is no exclusion policy or secret scanning.
- **Ideal handling:** apply default and repository-specific ignores, detect minified/generated content, run secret redaction before embedding or prompting, and report exclusions.
- **Tests:** `node_modules`, virtual environments, build directories, ignored files, minified bundles, and seeded canary secrets.
- **User impact:** poor relevance, higher latency/cost, and potential exfiltration of secrets to embedding or LLM providers.

### 17. Very long line, huge file, and Unicode text

- **Current behavior:** files are split every 500 Python characters, regardless of lines, tokens, functions, grapheme clusters, or model limits. Unicode is accepted if UTF-8, but boundaries can separate combining sequences and semantic units.
- **Root cause:** fixed character slicing.
- **Ideal handling:** impose per-file limits, preserve source offsets, use syntax/token-aware chunks with overlap, and normalize Unicode only when semantically safe.
- **Tests:** million-character line, emoji and combining characters, CJK text, large generated file, and exact boundary assertions.
- **User impact:** broken snippets reduce retrieval quality and can make answers misleading.

### 18. Function or statement crosses a chunk boundary

- **Current behavior:** related definitions are arbitrarily split with no overlap; path is the only metadata.
- **Root cause:** chunking is not syntax-aware.
- **Ideal handling:** chunk by symbol/AST where possible, retain line ranges and symbol names, and add bounded overlap.
- **Tests:** function beginning at character 490, long class, nested function, and multi-file comparison question.
- **User impact:** the retriever may return only half the logic, causing an incomplete explanation.

### 19. Empty or whitespace-only question

- **Current behavior:** it is embedded and searched; the top five chunks are sent to Groq with an empty question.
- **Root cause:** `QuestionRequest.question` has no length or content constraint.
- **Ideal handling:** HTTP 422 for blank questions; client-side disablement; reasonable maximum length.
- **Tests:** empty, spaces, newline-only, and over-limit question.
- **User impact:** wasted latency and model spend, followed by a low-value answer.

### 20. Asking before analysis

- **Current behavior:** `/ask` indexes `pipeline["index"]` and `pipeline["chunks"]`; absent keys raise `KeyError`, yielding HTTP 500. The frontend converts this to a generic message.
- **Root cause:** implicit global state and no readiness check.
- **Ideal handling:** require an `analysis_id`, return 409 `ANALYSIS_NOT_READY`, and expose job/readiness status.
- **Tests:** ask on fresh process, after failed analysis, and while analysis is running.
- **User impact:** a normal workflow error looks like a server defect.

### 21. Concurrent analyses

- **Current behavior:** multiple requests perform expensive work concurrently and eventually overwrite the same global `pipeline`. Assignments to chunks and index occur separately, so another request can observe a mismatched index/chunk pair.
- **Root cause:** one mutable dictionary without locks, immutable snapshots, tenant keys, or job isolation.
- **Ideal handling:** each analysis gets an immutable ID and isolated persisted artifacts; atomically publish readiness.
- **Tests:** barrier-controlled interleaving of two analyses and concurrent asks; assert no cross-repository retrieval.
- **User impact:** one user can receive code or answers from another user’s repository, a severe correctness and confidentiality issue.

### 22. Multiple workers, reload, restart, and autoscaling

- **Current behavior:** the pipeline exists only in one Python process. Uvicorn reload restarts it; multi-worker deployments and multiple replicas each have unrelated state. A request routed to a different process fails or uses another index.
- **Root cause:** process memory is used as the database.
- **Ideal handling:** persist analysis metadata and index artifacts in shared storage, or apply intentional session affinity only as a temporary constraint.
- **Tests:** analyze on worker A and ask on worker B; restart between calls; scale replicas from one to two.
- **User impact:** intermittent failures that appear random under production routing.

### 23. An analysis fails after a prior success

- **Current behavior:** old global state remains if failure occurs before replacement. A subsequent ask can answer from the previous repository even though the latest analysis failed.
- **Root cause:** no state lifecycle, invalidation, or association between UI input and pipeline contents.
- **Ideal handling:** isolate jobs and require explicit analysis IDs; failed jobs must never alias earlier artifacts.
- **Tests:** successful analysis A, failed analysis B, then ask using B; expect a B-specific failure.
- **User impact:** silently wrong and potentially cross-user answers.

### 24. Fewer than five chunks

- **Current behavior:** FAISS can return `-1` for unfilled neighbors. Python treats `chunks[-1]` as the last chunk, so it may be duplicated in retrieved context.
- **Root cause:** retrieval does not clamp `top_k` or filter negative/out-of-range indices.
- **Ideal handling:** search `min(top_k, index.ntotal)` and validate every returned index.
- **Tests:** indexes containing zero through six vectors; assert uniqueness and no negative-index lookup.
- **User impact:** repetitive context reduces answer quality and consumes prompt tokens.

### 25. Wrong FAISS input type, shape, or metric assumptions

- **Current behavior:** embeddings are converted with `np.array` without explicitly enforcing contiguous `float32`; query shape relies on `model.encode([query])`. Retrieval uses raw L2 distance with no normalization.
- **Root cause:** implicit library defaults and no contract validation.
- **Ideal handling:** validate dimensions, coerce contiguous `float32`, document metric choice, and consider normalized vectors with cosine/IP based on retrieval evaluation.
- **Tests:** float64, wrong dimension, one-dimensional query, NaN/Inf, and deterministic nearest-neighbor fixtures.
- **User impact:** runtime errors or lower-quality retrieval after model/library changes.

### 26. Embedding model unavailable or cold

- **Current behavior:** `SentenceTransformer` is constructed during module import. Startup can block while downloading/loading; failure prevents the API from importing.
- **Root cause:** eager global initialization with no health/readiness distinction.
- **Ideal handling:** package/cache the model, initialize through a managed lifecycle, expose readiness, and fail with an operator-visible dependency error.
- **Tests:** empty model cache without network, corrupt cache, low memory, and concurrent first use.
- **User impact:** the whole service is unavailable before it can return a useful diagnostic.

### 27. Groq key missing or invalid

- **Current behavior:** a Groq client is built from the environment during import. Missing or invalid credentials can fail at startup or on generation, depending on SDK behavior. Errors are unhandled.
- **Root cause:** no startup configuration validation or dependency error mapping.
- **Ideal handling:** validate required secrets at startup, never log values, and return 503 for downstream authentication/configuration failure.
- **Tests:** absent, empty, invalid, rotated, and revoked key; verify redaction.
- **User impact:** opaque outage and possible accidental secret exposure during debugging.

### 28. Groq timeout, rate limit, outage, and malformed response

- **Current behavior:** the synchronous call has no application-level retry, timeout policy, circuit breaker, fallback, or response validation. Exceptions produce HTTP 500.
- **Root cause:** direct SDK invocation in the request path.
- **Ideal handling:** bounded timeout, jittered retries only for safe transient errors, rate-limit mapping, circuit breaker, budget enforcement, cancellation, and clear 429/502/503 semantics.
- **Tests:** timeout, 429 with retry hint, 500, connection reset, empty choices, and slow response.
- **User impact:** requests hang or fail unpredictably; retries by users can amplify load and cost.

### 29. Prompt injection in repository text

- **Current behavior:** retrieved source is inserted verbatim into a prompt. Comments or strings can instruct the model to ignore the user or reveal unrelated context.
- **Root cause:** untrusted repository text and trusted instructions share one unstructured user message.
- **Ideal handling:** frame repository content as untrusted data, use strong delimiters and system-level policy, limit tool capabilities, filter secrets, and evaluate injection resistance. No prompt-only defense is perfect.
- **Tests:** adversarial comments asking for secret disclosure, instruction override, fabricated answer, and data exfiltration.
- **User impact:** manipulated answers and possible disclosure of retrieved content.

### 30. HTML/script content in model output or repository metadata

- **Current behavior:** the answer is inserted into `st.markdown(..., unsafe_allow_html=True)`. Module names and summary values are also interpolated into unsafe HTML.
- **Root cause:** unescaped untrusted content is rendered with HTML enabled.
- **Ideal handling:** render answers as escaped Markdown/text, sanitize any required HTML with a strict allowlist, and escape metadata.
- **Tests:** model output and filenames containing `<script>`, event handlers, malformed tags, Markdown links, and HTML entities.
- **User impact:** cross-site scripting or UI corruption, depending on Streamlit’s sanitizer and runtime behavior; relying on framework sanitization alone is unsafe.

### 31. Architecture analysis on malformed Python

- **Current behavior:** parse errors are swallowed and the file is omitted from the graph. Read/decode errors occur outside the `try` and can fail the endpoint or frontend rendering.
- **Root cause:** only `ast.parse` is guarded, with a bare exception and no skipped-file diagnostics.
- **Ideal handling:** report syntax/read failures separately; continue when safe; preserve qualified relative paths.
- **Tests:** syntax error, encoding error, unreadable file, generated Python, and modern syntax unsupported by the runtime.
- **User impact:** an incomplete graph appears authoritative or the entire analysis fails.

### 32. Duplicate basenames in dependency graph

- **Current behavior:** graph keys use `file` rather than relative path. `pkg_a/utils.py` and `pkg_b/utils.py` overwrite one another.
- **Root cause:** basename is used as module identity.
- **Ideal handling:** key nodes by repository-relative module path and resolve imports to internal modules where possible.
- **Tests:** duplicate basenames, packages, namespace packages, relative imports, aliases, and imports inside functions.
- **User impact:** incorrect architecture diagrams and lost modules.

### 33. Empty dependency graph and graph size

- **Current behavior:** an empty graph is still plotted. A large graph is drawn synchronously with labels and fixed node size, which can be slow and unreadable.
- **Root cause:** visualization has no empty-state, cap, aggregation, or layout policy.
- **Ideal handling:** show an empty-state explanation; aggregate by package; cap or paginate nodes; move expensive layouts off the request/UI path.
- **Tests:** zero nodes, isolated files, dense graphs, thousands of modules, and cyclic imports.
- **User impact:** blank output, frozen UI, or unusable diagrams.

### 34. Repository summary inaccuracies

- **Current behavior:** `total_files` counts every file including `.git` contents and binaries. Languages recognize only four suffixes, while the parser supports C/C++. `main_modules` is simply the first five Python basenames encountered, with nondeterministic walk ordering.
- **Root cause:** summary logic is independent from parser policy and uses no stable sorting or “main” heuristic.
- **Ideal handling:** centralize language policy, exclude internal/generated files, sort deterministically, and name the field `sample_python_files` unless importance is actually calculated.
- **Tests:** stable ordering, Git metadata exclusion, C/C++ reporting, mixed languages, and duplicate names.
- **User impact:** misleading metrics reduce trust in the analysis.

### 35. Frontend backend unavailable, timeout, or non-JSON response

- **Current behavior:** `requests.post` has no timeout and is not inside `try/except`. Connection failures, timeouts, and JSON decoding errors can crash the Streamlit interaction.
- **Root cause:** frontend assumes the local API is always reachable and well-formed.
- **Ideal handling:** explicit connect/read timeouts, exception handling, request IDs, retry guidance, and environment-configurable API URL.
- **Tests:** refused connection, delayed response, HTML 500 body, invalid JSON, and connection reset.
- **User impact:** indefinite spinner or a raw Streamlit exception.

### 36. Production host configuration

- **Current behavior:** the frontend always calls `http://127.0.0.1:8000`. In separate containers, pods, or remote browsers, that address may not reach the backend.
- **Root cause:** hard-coded development endpoint.
- **Ideal handling:** inject a validated backend base URL, or serve UI and API behind one origin/reverse proxy.
- **Tests:** separate containers, non-default port, TLS origin, and path-prefix deployment.
- **User impact:** a seemingly healthy production UI cannot analyze or answer.

### 37. `run.sh` lifecycle and port conflicts

- **Current behavior:** Uvicorn starts in the background with reload enabled; Streamlit remains foreground. There is no `set -e`, readiness check, cleanup trap, configurable port, or propagation if the backend dies. Existing port use causes one component to fail.
- **Root cause:** the script is a convenience launcher, not a process supervisor.
- **Ideal handling:** keep it development-only; validate prerequisites, trap signals, clean up both children, and detect readiness. Use a real orchestrator in production.
- **Tests:** occupied ports, Ctrl-C, backend startup failure, frontend failure, and repeated invocation.
- **User impact:** orphan processes, confusing partial startup, and stale code reload behavior.

### 38. Disk exhaustion and cleanup

- **Current behavior:** cloned repositories accumulate under `data/` indefinitely. There is no quota, TTL, cleanup, or disk monitoring.
- **Root cause:** local storage doubles as an unmanaged cache.
- **Ideal handling:** quota by user/job, immutable object storage artifacts, TTL/LRU cleanup, and low-disk alerts.
- **Tests:** quota boundary, cleanup race, active-job protection, and disk-full injection.
- **User impact:** future clones fail and the whole host can become unhealthy.

### 39. Abuse, SSRF-adjacent clone targets, and denial of service

- **Current behavior:** callers can submit arbitrary clone URLs and trigger CPU-, memory-, disk-, network-, and paid-model-intensive work without authentication or rate limits.
- **Root cause:** open synchronous endpoints with unconstrained input and cost.
- **Ideal handling:** authentication, authorization, host/protocol allowlist, egress controls, quotas, rate limits, job concurrency caps, and cost budgets.
- **Tests:** disallowed hosts/schemes, repeated requests, oversized repository, decompression/object explosion, and per-tenant quota isolation.
- **User impact:** service exhaustion, unexpected bills, and network/security exposure.

### 40. API contract and observability gaps

- **Current behavior:** errors default to framework 500 responses; there are no request IDs, structured logs, metrics, traces, health/readiness endpoints, API versioning, or documented schemas beyond generated defaults.
- **Root cause:** the prototype focuses on the happy path.
- **Ideal handling:** stable error envelope, correlation IDs, stage timings, dependency metrics, safe audit events, `/healthz` and `/readyz`, and versioned contracts.
- **Tests:** schema snapshots, error-code matrix, log redaction, trace propagation, and health behavior during dependency failure.
- **User impact:** support cannot distinguish user error, dependency outage, capacity failure, or code defect.

## Cross-cutting remediation order

1. **Prevent cross-user correctness and confidentiality failures:** replace global pipeline state with analysis IDs and immutable job artifacts.
2. **Constrain untrusted work:** validate URLs, enforce repository/file/chunk quotas, restrict egress, and add authentication/rate limits.
3. **Protect data:** contain symlinks, ignore secrets/vendor content, sanitize output, and harden prompts.
4. **Make failures explicit:** structured errors, readiness checks, skipped-file reports, timeouts, and dependency status.
5. **Improve retrieval correctness:** syntax-aware chunks, deterministic metadata, safe top-k handling, and measured embedding/index choices.
6. **Add production lifecycle controls:** persistent storage, cleanup, observability, and tested deployment/rollback.

## Interview section 1 — Why is global state unsafe here?

**Question:** What is the most serious production flaw in the current API, and how would you fix it?

**Answer:** The single process-wide `pipeline` is the highest-risk flaw. It represents only one repository, is overwritten by every analysis, can expose one user’s repository context to another, can momentarily pair one repository’s index with another’s chunks, disappears on restart, and is not shared across workers. I would issue an `analysis_id` for every request, run analysis as an isolated job, write immutable metadata and index artifacts keyed by tenant and commit SHA, and require that ID on `/ask`. A database tracks status and ownership; object storage holds artifacts; workers publish readiness atomically.

**Why interviewers ask:** This tests whether the candidate sees concurrency, tenancy, process topology, and data confidentiality—not merely dictionary thread safety.

**Common mistakes:** Adding only a lock; using sticky sessions as the final architecture; storing per-user state in another in-memory dictionary; overlooking failure after partial publication.

**Likely follow-ups:** How are jobs expired? How is authorization checked on `analysis_id`? How do workers publish atomically? What happens during schema/index-version migration? The answer should include TTL policy, owner checks, temporary artifact paths plus final commit/pointer swap, and versioned artifact metadata.

## Interview section 2 — How should repository ingestion be secured?

**Question:** What controls are needed before accepting arbitrary Git URLs?

**Answer:** Parse and canonicalize the URL, permit only intended schemes and hosts, reject local/file transports, constrain DNS and outbound network access, authenticate users, enforce per-tenant size/time/concurrency quotas, clone into a sandbox with CPU/memory/disk limits, contain symlinks, scan/redact secrets, and delete temporary credentials and checkout data according to retention policy. Provider APIs can preflight repository size and visibility but are not a substitute for sandboxing.

**Why interviewers ask:** Repository cloning crosses a trust boundary and can consume network, storage, compute, and downstream AI spend.

**Common mistakes:** Treating public GitHub content as trusted; validating with a simple URL prefix; embedding provider tokens in clone URLs; assuming `.gitignore` prevents sensitive ingestion.

**Likely follow-ups:** How do DNS rebinding and redirects affect the allowlist? How are private repositories handled? The answer should revalidate resolved destinations, use egress policy, prefer short-lived read-only provider credentials, redact logs, and isolate tenants.

## Interview section 3 — What is wrong with fixed-size chunks?

**Question:** Is a 500-character chunk size a reasonable RAG strategy for code?

**Answer:** It is a simple baseline, not a robust strategy. It splits symbols and statements, has no overlap, ignores token limits, loses line and symbol metadata, and treats every language identically. A better pipeline uses language-aware parsing to chunk symbols, splits oversized symbols by token-aware windows with overlap, records repository-relative path and line ranges, and evaluates retrieval on a labeled question set. The optimal chunking policy is empirical and may differ by language and query type.

**Why interviewers ask:** This probes whether a candidate distinguishes a plausible implementation from a measured retrieval system.

**Common mistakes:** Claiming one universal chunk size; maximizing overlap without considering index size and duplicate context; optimizing only embedding latency.

**Likely follow-ups:** How would you evaluate it? Use recall@k/MRR/nDCG for retrieval, answer groundedness/citation accuracy for generation, latency and index bytes for cost, with stratification by language and question class.

## Interview section 4 — How should downstream AI failures behave?

**Question:** How would you handle Groq timeouts and rate limits without causing an outage?

**Answer:** Set bounded connect/read deadlines, propagate request cancellation, map 429/5xx/timeouts into stable API errors, retry only transient failures with exponential backoff and jitter under a strict attempt/time budget, honor provider retry hints, and add a circuit breaker. Queueing can smooth asynchronous work, but interactive questions need a latency budget and fast failure. Metrics should separate provider errors, local saturation, and invalid credentials; secrets and prompts must be redacted.

**Why interviewers ask:** Naive retries multiply load and cost during an outage.

**Common mistakes:** Unlimited retries; retrying authentication or validation errors; returning HTTP 500 for every dependency condition; omitting idempotency/cancellation.

**Likely follow-ups:** Should there be a fallback model? Only if quality, privacy, compatibility, and cost are explicitly accepted; the response should disclose fallback use and preserve deterministic policy.

## Interview section 5 — How do you test concurrency bugs?

**Question:** How would you prove that one repository’s index cannot be paired with another repository’s chunks?

**Answer:** First, create a deterministic regression test against the current design using two distinct corpora and barriers inserted around index/chunk publication to force the harmful interleaving. Then test the redesigned system by running many concurrent analysis and ask requests across tenants, routing them across workers, and asserting every retrieved path and answer citation belongs to the requested analysis and owner. Add restart and retry cases, and run the suite repeatedly under race-friendly scheduling.

**Why interviewers ask:** Ordinary happy-path tests rarely reproduce concurrency failures.

**Common mistakes:** Relying on sleep timing; testing only threads in one process; checking status codes without validating data provenance.

**Likely follow-ups:** What is the linearization point? It is the atomic publication of the completed artifact manifest/status; asks can see either “not ready” or the complete immutable version, never a partial one.

## Interview section 6 — What should users see when analysis is partial?

**Question:** Should an analysis succeed if some files cannot be read or parsed?

**Answer:** Usually yes, with explicit degraded status, unless policy-critical failures occur. The result should state discovered, supported, indexed, empty, skipped, and failed counts; group reasons without exposing sensitive paths; preserve per-file diagnostics for authorized operators; and block success if no useful content remains or if security invariants fail. Questions should carry the analyzed commit and coverage metadata so users understand limitations.

**Why interviewers ask:** Real repositories are messy, so all-or-nothing behavior is often impractical while silent omission is deceptive.

**Common mistakes:** Swallowing all errors; failing the entire job for one malformed file; exposing absolute server paths; calling partial output “complete.”

**Likely follow-ups:** Which failures are fatal? Path escape, tenant-boundary violation, artifact corruption, invalid ownership, and inability to establish a consistent commit should be fatal; unsupported or malformed individual files can be reported as partial.
