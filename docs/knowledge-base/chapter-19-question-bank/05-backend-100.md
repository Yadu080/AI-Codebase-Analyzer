# Backend Interview Question Bank — 100 Questions

Each answer explicitly separates repository behavior from production recommendations.

1. **Question:** What backend framework is implemented, and where is the application created?
   - **Ideal Answer:** **Implemented:** `app/api.py` imports FastAPI and creates a module-level `app = FastAPI()`. **Recommended:** add title, version, lifespan, and OpenAPI metadata.
   - **Expected Follow-up:** Why does `uvicorn app.api:app` work?
   - **Common Mistake:** Claiming Streamlit is the API server.
   - **How to Impress Interviewer:** Explain module import plus ASGI application discovery.

2. **Question:** What protocol connects Uvicorn and this FastAPI application?
   - **Ideal Answer:** **Implemented:** FastAPI exposes an ASGI callable that Uvicorn serves. **Recommended:** configure workers, timeouts, proxy headers, and graceful shutdown for deployment.
   - **Expected Follow-up:** How is ASGI different from WSGI?
   - **Common Mistake:** Saying FastAPI directly opens the socket.
   - **How to Impress Interviewer:** Relate ASGI scopes, receive/send events, and concurrency.

3. **Question:** Which endpoints does the backend currently expose?
   - **Ideal Answer:** **Implemented:** three POST routes: `/analyze`, `/ask`, and `/architecture`. **Recommended:** add health/readiness endpoints and version the public API.
   - **Expected Follow-up:** Why are all three POST requests?
   - **Common Mistake:** Inventing a GET endpoint from the README.
   - **How to Impress Interviewer:** Discuss safety, idempotency, and resource-oriented alternatives.

4. **Question:** How is an `/analyze` request validated?
   - **Ideal Answer:** **Implemented:** FastAPI uses Pydantic `RepoRequest`, requiring a string `repo_url`. **Recommended:** use `HttpUrl` plus an allowlist and repository-specific validation.
   - **Expected Follow-up:** What response occurs for a missing field?
   - **Common Mistake:** Saying the URL is already security-validated.
   - **How to Impress Interviewer:** Mention automatic 422 responses and SSRF risk.

5. **Question:** How is an `/ask` request validated?
   - **Ideal Answer:** **Implemented:** `QuestionRequest` requires `question: str`. **Recommended:** reject blank input and enforce sensible length/token limits.
   - **Expected Follow-up:** Would whitespace-only text pass?
   - **Common Mistake:** Assuming Pydantic rejects empty strings by default.
   - **How to Impress Interviewer:** Propose `Field(min_length=1, max_length=...)` and trimming.

6. **Question:** What does `/analyze` do in order?
   - **Ideal Answer:** **Implemented:** clone, load files, character-chunk, embed, build FAISS index, save chunks/index globally, summarize, and return counts. **Recommended:** make it a tracked background job.
   - **Expected Follow-up:** Which stage is likely slowest?
   - **Common Mistake:** Omitting embedding or persistent state.
   - **How to Impress Interviewer:** Identify failure boundaries and stage-level telemetry.

7. **Question:** Why are the current route handlers declared with `def` rather than `async def`?
   - **Ideal Answer:** **Implemented:** all handlers are synchronous, so FastAPI runs them in a threadpool. **Recommended:** keep blocking work off the event loop and use workers/queues for CPU-heavy analysis.
   - **Expected Follow-up:** Would changing only the keyword improve performance?
   - **Common Mistake:** Converting to `async def` while retaining blocking calls.
   - **How to Impress Interviewer:** Distinguish event-loop blocking from threadpool saturation.

8. **Question:** What is stored in the module-level `pipeline` dictionary?
   - **Ideal Answer:** **Implemented:** the latest analysis stores `chunks`, `index`, and `summary`. **Recommended:** use repository-scoped durable storage with explicit state models.
   - **Expected Follow-up:** What happens after process restart?
   - **Common Mistake:** Calling this a database.
   - **How to Impress Interviewer:** Explain process-local lifetime and worker isolation.

9. **Question:** What happens if `/ask` is called before `/analyze`?
   - **Ideal Answer:** **Implemented:** indexing `pipeline["index"]` or `["chunks"]` raises `KeyError`, likely producing a 500. **Recommended:** return a deliberate 409 or 404 with a typed error.
   - **Expected Follow-up:** Where should that precondition be checked?
   - **Common Mistake:** Saying FastAPI automatically returns 422.
   - **How to Impress Interviewer:** Define a machine-readable error contract.

10. **Question:** Can the backend safely serve two repositories concurrently?
   - **Ideal Answer:** **Implemented:** no; both analyses overwrite one shared `pipeline`, so asks target whichever completed last. **Recommended:** key state by analysis ID and isolate writes.
   - **Expected Follow-up:** What race can occur during overlapping analysis?
   - **Common Mistake:** Assuming Python dictionaries make the workflow atomic.
   - **How to Impress Interviewer:** Describe publication only after a complete immutable pipeline is built.

11. **Question:** How does multi-worker Uvicorn affect `pipeline`?
   - **Ideal Answer:** **Implemented:** each worker process has its own dictionary and may not see another worker’s analysis. **Recommended:** move state to shared persistence or use sticky routing only as a temporary workaround.
   - **Expected Follow-up:** Why is `--workers 1` not a full fix?
   - **Common Mistake:** Believing globals are shared across processes.
   - **How to Impress Interviewer:** Connect process memory, load balancing, and consistency.

12. **Question:** Is `/analyze` idempotent?
   - **Ideal Answer:** **Implemented:** repeated calls reuse an existing clone but recompute chunks, embeddings, and index; results may overwrite global state. **Recommended:** return an analysis resource keyed by repo and revision.
   - **Expected Follow-up:** How should cache invalidation handle new commits?
   - **Common Mistake:** Equating POST with inherently non-idempotent behavior.
   - **How to Impress Interviewer:** Include commit SHA in the idempotency key.

13. **Question:** What HTTP status does successful `/analyze` return?
   - **Ideal Answer:** **Implemented:** FastAPI defaults to 200 because no `status_code` is declared. **Recommended:** use 202 for queued analysis or 201 when creating an analysis resource.
   - **Expected Follow-up:** When would 200 remain appropriate?
   - **Common Mistake:** Assuming POST automatically means 201.
   - **How to Impress Interviewer:** Tie status choice to synchronous versus asynchronous semantics.

14. **Question:** What is the `/analyze` response schema?
   - **Ideal Answer:** **Implemented:** an untyped dictionary containing `message`, `chunks`, and `summary`. **Recommended:** define a Pydantic response model and `response_model`.
   - **Expected Follow-up:** What benefits does response validation provide?
   - **Common Mistake:** Treating the returned dict as a declared contract.
   - **How to Impress Interviewer:** Mention filtering, OpenAPI accuracy, and regression detection.

15. **Question:** What is the `/ask` response schema?
   - **Ideal Answer:** **Implemented:** it returns `{"answer": answer}` without a response model. **Recommended:** include analysis ID, citations, model metadata, and a typed schema.
   - **Expected Follow-up:** Why return citations?
   - **Common Mistake:** Claiming retrieved chunks are already exposed.
   - **How to Impress Interviewer:** Separate user answer, evidence, and diagnostics.

16. **Question:** What does `/architecture` return?
   - **Ideal Answer:** **Implemented:** it clones/reuses the repository, extracts Python imports, and returns them under `architecture`. **Recommended:** type the graph and include parse warnings and revision identity.
   - **Expected Follow-up:** Does it return the rendered NetworkX graph?
   - **Common Mistake:** Confusing API output with frontend visualization.
   - **How to Impress Interviewer:** Note that JSON contains an adjacency mapping, not an image.

17. **Question:** How are validation failures represented by FastAPI?
   - **Ideal Answer:** **Implemented:** request-model failures are handled by FastAPI/Pydantic as 422 responses. **Recommended:** normalize them into the project’s versioned error envelope if clients require stability.
   - **Expected Follow-up:** Why not return 400 for everything?
   - **Common Mistake:** Catching validation errors inside every handler.
   - **How to Impress Interviewer:** Explain transport syntax versus semantic validation.

18. **Question:** How are application exceptions handled today?
   - **Ideal Answer:** **Implemented:** there are no route-level handlers, so uncaught Git, file, FAISS, or Groq errors become generic 500 responses. **Recommended:** map known domain failures and log causes.
   - **Expected Follow-up:** Which errors are safe to expose?
   - **Common Mistake:** Returning raw exception strings to clients.
   - **How to Impress Interviewer:** Preserve correlation IDs while redacting internals.

19. **Question:** What error should an invalid repository URL produce?
   - **Ideal Answer:** **Implemented:** behavior depends on GitPython and likely ends as 500. **Recommended:** validate early and map malformed URLs to 422 and inaccessible repositories to a suitable 4xx.
   - **Expected Follow-up:** How would private repositories differ?
   - **Common Mistake:** Classifying every clone failure as server failure.
   - **How to Impress Interviewer:** Separate user input, authentication, not-found, and upstream outage.

20. **Question:** What security issue exists in accepting arbitrary `repo_url` values?
   - **Ideal Answer:** **Implemented:** the value flows directly to `git.Repo.clone_from`. **Recommended:** restrict schemes/hosts, block local paths and private networks, and sandbox Git to reduce SSRF and option-injection risk.
   - **Expected Follow-up:** Is Pydantic `HttpUrl` sufficient?
   - **Common Mistake:** Treating public Git hosting as implicitly enforced.
   - **How to Impress Interviewer:** Mention redirect/DNS rebinding defenses and egress policy.

21. **Question:** How is the clone destination derived?
   - **Ideal Answer:** **Implemented:** the final URL segment, minus `.git`, is joined beneath `data`. **Recommended:** canonicalize and generate a server-owned identifier instead of trusting a path-derived name.
   - **Expected Follow-up:** What collision can this create?
   - **Common Mistake:** Assuming repository names are globally unique.
   - **How to Impress Interviewer:** Include owner, host, and commit in storage identity.

22. **Question:** Is the clone path traversal-safe?
   - **Ideal Answer:** **Implemented:** there is no explicit resolved-path containment check. **Recommended:** reject suspicious names and verify the resolved destination remains under the configured data root.
   - **Expected Follow-up:** What other Git URL forms matter?
   - **Common Mistake:** Assuming `os.path.join` enforces containment.
   - **How to Impress Interviewer:** Test scp-like, file, and encoded path inputs.

23. **Question:** What happens when a repository directory already exists?
   - **Ideal Answer:** **Implemented:** `clone_repository` returns it without fetch, pull, or revision verification. **Recommended:** pin a commit and update through controlled fetch logic.
   - **Expected Follow-up:** How can stale code affect answers?
   - **Common Mistake:** Saying every analysis clones fresh content.
   - **How to Impress Interviewer:** Make revision SHA visible in API responses.

24. **Question:** How should clone timeouts be handled?
   - **Ideal Answer:** **Implemented:** no application-level timeout exists. **Recommended:** run cloning in a constrained subprocess/job with wall-clock timeout, size limit, cancellation, and cleanup.
   - **Expected Follow-up:** Why is a request timeout alone insufficient?
   - **Common Mistake:** Assuming disconnected clients stop Git work.
   - **How to Impress Interviewer:** Discuss cooperative cancellation and orphaned subprocesses.

25. **Question:** What resource-exhaustion risk exists during analysis?
   - **Ideal Answer:** **Implemented:** the service can clone and read arbitrarily large repositories, build all chunks and embeddings in memory, then index them. **Recommended:** enforce size/file/chunk quotas.
   - **Expected Follow-up:** Which limit would you enforce first?
   - **Common Mistake:** Focusing only on request-body size.
   - **How to Impress Interviewer:** Budget disk, RAM, CPU, network, and model tokens separately.

26. **Question:** Which source extensions are loaded?
   - **Ideal Answer:** **Implemented:** `.py`, `.js`, `.ts`, `.java`, `.cpp`, and `.c`. **Recommended:** make language support configurable and record skipped files.
   - **Expected Follow-up:** Does the README’s Python-focus statement match?
   - **Common Mistake:** Claiming every repository file is embedded.
   - **How to Impress Interviewer:** Note extension checks are case-sensitive.

27. **Question:** How are unreadable code files handled?
   - **Ideal Answer:** **Implemented:** a bare `except` silently skips them. **Recommended:** catch expected decoding/I/O errors and report structured skip metrics.
   - **Expected Follow-up:** Why are bare exceptions dangerous?
   - **Common Mistake:** Treating silent skipping as resilience.
   - **How to Impress Interviewer:** Preserve partial success while making data loss observable.

28. **Question:** Does traversal exclude `.git`, dependencies, or generated code?
   - **Ideal Answer:** **Implemented:** no directory pruning or ignore-file support is present. **Recommended:** honor `.gitignore`, default excludes, symlink policy, and configurable paths.
   - **Expected Follow-up:** Why does generated code hurt retrieval?
   - **Common Mistake:** Assuming `os.walk` follows project ignore rules.
   - **How to Impress Interviewer:** Add provenance and exclusion statistics.

29. **Question:** How does the current code handle symlinks?
   - **Ideal Answer:** **Implemented:** no explicit symlink policy is defined; `os.walk` defaults influence directory traversal while file opens may follow links. **Recommended:** reject links escaping the repository root.
   - **Expected Follow-up:** What is the threat?
   - **Common Mistake:** Assuming cloned repositories cannot contain symlinks.
   - **How to Impress Interviewer:** Resolve each candidate path and enforce containment.

30. **Question:** How does `generate_repo_summary` count files?
   - **Ideal Answer:** **Implemented:** it counts every walked file, even unsupported files, while chunks cover only selected source extensions. **Recommended:** expose total and indexed file counts separately.
   - **Expected Follow-up:** Why might totals confuse users?
   - **Common Mistake:** Saying `total_files` means embedded files.
   - **How to Impress Interviewer:** Define metrics with precise denominators.

31. **Question:** How are languages detected in the summary?
   - **Ideal Answer:** **Implemented:** only `.py`, `.js`, `.ts`, and `.java` add language labels; C/C++ files can be indexed but omitted. **Recommended:** centralize extension-to-language mapping.
   - **Expected Follow-up:** What other edge cases exist?
   - **Common Mistake:** Claiming the list derives from the parser constant.
   - **How to Impress Interviewer:** Point out casing, headers, notebooks, and mixed files.

32. **Question:** Is summary language ordering stable?
   - **Ideal Answer:** **Implemented:** languages are collected in a set and converted to a list, so ordering is not guaranteed. **Recommended:** sort or use deterministic insertion order.
   - **Expected Follow-up:** Why does determinism matter?
   - **Common Mistake:** Depending on the current runtime’s observed order.
   - **How to Impress Interviewer:** Connect stable output to tests and caching.

33. **Question:** How are `main_modules` selected?
   - **Ideal Answer:** **Implemented:** they are the first five Python filenames encountered by `os.walk`. **Recommended:** rank modules by project structure, entry points, or dependency centrality.
   - **Expected Follow-up:** Are paths preserved?
   - **Common Mistake:** Calling them the five most important modules.
   - **How to Impress Interviewer:** Explain basename collisions and nondeterministic traversal.

34. **Question:** What happens if analysis finds zero chunks?
   - **Ideal Answer:** **Implemented:** embedding may return an empty result and `build_index` accesses `embeddings[0]`, causing failure. **Recommended:** detect zero supported content and return a clear 422.
   - **Expected Follow-up:** Where is the best guard?
   - **Common Mistake:** Blaming FAISS alone.
   - **How to Impress Interviewer:** Validate invariants between every pipeline stage.

35. **Question:** How does the backend chunk code?
   - **Ideal Answer:** **Implemented:** fixed 500-character slices without overlap or syntax awareness. **Recommended:** use language-aware boundaries, overlap, metadata, and token-based limits.
   - **Expected Follow-up:** Why can fixed slices break retrieval?
   - **Common Mistake:** Calling 500 characters 500 tokens.
   - **How to Impress Interviewer:** Tie chunk strategy to embedding model limits.

36. **Question:** What metadata accompanies each chunk?
   - **Ideal Answer:** **Implemented:** only `file_path` and raw `chunk` text. **Recommended:** add repository, revision, language, symbol, line range, and stable chunk ID.
   - **Expected Follow-up:** Which metadata enables citations?
   - **Common Mistake:** Claiming line numbers are retained.
   - **How to Impress Interviewer:** Design IDs that survive incremental re-indexing.

37. **Question:** Where is the embedding model instantiated?
   - **Ideal Answer:** **Implemented:** `SentenceTransformer("all-MiniLM-L6-v2")` loads at module import in `app/embedder.py`. **Recommended:** initialize it in lifespan/startup and expose readiness.
   - **Expected Follow-up:** What happens on first process start?
   - **Common Mistake:** Saying it loads once for an entire multi-worker deployment.
   - **How to Impress Interviewer:** Discuss startup cost and per-process memory.

38. **Question:** Can model loading delay API startup?
   - **Ideal Answer:** **Implemented:** yes, importing `app.api` imports `app.embedder`, which constructs the model before serving. **Recommended:** controlled warmup with failure reporting and cached model artifacts.
   - **Expected Follow-up:** How should readiness differ from liveness?
   - **Common Mistake:** Hiding startup failure behind lazy requests.
   - **How to Impress Interviewer:** Prevent traffic until dependencies are ready.

39. **Question:** What FAISS index type is used?
   - **Ideal Answer:** **Implemented:** `faiss.IndexFlatL2`, an exact Euclidean-distance index. **Recommended:** benchmark cosine/IP normalization and approximate indexes at scale.
   - **Expected Follow-up:** What are FlatL2’s complexity characteristics?
   - **Common Mistake:** Calling it an approximate vector database.
   - **How to Impress Interviewer:** State exact search trades memory and latency for recall.

40. **Question:** Are embeddings normalized before L2 search?
   - **Ideal Answer:** **Implemented:** no explicit normalization appears. **Recommended:** test normalized vectors with inner product or L2 according to the model’s retrieval behavior.
   - **Expected Follow-up:** When are cosine and L2 rankings equivalent?
   - **Common Mistake:** Assuming SentenceTransformer always normalizes output.
   - **How to Impress Interviewer:** Mention unit vectors make squared L2 monotonic with cosine.

41. **Question:** How is NumPy data passed to FAISS?
   - **Ideal Answer:** **Implemented:** `np.array(embeddings)` is added without explicit dtype or contiguity checks. **Recommended:** enforce contiguous `float32` and validate shape.
   - **Expected Follow-up:** Why does dtype matter?
   - **Common Mistake:** Assuming every encoder output matches FAISS requirements.
   - **How to Impress Interviewer:** Validate `(n, dimension)` and finite values.

42. **Question:** What top-k value does retrieval use?
   - **Ideal Answer:** **Implemented:** `retrieve` defaults to five and `/ask` does not override it. **Recommended:** tune or constrain top-k based on evaluation and context budget.
   - **Expected Follow-up:** Is a larger top-k always better?
   - **Common Mistake:** Claiming five was empirically optimized.
   - **How to Impress Interviewer:** Explain recall versus noise and token cost.

43. **Question:** What happens when fewer than five vectors exist?
   - **Ideal Answer:** **Implemented:** FAISS may return sentinel indices such as `-1`; Python then indexes the last chunk, causing duplicates or wrong evidence. **Recommended:** cap `k` at index size and reject invalid indices.
   - **Expected Follow-up:** How would you test this?
   - **Common Mistake:** Assuming FAISS shortens its result automatically.
   - **How to Impress Interviewer:** Include zero-, one-, and four-vector boundary tests.

44. **Question:** Are retrieval distances used by the API?
   - **Ideal Answer:** **Implemented:** distances are returned by FAISS but discarded. **Recommended:** retain scores for diagnostics, thresholds, reranking, and citations.
   - **Expected Follow-up:** Can raw L2 scores be shown as confidence?
   - **Common Mistake:** Calling distance a calibrated probability.
   - **How to Impress Interviewer:** Calibrate abstention using labeled evaluation data.

45. **Question:** Is the FAISS index persisted?
   - **Ideal Answer:** **Implemented:** no; it exists only inside the process-global pipeline. **Recommended:** persist versioned indexes and metadata atomically.
   - **Expected Follow-up:** What must be stored with the index?
   - **Common Mistake:** Persisting FAISS without aligned chunk metadata.
   - **How to Impress Interviewer:** Validate model version, dimension, and revision on load.

46. **Question:** How should index replacement be made concurrency-safe?
   - **Ideal Answer:** **Implemented:** separate dictionary assignments expose partially updated state. **Recommended:** build an immutable bundle and swap one reference under a lock or repository-scoped transaction.
   - **Expected Follow-up:** What partial state is possible?
   - **Common Mistake:** Locking only `pipeline["index"]`.
   - **How to Impress Interviewer:** Use copy-on-write publication after all stages succeed.

47. **Question:** Can `/ask` read mismatched chunks and index?
   - **Ideal Answer:** **Implemented:** yes; an analysis can replace `chunks` and `index` between separate reads. **Recommended:** snapshot a single pipeline object at request start.
   - **Expected Follow-up:** Why is the GIL insufficient?
   - **Common Mistake:** Treating multiple dictionary operations as one transaction.
   - **How to Impress Interviewer:** Describe a concrete interleaving that returns wrong code.

48. **Question:** Should repository analysis remain inside an HTTP request?
   - **Ideal Answer:** **Implemented:** it runs synchronously before the response. **Recommended:** enqueue analysis, return 202 plus job ID, and provide status/cancellation endpoints.
   - **Expected Follow-up:** When is synchronous processing acceptable?
   - **Common Mistake:** Assuming `async def` creates a durable job.
   - **How to Impress Interviewer:** Address retries, worker crashes, and idempotency.

49. **Question:** How should analysis progress be represented?
   - **Ideal Answer:** **Implemented:** only final success or failure is visible. **Recommended:** persist states such as queued, cloning, parsing, embedding, indexing, ready, failed, and canceled.
   - **Expected Follow-up:** How can clients receive updates?
   - **Common Mistake:** Storing progress only in a worker’s memory.
   - **How to Impress Interviewer:** Include monotonic stage events and retry metadata.

50. **Question:** What timeout controls exist on API routes?
   - **Ideal Answer:** **Implemented:** none are declared in application code. **Recommended:** coordinate gateway, server, upstream, and job timeouts rather than one blanket value.
   - **Expected Follow-up:** What should happen after client disconnect?
   - **Common Mistake:** Treating Uvicorn keep-alive as request execution timeout.
   - **How to Impress Interviewer:** Separate connect, read, processing, and shutdown timeouts.

51. **Question:** Is rate limiting implemented?
   - **Ideal Answer:** **Implemented:** no. **Recommended:** rate-limit by authenticated principal and endpoint, with stricter quotas for clone, embedding, and LLM operations.
   - **Expected Follow-up:** Where should distributed limits live?
   - **Common Mistake:** Limiting only `/ask`.
   - **How to Impress Interviewer:** Add concurrency caps and cost-weighted quotas.

52. **Question:** Is authentication or authorization implemented?
   - **Ideal Answer:** **Implemented:** no route has authentication dependencies. **Recommended:** authenticate callers and authorize access to each analysis resource.
   - **Expected Follow-up:** Why does authorization matter for public repositories?
   - **Common Mistake:** Assuming public source means unrestricted compute.
   - **How to Impress Interviewer:** Discuss abuse prevention and cross-tenant data isolation.

53. **Question:** Is CORS configured?
   - **Ideal Answer:** **Implemented:** no CORS middleware is present. **Recommended:** add an explicit origin/method/header allowlist only if a browser client uses a different origin.
   - **Expected Follow-up:** Why does Streamlit currently work?
   - **Common Mistake:** Assuming server-side `requests` is subject to browser CORS.
   - **How to Impress Interviewer:** Distinguish browser enforcement from backend-to-backend HTTP.

54. **Question:** How does the Streamlit frontend call the backend?
   - **Ideal Answer:** **Implemented:** synchronous Python `requests.post` calls target hard-coded `http://127.0.0.1:8000`. **Recommended:** configure base URL, timeouts, retries, and typed client errors.
   - **Expected Follow-up:** Is this traffic originating in the browser?
   - **Common Mistake:** Treating Streamlit’s Python process as frontend JavaScript.
   - **How to Impress Interviewer:** Explain deployment networking and loopback scope.

55. **Question:** What is wrong with omitting timeouts in frontend `requests.post`?
   - **Ideal Answer:** **Implemented:** calls can wait indefinitely and tie up the Streamlit interaction. **Recommended:** set connect/read timeouts and handle timeout errors distinctly.
   - **Expected Follow-up:** Should `/analyze` simply get a huge read timeout?
   - **Common Mistake:** Retrying all POST requests blindly.
   - **How to Impress Interviewer:** Prefer job polling for long work and idempotency for retries.

56. **Question:** Does the frontend preserve backend error details?
   - **Ideal Answer:** **Implemented:** it checks only status 200 and shows generic messages. **Recommended:** parse a safe typed error envelope and retain a correlation ID.
   - **Expected Follow-up:** What should users see for 422 versus 500?
   - **Common Mistake:** Displaying raw stack traces.
   - **How to Impress Interviewer:** Separate actionable user text from operator diagnostics.

57. **Question:** What API versioning strategy exists?
   - **Ideal Answer:** **Implemented:** none; routes are rooted directly at `/analyze`, `/ask`, and `/architecture`. **Recommended:** introduce `/v1` or negotiated versioning before external clients depend on shapes.
   - **Expected Follow-up:** When is versioning unnecessary?
   - **Common Mistake:** Versioning every internal code change.
   - **How to Impress Interviewer:** Version contracts, not deployments.

58. **Question:** How is OpenAPI documentation produced?
   - **Ideal Answer:** **Implemented:** FastAPI automatically derives request schemas and paths, but responses lack explicit models and descriptions. **Recommended:** add tags, summaries, examples, and error schemas.
   - **Expected Follow-up:** Which current details will OpenAPI miss?
   - **Common Mistake:** Assuming inferred dictionaries create stable response models.
   - **How to Impress Interviewer:** Treat the generated spec as a tested artifact.

59. **Question:** Should `RepoRequest` and `QuestionRequest` remain in `api.py`?
   - **Ideal Answer:** **Implemented:** both are local, minimal models. **Recommended:** move shared request/response/domain schemas when reuse or API growth justifies it, not merely for file count.
   - **Expected Follow-up:** What separation would you choose?
   - **Common Mistake:** Creating abstractions before contracts stabilize.
   - **How to Impress Interviewer:** Separate transport models from domain/job models.

60. **Question:** How should whitespace and URL normalization be handled?
   - **Ideal Answer:** **Implemented:** raw strings pass through unchanged. **Recommended:** trim questions, canonicalize allowed repository URLs, and preserve a canonical identity.
   - **Expected Follow-up:** Could normalization change semantics?
   - **Common Mistake:** Lowercasing entire URLs blindly.
   - **How to Impress Interviewer:** Normalize host/scheme while respecting case-sensitive paths where relevant.

61. **Question:** What observability is implemented in the backend?
   - **Ideal Answer:** **Implemented:** repository cloning uses `print`; there is no structured application logging, metrics, or tracing. **Recommended:** add request IDs, stage timings, counters, and structured logs.
   - **Expected Follow-up:** Which metrics matter first?
   - **Common Mistake:** Logging full code or prompts.
   - **How to Impress Interviewer:** Track latency and failures by pipeline stage without leaking source.

62. **Question:** How should request correlation work across analysis and ask flows?
   - **Ideal Answer:** **Implemented:** no IDs connect requests. **Recommended:** issue request IDs and stable analysis IDs, propagate them through jobs, logs, and LLM calls.
   - **Expected Follow-up:** Should clients supply request IDs?
   - **Common Mistake:** Using repository URL as the sole correlation key.
   - **How to Impress Interviewer:** Support trace context and deduplicated idempotency keys.

63. **Question:** Is a health endpoint implemented?
   - **Ideal Answer:** **Implemented:** no. **Recommended:** expose cheap liveness and readiness checks, with readiness reflecting model/storage availability rather than running full analysis.
   - **Expected Follow-up:** Should Groq be called during every readiness probe?
   - **Common Mistake:** Making health checks expensive or state-mutating.
   - **How to Impress Interviewer:** Distinguish local readiness from degraded upstream capability.

64. **Question:** How should graceful shutdown handle in-flight analysis?
   - **Ideal Answer:** **Implemented:** no lifespan or shutdown logic exists. **Recommended:** stop accepting jobs, drain or checkpoint workers, close resources, and avoid publishing partial indexes.
   - **Expected Follow-up:** What if shutdown exceeds its grace period?
   - **Common Mistake:** Assuming Uvicorn preserves Python globals.
   - **How to Impress Interviewer:** Design jobs to be retryable after termination.

65. **Question:** Where should the Groq client lifecycle live?
   - **Ideal Answer:** **Implemented:** `qa_engine.py` creates a global client at import. **Recommended:** inject a configured client through application lifespan or service dependencies for testing and rotation.
   - **Expected Follow-up:** Is one client per request desirable?
   - **Common Mistake:** Recreating connection-capable clients unnecessarily.
   - **How to Impress Interviewer:** Balance reuse, thread safety, and secret refresh.

66. **Question:** What happens if `GROQ_API_KEY` is missing?
   - **Ideal Answer:** **Implemented:** `os.getenv` returns `None`; failure may occur at client construction or first request depending on SDK behavior. **Recommended:** validate configuration at startup.
   - **Expected Follow-up:** Should liveness fail?
   - **Common Mistake:** Returning the missing-key detail to users.
   - **How to Impress Interviewer:** Fail readiness with a redacted operator-facing reason.

67. **Question:** Is dependency injection used?
   - **Ideal Answer:** **Implemented:** no FastAPI `Depends` usage appears; routes directly import concrete functions and globals. **Recommended:** inject services/state where it improves testing, authorization, and lifecycle control.
   - **Expected Follow-up:** What would you inject first?
   - **Common Mistake:** Wrapping every pure function in a dependency.
   - **How to Impress Interviewer:** Start with pipeline store and external clients.

68. **Question:** How testable are the current route handlers?
   - **Ideal Answer:** **Implemented:** direct imports, global state, filesystem/network calls, and import-time models complicate isolation. **Recommended:** compose services behind interfaces and use FastAPI dependency overrides.
   - **Expected Follow-up:** What is the first route test?
   - **Common Mistake:** Mocking FastAPI itself.
   - **How to Impress Interviewer:** Test HTTP contracts while substituting clone/embed/LLM boundaries.

69. **Question:** What backend tests are present?
   - **Ideal Answer:** **Implemented:** no test files were found in the inspected repository. **Recommended:** add unit, API contract, concurrency, and failure-path tests.
   - **Expected Follow-up:** Which bug deserves a regression test first?
   - **Common Mistake:** Claiming README examples are tests.
   - **How to Impress Interviewer:** Prioritize ask-before-analyze and overlapping-analysis races.

70. **Question:** How would you test FastAPI endpoints without running Uvicorn?
   - **Ideal Answer:** **Implemented:** no such tests exist. **Recommended:** use FastAPI/Starlette’s test client or an ASGI transport and override external dependencies.
   - **Expected Follow-up:** When is a live Uvicorn test still useful?
   - **Common Mistake:** Making every test clone a real GitHub repository.
   - **How to Impress Interviewer:** Keep a small end-to-end layer for server and networking behavior.

71. **Question:** What malformed-state test should cover `/ask`?
   - **Ideal Answer:** **Implemented:** no guard exists for missing or inconsistent pipeline keys. **Recommended:** test empty state, missing index, missing chunks, and index/chunk cardinality mismatch.
   - **Expected Follow-up:** Which statuses should these map to?
   - **Common Mistake:** Testing only happy-path generated text.
   - **How to Impress Interviewer:** Assert no LLM call occurs when retrieval preconditions fail.

72. **Question:** How should API error responses be structured?
   - **Ideal Answer:** **Implemented:** validation uses FastAPI defaults and other failures are generic. **Recommended:** return stable `code`, `message`, `request_id`, and optional safe `details`.
   - **Expected Follow-up:** Should HTTP status and error code duplicate?
   - **Common Mistake:** Encoding all failures as HTTP 200.
   - **How to Impress Interviewer:** Keep domain codes stable across wording changes.

73. **Question:** Which status fits an analysis that is not ready?
   - **Ideal Answer:** **Implemented:** no analysis resource exists, so this case becomes a likely 500. **Recommended:** return 409 for unmet state or 202 with status information, consistently documented.
   - **Expected Follow-up:** Why not 404?
   - **Common Mistake:** Choosing status without defining resource semantics.
   - **How to Impress Interviewer:** Distinguish unknown analysis from known-but-processing analysis.

74. **Question:** How should upstream Groq rate limits map to HTTP?
   - **Ideal Answer:** **Implemented:** they are uncaught and likely surface as 500. **Recommended:** map to 429 or 503 as appropriate, include `Retry-After`, and bound retries.
   - **Expected Follow-up:** When should the backend retry?
   - **Common Mistake:** Retrying non-idempotent or quota-exhausted calls indefinitely.
   - **How to Impress Interviewer:** Use jittered backoff within a latency budget.

75. **Question:** How should GitHub/network outages map to API behavior?
   - **Ideal Answer:** **Implemented:** GitPython exceptions propagate. **Recommended:** classify timeout, DNS, authentication, not-found, and upstream unavailable separately.
   - **Expected Follow-up:** Which failures are retryable?
   - **Common Mistake:** Converting every external failure to 400.
   - **How to Impress Interviewer:** Record root cause internally while maintaining a safe contract.

76. **Question:** Does the backend support private repositories?
   - **Ideal Answer:** **Implemented:** no credential input or secure Git authentication flow is defined. **Recommended:** add a scoped credential integration only if required, never credentials embedded in URLs.
   - **Expected Follow-up:** How would secrets be isolated?
   - **Common Mistake:** Persisting access tokens in clone paths or logs.
   - **How to Impress Interviewer:** Use short-lived credentials and scrub remote metadata.

77. **Question:** Is HTTPS termination configured in this repository?
   - **Ideal Answer:** **Implemented:** no; documented Uvicorn runs locally on default HTTP. **Recommended:** terminate TLS at a trusted proxy or configure deployment TLS and forwarded headers safely.
   - **Expected Follow-up:** What proxy-header risk exists?
   - **Common Mistake:** Trusting `X-Forwarded-*` from every client.
   - **How to Impress Interviewer:** Restrict trusted proxies and generate correct external URLs.

78. **Question:** What Uvicorn configuration is documented?
   - **Ideal Answer:** **Implemented:** README shows `uvicorn app.api:app --reload`. **Recommended:** reserve reload for development and configure production workers/logging/timeouts through deployment settings.
   - **Expected Follow-up:** Why is reload unsafe for production?
   - **Common Mistake:** Treating reload as high availability.
   - **How to Impress Interviewer:** Note reload restarts erase the in-memory pipeline.

79. **Question:** What happens to state during development reload?
   - **Ideal Answer:** **Implemented:** module reload recreates the empty `pipeline`, requiring re-analysis. **Recommended:** persist analysis artifacts or communicate state loss explicitly.
   - **Expected Follow-up:** Does the cloned repository also disappear?
   - **Common Mistake:** Equating process memory with files under `data`.
   - **How to Impress Interviewer:** Separate durable clone files from volatile index memory.

80. **Question:** How should large JSON architecture responses be controlled?
   - **Ideal Answer:** **Implemented:** the full import mapping is returned without pagination or size limits. **Recommended:** cap repository size, paginate graph data, or store an artifact.
   - **Expected Follow-up:** Is streaming JSON enough?
   - **Common Mistake:** Ignoring serialization memory and client rendering cost.
   - **How to Impress Interviewer:** Offer filtered subgraphs and summaries.

81. **Question:** What does the AST parser do with syntax errors?
   - **Ideal Answer:** **Implemented:** a bare `except` silently skips the file. **Recommended:** catch `SyntaxError`, retain warnings, and distinguish unsupported syntax from I/O failures.
   - **Expected Follow-up:** Could one bad file fail `/architecture`?
   - **Common Mistake:** Saying all parse failures are returned to the client.
   - **How to Impress Interviewer:** Return partial graph plus parse coverage metadata.

82. **Question:** Are architecture graph keys unique?
   - **Ideal Answer:** **Implemented:** keys use only `file` basenames, so same-named files in different directories overwrite each other. **Recommended:** use repository-relative paths.
   - **Expected Follow-up:** What example commonly collides?
   - **Common Mistake:** Assuming Python module basenames are globally unique.
   - **How to Impress Interviewer:** Normalize modules while preserving package context.

83. **Question:** Are imports resolved to internal files?
   - **Ideal Answer:** **Implemented:** no; raw module names from `ast.Import`/`ImportFrom` are listed. **Recommended:** classify internal, standard-library, and third-party dependencies.
   - **Expected Follow-up:** How are relative imports represented?
   - **Common Mistake:** Calling raw import strings a complete dependency graph.
   - **How to Impress Interviewer:** Discuss aliasing, packages, and dynamic imports.

84. **Question:** Why should `visualize_graph` not run in an API worker?
   - **Ideal Answer:** **Implemented:** the function exists but routes do not call it; it uses blocking `plt.show()`. **Recommended:** render headlessly to an artifact outside request-critical code.
   - **Expected Follow-up:** What does the API return instead?
   - **Common Mistake:** Saying `/architecture` opens a plot.
   - **How to Impress Interviewer:** Keep presentation concerns out of backend workers.

85. **Question:** What coupling exists between frontend and backend architecture analysis?
   - **Ideal Answer:** **Implemented:** Streamlit calls `build_dependency_graph` directly after `/analyze` instead of using `/architecture`. **Recommended:** choose one service boundary to avoid duplicate clone/path logic.
   - **Expected Follow-up:** What inconsistency can result?
   - **Common Mistake:** Assuming every frontend feature uses HTTP.
   - **How to Impress Interviewer:** Identify backend bypass as deployment and contract debt.

86. **Question:** What repository-name bug exists between backend and frontend?
   - **Ideal Answer:** **Implemented:** backend removes `.git`, while frontend derives `repo_name` without removing it before constructing `data/...`. **Recommended:** return canonical repository/analysis identity from `/analyze`.
   - **Expected Follow-up:** What URL triggers it?
   - **Common Mistake:** Duplicating URL parsing in both layers.
   - **How to Impress Interviewer:** Make server responses authoritative for resource locations.

87. **Question:** Should local filesystem paths appear in API responses?
   - **Ideal Answer:** **Implemented:** analyze responses do not expose them, but future citations could inherit absolute chunk paths. **Recommended:** expose repository-relative logical paths only.
   - **Expected Follow-up:** Why are absolute paths sensitive?
   - **Common Mistake:** Returning implementation paths for client convenience.
   - **How to Impress Interviewer:** Separate storage locator from public resource identifier.

88. **Question:** How should data cleanup work?
   - **Ideal Answer:** **Implemented:** cloned repositories remain under `data` indefinitely and no cleanup policy exists. **Recommended:** track ownership, retention, quotas, and safe recursive deletion by server-generated ID.
   - **Expected Follow-up:** When can cleanup race with active reads?
   - **Common Mistake:** Deleting paths reconstructed from user input.
   - **How to Impress Interviewer:** Use leases/reference counts and auditable lifecycle events.

89. **Question:** Is caching implemented beyond clone reuse?
   - **Ideal Answer:** **Implemented:** only an existing directory avoids recloning; embeddings and FAISS are rebuilt. **Recommended:** cache by commit SHA, chunker version, and embedding model version.
   - **Expected Follow-up:** What invalidates the cache?
   - **Common Mistake:** Caching solely by repository URL.
   - **How to Impress Interviewer:** Use content-addressed artifacts and atomic manifests.

90. **Question:** How would you support incremental re-indexing?
   - **Ideal Answer:** **Implemented:** the whole repository is reprocessed. **Recommended:** diff commits, retain stable chunk IDs, re-embed changed chunks, and rebuild or update the index safely.
   - **Expected Follow-up:** Can `IndexFlatL2` delete arbitrary vectors easily?
   - **Common Mistake:** Ignoring moved/deleted files.
   - **How to Impress Interviewer:** Keep a metadata mapping independent of FAISS row positions.

91. **Question:** What backpressure strategy exists?
   - **Ideal Answer:** **Implemented:** none; each request can start expensive work. **Recommended:** bound concurrent clones/embeddings/LLM calls and reject or queue excess demand.
   - **Expected Follow-up:** Why are rate limits alone insufficient?
   - **Common Mistake:** Letting threadpool growth define capacity.
   - **How to Impress Interviewer:** Use separate bulkheads for CPU, disk, and upstream calls.

92. **Question:** How does synchronous embedding affect concurrency?
   - **Ideal Answer:** **Implemented:** model encoding runs inside a synchronous handler and occupies worker/thread resources, potentially contending for CPU. **Recommended:** isolate CPU inference in dedicated workers with bounded concurrency.
   - **Expected Follow-up:** Would more Uvicorn workers always help?
   - **Common Mistake:** Ignoring duplicated model memory.
   - **How to Impress Interviewer:** Capacity-plan from CPU cores, RAM, and model batching.

93. **Question:** Could embedding requests be batched?
   - **Ideal Answer:** **Implemented:** all chunk texts from one analysis are passed to one `model.encode` call, but cross-request batching is absent. **Recommended:** benchmark bounded batches and memory limits.
   - **Expected Follow-up:** What can one giant batch do?
   - **Common Mistake:** Assuming a Python list means optimal device batching.
   - **How to Impress Interviewer:** Tune batch size using throughput and peak RSS.

94. **Question:** How should API configuration be managed?
   - **Ideal Answer:** **Implemented:** Groq uses environment loading; API URL is hard-coded in frontend; other limits are literals. **Recommended:** define validated settings with environment-specific values.
   - **Expected Follow-up:** Should `.env` be used in production?
   - **Common Mistake:** Committing secrets alongside defaults.
   - **How to Impress Interviewer:** Fail fast on required settings and expose safe config diagnostics.

95. **Question:** What dependency-version risk exists?
   - **Ideal Answer:** **Implemented:** `requirements.txt` lists unpinned package names. **Recommended:** pin or lock tested versions and automate vulnerability/update review.
   - **Expected Follow-up:** Why can FastAPI/Pydantic compatibility matter?
   - **Common Mistake:** Assuming latest transitive versions are reproducible.
   - **How to Impress Interviewer:** Separate human constraints from a fully resolved lock.

96. **Question:** How should response compression be considered?
   - **Ideal Answer:** **Implemented:** no compression middleware is configured. **Recommended:** enable proxy or middleware compression for sizable JSON after measuring CPU and security implications.
   - **Expected Follow-up:** Which responses benefit?
   - **Common Mistake:** Compressing tiny answers indiscriminately.
   - **How to Impress Interviewer:** Mention graph payloads, thresholds, and BREACH-sensitive secrets.

97. **Question:** What headers should a hardened API add?
   - **Ideal Answer:** **Implemented:** no custom security or caching headers are configured. **Recommended:** set appropriate cache policy, content-type protections, and proxy-level security headers based on deployment.
   - **Expected Follow-up:** Should `/ask` responses be cached publicly?
   - **Common Mistake:** Copying browser-page headers without threat modeling an API.
   - **How to Impress Interviewer:** Mark potentially source-derived answers private/no-store.

98. **Question:** What would a production analysis resource API look like?
   - **Ideal Answer:** **Implemented:** analysis mutates one singleton and returns immediate summary. **Recommended:** `POST /v1/analyses`, `GET /v1/analyses/{id}`, and repository-scoped query endpoints.
   - **Expected Follow-up:** Where does architecture fit?
   - **Common Mistake:** Adding endpoints without defining lifecycle.
   - **How to Impress Interviewer:** Include revision, status, artifacts, ownership, and expiry.

99. **Question:** What is the highest-priority backend correctness fix?
   - **Ideal Answer:** **Implemented:** global, partially updated singleton state makes requests unsafe and can mix repositories. **Recommended:** introduce immutable analysis-scoped state with IDs before scaling workers.
   - **Expected Follow-up:** Why prioritize this over formatting?
   - **Common Mistake:** Starting with cosmetic route refactors.
   - **How to Impress Interviewer:** Tie the fix to determinism, tenancy, concurrency, and deployability.

100. **Question:** How would you evolve this backend without a risky rewrite?
   - **Ideal Answer:** **Implemented:** the modules already define useful stage boundaries. **Recommended:** add typed contracts and tests, wrap stages in an analysis service/job, externalize state, then add security and observability incrementally.
   - **Expected Follow-up:** What would remain unchanged first?
   - **Common Mistake:** Replacing FastAPI, FAISS, and all modules simultaneously.
   - **How to Impress Interviewer:** Propose compatibility tests and measurable migration checkpoints.
