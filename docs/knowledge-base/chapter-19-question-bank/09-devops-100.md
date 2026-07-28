# DevOps Interview Question Bank — 100 Questions

`[Actual]` describes the repository today. `[Proposed]` is a production recommendation, not an implemented feature.

## Current State

### 1. [Actual] How is the application started today?
**Question:** How is the application started today?
**Ideal Answer:** `run.sh` backgrounds `uvicorn app.api:app --reload` and then runs `streamlit run frontend.py` in the foreground.
**Expected Follow-up:** What happens if either process exits?
**Common Mistake:** Claiming a process manager supervises both services.
**How to Impress Interviewer:** Note that the script neither records the backend PID nor propagates signals to both children.

### 2. [Actual] Why is `--reload` unsuitable for production?
**Question:** Why is the current Uvicorn invocation unsuitable for production?
**Ideal Answer:** `--reload` watches files and spawns a reloader process; it is a development convenience with extra overhead and surprising process behavior.
**Expected Follow-up:** What would replace it?
**Common Mistake:** Treating reload as automatic crash recovery.
**How to Impress Interviewer:** Propose explicit workers under an orchestrator, with readiness and graceful termination.

### 3. [Actual] Which process owns the shell lifecycle?
**Question:** Which process keeps `run.sh` attached to the terminal?
**Ideal Answer:** Streamlit does, because Uvicorn is backgrounded with `&` and Streamlit is the final foreground command.
**Expected Follow-up:** How does Ctrl-C affect Uvicorn?
**Common Mistake:** Assuming Bash automatically cleans up the background child.
**How to Impress Interviewer:** Explain why a `trap` plus `wait` is needed for reliable signal forwarding.

### 4. [Actual] What startup dependency exists between the services?
**Question:** Does `run.sh` verify that FastAPI is ready before Streamlit starts?
**Ideal Answer:** No. It starts Uvicorn and immediately starts Streamlit; frontend requests can race backend startup.
**Expected Follow-up:** How would you gate readiness?
**Common Mistake:** Saying process creation means the API is ready.
**How to Impress Interviewer:** Use a health endpoint and bounded readiness polling, not a fixed sleep.

### 5. [Actual] How is the backend address configured?
**Question:** How does the frontend discover the backend?
**Ideal Answer:** `frontend.py` hard-codes `API_URL = "http://127.0.0.1:8000"`.
**Expected Follow-up:** Why does that break in containers?
**Common Mistake:** Assuming `127.0.0.1` reaches another container.
**How to Impress Interviewer:** Propose an environment variable with service-DNS default and startup validation.

### 6. [Actual] What port configuration is present?
**Question:** Where are backend and frontend ports configured?
**Ideal Answer:** The backend relies on Uvicorn's default port 8000; Streamlit also uses its defaults; neither is explicit in `run.sh`.
**Expected Follow-up:** What operational risk follows?
**Common Mistake:** Claiming ports are documented as deployment contracts.
**How to Impress Interviewer:** Make host and port explicit and configurable per environment.

### 7. [Actual] Is there a CI pipeline?
**Question:** What continuous-integration automation exists in this repository?
**Ideal Answer:** None is present; there is no `.github/workflows` configuration or equivalent CI manifest.
**Expected Follow-up:** What first checks would you add?
**Common Mistake:** Calling `run.sh` CI.
**How to Impress Interviewer:** Prioritize install, lint, unit tests, dependency audit, and a minimal API smoke test.

### 8. [Actual] Is the project containerized?
**Question:** What container support exists today?
**Ideal Answer:** None is present: no Dockerfile, Compose file, or `.dockerignore`.
**Expected Follow-up:** Would you build one or two images?
**Common Mistake:** Assuming Python requirements imply a container image.
**How to Impress Interviewer:** Separate API and Streamlit runtime images while sharing a pinned dependency base.

### 9. [Actual] Are dependencies reproducible?
**Question:** Does `requirements.txt` produce deterministic installs?
**Ideal Answer:** No; packages are listed without versions or hashes, so installs can change over time.
**Expected Follow-up:** How would you lock them?
**Common Mistake:** Saying package names alone are reproducible.
**How to Impress Interviewer:** Generate a reviewed lock with hashes and automate controlled update PRs.

### 10. [Actual] Is the Python runtime pinned?
**Question:** Where is the supported Python version declared?
**Ideal Answer:** It is not declared in a runtime file, package metadata, container, or CI matrix.
**Expected Follow-up:** Why does that matter here?
**Common Mistake:** Assuming every dependency supports every Python release.
**How to Impress Interviewer:** Pin a production minor version and test the stated support range.

### 11. [Actual] How are secrets loaded?
**Question:** How does the Groq credential reach the application?
**Ideal Answer:** `qa_engine.py` calls `load_dotenv()` and reads `GROQ_API_KEY` from the environment.
**Expected Follow-up:** What occurs if it is absent?
**Common Mistake:** Claiming a managed secret store is already integrated.
**How to Impress Interviewer:** Validate required configuration at startup without logging secret values.

### 12. [Actual] What state survives a restart?
**Question:** Is the FAISS index durable?
**Ideal Answer:** No. `app.api.pipeline` holds chunks, index, and summary in process memory; restart requires re-analysis.
**Expected Follow-up:** What does that mean for deployments?
**Common Mistake:** Assuming the `data` clone directory restores the index.
**How to Impress Interviewer:** Separate durable job artifacts from ephemeral serving state and version their schema.

### 13. [Actual] Can multiple API workers share state?
**Question:** What happens if Uvicorn runs multiple workers?
**Ideal Answer:** Each worker gets its own `pipeline` dictionary, so `/analyze` and `/ask` may hit different, inconsistent states.
**Expected Follow-up:** What architecture supports scaling?
**Common Mistake:** Treating Python globals as cross-process storage.
**How to Impress Interviewer:** Put job metadata and indexes in shared storage, then route queries by repository/index ID.

### 14. [Actual] Can concurrent analyses interfere?
**Question:** How does the current API isolate simultaneous users?
**Ideal Answer:** It does not; every `/analyze` overwrites the single global pipeline used by all `/ask` calls.
**Expected Follow-up:** What API change is required?
**Common Mistake:** Assuming FastAPI creates a pipeline per request.
**How to Impress Interviewer:** Return an analysis ID and make all later operations explicitly address that immutable version.

### 15. [Actual] What deployment health signals exist?
**Question:** Does FastAPI expose liveness or readiness endpoints?
**Ideal Answer:** No dedicated health endpoints are defined; only `/analyze`, `/ask`, and `/architecture` exist.
**Expected Follow-up:** How should liveness differ from readiness?
**Common Mistake:** Using an expensive `/analyze` call as a probe.
**How to Impress Interviewer:** Keep liveness local and make readiness check required model/config dependencies without doing real work.

### 16. [Actual] What observability exists?
**Question:** What logging, metrics, or tracing is configured?
**Ideal Answer:** Only ad hoc `print` statements in repository cloning and framework defaults; no structured logs, metrics, or tracing.
**Expected Follow-up:** Which metrics matter first?
**Common Mistake:** Calling Streamlit messages production telemetry.
**How to Impress Interviewer:** Track clone, parse, embedding, retrieval, and LLM latency separately with correlation IDs.

### 17. [Actual] How are errors surfaced?
**Question:** How does the frontend handle backend failures?
**Ideal Answer:** It checks only the HTTP status and shows a generic message; request timeouts and connection exceptions are not handled.
**Expected Follow-up:** What operational impact follows?
**Common Mistake:** Assuming `requests.post` always returns a response.
**How to Impress Interviewer:** Add bounded timeouts, typed error responses, retries only for safe transient failures, and request IDs.

### 18. [Actual] Are outbound calls bounded?
**Question:** Does Streamlit set timeouts on calls to FastAPI?
**Ideal Answer:** No; both `requests.post` calls omit `timeout`, so the UI can block indefinitely.
**Expected Follow-up:** Is one timeout enough for analysis?
**Common Mistake:** Applying aggressive retries to long, non-idempotent jobs.
**How to Impress Interviewer:** Convert analysis to an asynchronous job with status polling and phase-specific deadlines.

### 19. [Actual] Is repository analysis asynchronous?
**Question:** How is `/analyze` executed?
**Ideal Answer:** It is a synchronous endpoint that clones, reads, chunks, embeds, and indexes before replying.
**Expected Follow-up:** What production failure mode does this create?
**Common Mistake:** Assuming `def` endpoints make CPU-heavy work scalable.
**How to Impress Interviewer:** Move work to a bounded queue and return `202 Accepted` with a job ID.

### 20. [Actual] What resource-heavy startup occurs?
**Question:** When is the sentence-transformer model loaded?
**Ideal Answer:** At import time in `app.embedder`, so each API process loads `all-MiniLM-L6-v2` during startup.
**Expected Follow-up:** How does that affect workers?
**Common Mistake:** Assuming all workers share model memory.
**How to Impress Interviewer:** Measure memory per worker and use warmup/readiness or a dedicated embedding service.

### 21. [Actual] What external artifact is downloaded?
**Question:** What runtime dependency may require network access beyond Groq and GitHub?
**Ideal Answer:** SentenceTransformers may download the Hugging Face model when it is not cached.
**Expected Follow-up:** How would you make deployment predictable?
**Common Mistake:** Assuming `pip install` includes model weights.
**How to Impress Interviewer:** Pin and prefetch a verified model revision during image build.

### 22. [Actual] Where are repositories stored?
**Question:** Where does repository cloning write data?
**Ideal Answer:** `clone_repository` defaults to the relative `data/<repo_name>` path.
**Expected Follow-up:** What does relative storage imply?
**Common Mistake:** Treating it as a managed persistent volume.
**How to Impress Interviewer:** Configure an absolute work root, quotas, lifecycle cleanup, and per-job directories.

### 23. [Actual] How are repeated repository requests handled?
**Question:** What happens when `data/<repo_name>` already exists?
**Ideal Answer:** The loader returns the existing path without fetching updates or verifying its origin or revision.
**Expected Follow-up:** What consistency issue follows?
**Common Mistake:** Calling this a reliable cache.
**How to Impress Interviewer:** Key artifacts by canonical URL plus commit SHA and make cache freshness explicit.

### 24. [Actual] Is disk usage managed?
**Question:** What cleanup policy exists for cloned repositories?
**Ideal Answer:** None is implemented; cloned repositories can accumulate under `data`.
**Expected Follow-up:** How would you prevent disk exhaustion?
**Common Mistake:** Assuming process restart clears disk.
**How to Impress Interviewer:** Enforce per-job and global quotas, TTL cleanup, and disk-pressure alerts.

### 25. [Actual] Are file-processing limits configured?
**Question:** Does the parser bound repository size, file count, or file size?
**Ideal Answer:** No; it recursively reads every supported source file into memory.
**Expected Follow-up:** What should fail fast?
**Common Mistake:** Relying only on extension filtering.
**How to Impress Interviewer:** Add admission limits before clone and cumulative byte/chunk budgets during parsing.

### 26. [Actual] How does chunking affect capacity?
**Question:** What operational characteristic follows from 500-character chunks?
**Ideal Answer:** Chunk count grows linearly with source size and all chunks are embedded in one batch, increasing memory and latency.
**Expected Follow-up:** How would you control peak memory?
**Common Mistake:** Confusing character chunks with token-aware bounded batches.
**How to Impress Interviewer:** Stream files, batch embeddings, and emit stage-level capacity metrics.

### 27. [Actual] What happens with an empty analysis?
**Question:** How does index construction handle zero chunks?
**Ideal Answer:** `build_index` accesses `embeddings[0]`, so an empty supported-code set can fail.
**Expected Follow-up:** Where should this be detected?
**Common Mistake:** Expecting FAISS to infer dimensions from an empty array.
**How to Impress Interviewer:** Validate after parsing and return a stable domain error before embedding/indexing.

### 28. [Actual] Are deployments rollback-ready?
**Question:** What release artifacts or versioning exist?
**Ideal Answer:** None are defined; the project is launched from source and has no image tag, build metadata, or release workflow.
**Expected Follow-up:** What enables rollback?
**Common Mistake:** Treating Git history alone as a deployed artifact registry.
**How to Impress Interviewer:** Produce immutable images labeled with commit SHA and retain previous compatible artifacts.

### 29. [Actual] Is database migration tooling needed today?
**Question:** Are there schema migrations in the current application?
**Ideal Answer:** No database is used; current state is in-memory plus cloned files.
**Expected Follow-up:** When would migrations become relevant?
**Common Mistake:** Inventing a database that is not in the repository.
**How to Impress Interviewer:** State that proposed job metadata persistence would require backward-compatible migrations.

### 30. [Actual] How is configuration documented?
**Question:** Which required environment variable is documented?
**Ideal Answer:** README documents `GROQ_API_KEY`; backend URL, ports, model, storage path, and operational limits are not configurable contracts.
**Expected Follow-up:** What configuration policy would you adopt?
**Common Mistake:** Putting production secrets in a committed `.env`.
**How to Impress Interviewer:** Maintain a non-secret example file plus startup schema validation.

### 31. [Actual] What test automation is visible?
**Question:** What tests run before deployment?
**Ideal Answer:** No test suite or automated test command is present in the inspected repository.
**Expected Follow-up:** What is the minimum release gate?
**Common Mistake:** Calling manual UI use a regression suite.
**How to Impress Interviewer:** Start with pure pipeline unit tests and mocked Git/Groq integration tests.

### 32. [Actual] What linting or formatting gates exist?
**Question:** Are code-quality tools configured?
**Ideal Answer:** No formatter, linter, type checker, or pre-commit configuration is present.
**Expected Follow-up:** Which checks provide quick value?
**Common Mistake:** Adding many tools without making CI authoritative.
**How to Impress Interviewer:** Use a small deterministic toolchain and pin its versions.

### 33. [Actual] How are frontend assets obtained?
**Question:** Does the Streamlit UI depend on a third-party asset at runtime?
**Ideal Answer:** Yes; injected HTML links Google Fonts, so appearance and page load depend on an external CDN.
**Expected Follow-up:** How would an offline deployment behave?
**Common Mistake:** Assuming Python packaging contains those fonts.
**How to Impress Interviewer:** Self-host pinned assets or define a deliberate fallback and CSP policy.

### 34. [Actual] Is the backend bound for remote access?
**Question:** Does `run.sh` explicitly bind Uvicorn to all interfaces?
**Ideal Answer:** No; it uses Uvicorn defaults, normally `127.0.0.1`, matching the local-only frontend URL.
**Expected Follow-up:** What changes behind a reverse proxy?
**Common Mistake:** Exposing a development server directly to the internet.
**How to Impress Interviewer:** Bind on the internal interface and terminate TLS at a controlled ingress.

### 35. [Actual] Are graceful shutdown semantics defined?
**Question:** What happens to an in-flight analysis during shutdown?
**Ideal Answer:** There is no job persistence, cancellation protocol, or drain logic; termination can lose all in-memory progress.
**Expected Follow-up:** How should deploys drain work?
**Common Mistake:** Assuming synchronous requests survive process termination.
**How to Impress Interviewer:** Stop intake, checkpoint idempotent stages, honor a grace period, then requeue safely.

### 36. [Actual] Is there backpressure?
**Question:** What limits simultaneous clone and embedding jobs?
**Ideal Answer:** No application-level queue, concurrency cap, or rate limit exists.
**Expected Follow-up:** Why is autoscaling alone insufficient?
**Common Mistake:** Allowing every request to start expensive work immediately.
**How to Impress Interviewer:** Bound queue depth and worker concurrency based on memory, CPU, disk, and external quotas.

### 37. [Actual] How are logs correlated?
**Question:** Can a clone message be tied to a frontend request?
**Ideal Answer:** No; current `print` messages contain no request, user, repository, or job identifier.
**Expected Follow-up:** What fields would you add?
**Common Mistake:** Logging full URLs when they may contain credentials.
**How to Impress Interviewer:** Use structured events with sanitized repo host, job ID, stage, duration, and outcome.

### 38. [Actual] What service-level objective exists?
**Question:** Is availability or latency formally targeted?
**Ideal Answer:** No SLO, error budget, or performance baseline is documented.
**Expected Follow-up:** What would you measure first?
**Common Mistake:** Promising arbitrary “five nines” for a demo architecture.
**How to Impress Interviewer:** Separate interactive query SLOs from long-running analysis completion objectives.

### 39. [Actual] Is environment parity enforced?
**Question:** How do development and production environments differ today?
**Ideal Answer:** Only a local development path is defined; there is no production manifest to compare.
**Expected Follow-up:** What would establish parity?
**Common Mistake:** Assuming a developer virtual environment is deployable infrastructure.
**How to Impress Interviewer:** Run the same immutable artifacts locally, in CI, and in production with configuration-only differences.

### 40. [Actual] What is the present deployment maturity?
**Question:** Summarize the current operational posture without overstating it.
**Ideal Answer:** It is a local demo: one shell script, development reload, unpinned dependencies, process-local state, and no CI or container definitions.
**Expected Follow-up:** What is the first production milestone?
**Common Mistake:** Describing proposed Kubernetes components as existing.
**How to Impress Interviewer:** Define a staged path: reproducible build, tests, single-node deployment, observability, then scale.

## Proposed Production Practices

### 41. [Proposed] What should the first CI workflow do?
**Question:** Design the smallest useful CI pipeline for this repository.
**Ideal Answer:** Install from a pinned lock, lint, test, audit dependencies, and run API import/smoke checks on every pull request.
**Expected Follow-up:** What should block merging?
**Common Mistake:** Starting with deployment before reliable verification.
**How to Impress Interviewer:** Cache safely by lockfile hash and cancel superseded branch runs.

### 42. [Proposed] How should CI handle the embedding model?
**Question:** Should every unit-test job download `all-MiniLM-L6-v2`?
**Ideal Answer:** No; mock model boundaries in unit tests and reserve a cached, pinned-model integration job for representative validation.
**Expected Follow-up:** How do you prevent mock-only confidence?
**Common Mistake:** Either downloading large weights everywhere or never testing the real model.
**How to Impress Interviewer:** Compare embedding dimensions and a small retrieval-quality fixture in a scheduled test.

### 43. [Proposed] How should dependencies be locked?
**Question:** What dependency-management improvement fits this project?
**Ideal Answer:** Declare direct constraints, compile a transitive lock with hashes, and use automated reviewed updates.
**Expected Follow-up:** How are security patches delivered quickly?
**Common Mistake:** Hand-pinning only top-level packages.
**How to Impress Interviewer:** Maintain separate runtime and development locks with reproducible CI verification.

### 44. [Proposed] What should the API image contain?
**Question:** Describe a production API container.
**Ideal Answer:** A slim pinned Python base, locked runtime packages, pre-fetched pinned model, application code, non-root user, and no compiler/cache residue.
**Expected Follow-up:** Why use a multi-stage build?
**Common Mistake:** Copying the local virtual environment into the image.
**How to Impress Interviewer:** Emit an SBOM and image provenance alongside the digest.

### 45. [Proposed] What should the frontend image contain?
**Question:** Why use a separate Streamlit image?
**Ideal Answer:** It has a distinct command, scaling profile, network exposure, and failure domain from FastAPI.
**Expected Follow-up:** Can both share dependency layers?
**Common Mistake:** Running both under one container shell script in production.
**How to Impress Interviewer:** Share a versioned base while independently releasing the two services.

### 46. [Proposed] How should container processes run?
**Question:** What should replace `run.sh` inside production containers?
**Ideal Answer:** One foreground process per container, invoked directly with exec-form commands and managed by the platform.
**Expected Follow-up:** How are signals handled?
**Common Mistake:** Backgrounding Uvicorn inside a container.
**How to Impress Interviewer:** Verify SIGTERM draining in an automated deployment test.

### 47. [Proposed] What local orchestration is useful?
**Question:** What should a Compose setup provide?
**Ideal Answer:** API and frontend services, service-DNS backend URL, health checks, environment injection, and bounded development volumes.
**Expected Follow-up:** Should Compose be the production orchestrator?
**Common Mistake:** Encoding production secrets in the Compose file.
**How to Impress Interviewer:** Keep Compose as a parity-oriented developer profile built from production Dockerfiles.

### 48. [Proposed] How should API configuration work?
**Question:** Replace the hard-coded backend URL design.
**Ideal Answer:** Read a validated `API_URL` environment setting, with local default only in development and an explicit production value.
**Expected Follow-up:** When is it validated?
**Common Mistake:** Silently falling back to localhost in production.
**How to Impress Interviewer:** Expose sanitized effective configuration in diagnostics.

### 49. [Proposed] What probes should the API expose?
**Question:** Define liveness, readiness, and startup checks.
**Ideal Answer:** Liveness checks the process loop, startup allows model warmup, and readiness confirms the service can accept work.
**Expected Follow-up:** Should readiness call Groq?
**Common Mistake:** Making every probe depend on external vendors.
**How to Impress Interviewer:** Report degraded dependencies separately and keep probes cheap and non-destructive.

### 50. [Proposed] What probes should Streamlit use?
**Question:** How should the frontend be health-checked?
**Ideal Answer:** Check its own HTTP health independently; backend reachability belongs in readiness only if the product cannot function without it.
**Expected Follow-up:** How do you avoid cascading restarts?
**Common Mistake:** Killing healthy frontend pods whenever Groq is unavailable.
**How to Impress Interviewer:** Surface dependency degradation to users while preserving static UI availability.

### 51. [Proposed] How should analysis become asynchronous?
**Question:** Design the production `/analyze` flow.
**Ideal Answer:** Validate and enqueue a job, return an ID, process stages in workers, persist status, and expose polling or events.
**Expected Follow-up:** What makes retries safe?
**Common Mistake:** Holding one HTTP connection through cloning and embedding.
**How to Impress Interviewer:** Use idempotency keys and stage checkpoints keyed by commit SHA.

### 52. [Proposed] What queue semantics are needed?
**Question:** Which delivery guarantee fits analysis jobs?
**Ideal Answer:** At-least-once delivery is practical if handlers are idempotent and artifacts are atomically published.
**Expected Follow-up:** How are duplicates handled?
**Common Mistake:** Claiming exactly-once execution from a normal queue.
**How to Impress Interviewer:** Separate duplicate execution from duplicate visible results.

### 53. [Proposed] How should analysis state be modeled?
**Question:** What replaces the global `pipeline` dictionary?
**Ideal Answer:** Durable metadata maps tenant, repository, commit, job, index artifact, state, and timestamps.
**Expected Follow-up:** Where do large indexes live?
**Common Mistake:** Storing large FAISS binaries directly in transactional rows by default.
**How to Impress Interviewer:** Store immutable artifacts in object storage and checksummed references in metadata.

### 54. [Proposed] How should index artifacts be versioned?
**Question:** What metadata must accompany a FAISS index?
**Ideal Answer:** Commit SHA, chunker version, embedding model/revision, vector dimension, distance metric, and artifact checksum.
**Expected Follow-up:** Why does model revision matter?
**Common Mistake:** Reusing an index with an incompatible query embedder.
**How to Impress Interviewer:** Make compatibility validation mandatory before loading.

### 55. [Proposed] How should releases be tagged?
**Question:** What constitutes an immutable release?
**Ideal Answer:** Images identified by digest and labeled with source commit, build time, dependency lock, and model revision.
**Expected Follow-up:** Why not deploy `latest`?
**Common Mistake:** Using a mutable branch tag as rollback evidence.
**How to Impress Interviewer:** Promote the same digest across environments.

### 56. [Proposed] What branching deployment flow fits?
**Question:** How should code move from pull request to production?
**Ideal Answer:** PR verification builds evidence; merge builds a signed artifact; staging validates it; an approval promotes the identical artifact.
**Expected Follow-up:** Where should environment config live?
**Common Mistake:** Rebuilding separately for production.
**How to Impress Interviewer:** Record deployment provenance and automated rollback criteria.

### 57. [Proposed] How should database migrations deploy?
**Question:** If job metadata gains a database, how should migrations run?
**Ideal Answer:** Use versioned, backward-compatible migrations as a controlled release step before dependent code.
**Expected Follow-up:** How do rolling deploys remain compatible?
**Common Mistake:** Letting every replica race to migrate on startup.
**How to Impress Interviewer:** Apply expand-migrate-contract across releases.

### 58. [Proposed] What deployment strategy is appropriate?
**Question:** Blue-green or rolling deployment?
**Ideal Answer:** Rolling is sufficient once state is externalized and versions are compatible; blue-green helps risky index/schema changes.
**Expected Follow-up:** What gates traffic?
**Common Mistake:** Choosing a strategy without readiness or rollback signals.
**How to Impress Interviewer:** Tie promotion to query error rate and latency, not merely pod health.

### 59. [Proposed] How should rollback work?
**Question:** What must a rollback preserve?
**Ideal Answer:** Revert to a known image digest while keeping metadata and index artifacts readable by that version.
**Expected Follow-up:** What if a migration is irreversible?
**Common Mistake:** Assuming code rollback reverses data changes.
**How to Impress Interviewer:** Test backward compatibility and prefer roll-forward for destructive migrations.

### 60. [Proposed] What should be logged?
**Question:** Define structured logging for the pipeline.
**Ideal Answer:** Emit request/job ID, stage, sanitized repo identifier, commit SHA, duration, counts, outcome, and error class.
**Expected Follow-up:** What must not be logged?
**Common Mistake:** Logging source chunks, prompts, tokens, or credential-bearing URLs.
**How to Impress Interviewer:** Define retention and redaction tests as code.

### 61. [Proposed] What metrics should analysis expose?
**Question:** Which analysis metrics support capacity planning?
**Ideal Answer:** Queue depth, active jobs, clone bytes/time, files/chunks, embedding batch latency, index size, failures, and retries.
**Expected Follow-up:** Which are high-cardinality?
**Common Mistake:** Labeling metrics with raw repository URLs or job IDs.
**How to Impress Interviewer:** Keep identifiers in traces/logs and metrics labels bounded.

### 62. [Proposed] What metrics should querying expose?
**Question:** Which `/ask` metrics matter?
**Ideal Answer:** Retrieval latency, LLM latency, total latency, retrieved count, token usage, vendor errors, and success rate.
**Expected Follow-up:** How would you define an SLO?
**Common Mistake:** Measuring only average latency.
**How to Impress Interviewer:** Use percentile latency and separate vendor-caused degradation.

### 63. [Proposed] Where should traces span?
**Question:** What distributed trace boundaries are useful?
**Ideal Answer:** Frontend request, API validation, queue publish, worker stages, storage calls, retrieval, and Groq invocation.
**Expected Follow-up:** How is async context propagated?
**Common Mistake:** Creating unrelated traces at the queue boundary.
**How to Impress Interviewer:** Propagate trace context in job metadata while excluding sensitive prompt content.

### 64. [Proposed] What alerts are actionable?
**Question:** Which initial alerts avoid noise?
**Ideal Answer:** Sustained query SLO burn, growing oldest-job age, disk pressure, crash loops, and elevated external-service failures.
**Expected Follow-up:** Why not alert on every exception?
**Common Mistake:** Paging on low-impact single events.
**How to Impress Interviewer:** Use multi-window burn-rate alerts tied to user impact.

### 65. [Proposed] How should dashboards be organized?
**Question:** What operational views would you build?
**Ideal Answer:** Service health, analysis funnel, query path, capacity, and external dependency panels.
**Expected Follow-up:** Which view is primary during incidents?
**Common Mistake:** Building a dashboard from every available metric.
**How to Impress Interviewer:** Link dashboards to runbooks and deployment markers.

### 66. [Proposed] How should worker concurrency be set?
**Question:** How do you size embedding workers?
**Ideal Answer:** Benchmark memory and CPU per batch, then cap concurrency within node headroom and external quotas.
**Expected Follow-up:** Can CPU percentage alone drive scaling?
**Common Mistake:** Setting concurrency equal to request count.
**How to Impress Interviewer:** Account for model memory and peak repository expansion.

### 67. [Proposed] How should autoscaling work?
**Question:** What signal should scale analysis workers?
**Ideal Answer:** Queue age and depth per effective worker capacity, constrained by memory and vendor limits.
**Expected Follow-up:** What scales API replicas?
**Common Mistake:** Scaling workers solely on CPU after queues are already delayed.
**How to Impress Interviewer:** Model cold-start time and set a bounded maximum to protect dependencies.

### 68. [Proposed] How should the query tier scale?
**Question:** What must change before horizontal query scaling?
**Ideal Answer:** Remove global state, load versioned indexes from shared storage/cache, and make requests identify an analysis.
**Expected Follow-up:** Should every replica load every index?
**Common Mistake:** Replicating unbounded indexes into each process.
**How to Impress Interviewer:** Use an LRU index cache with memory budgets and observable hit rates.

### 69. [Proposed] How should repository workspaces be isolated?
**Question:** What filesystem model should workers use?
**Ideal Answer:** A unique temporary directory per job with strict permissions, quotas, and guaranteed cleanup.
**Expected Follow-up:** What if cleanup fails?
**Common Mistake:** Reusing `data/<repo_name>` across tenants.
**How to Impress Interviewer:** Add reconciliation that removes orphaned workspaces after a safe TTL.

### 70. [Proposed] How should disk capacity be protected?
**Question:** What controls prevent clone-driven disk exhaustion?
**Ideal Answer:** Preflight size policy, shallow/filtered clone where valid, filesystem quota, free-space checks, and cleanup.
**Expected Follow-up:** Can remote repository size always be known?
**Common Mistake:** Depending on one preflight estimate.
**How to Impress Interviewer:** Enforce streaming hard limits even when metadata is inaccurate.

### 71. [Proposed] How should memory be protected?
**Question:** What changes reduce analysis memory peaks?
**Ideal Answer:** Stream parsing, bounded embedding batches, artifact spill, worker memory limits, and early rejection of oversized jobs.
**Expected Follow-up:** What happens on OOM?
**Common Mistake:** Retrying identical oversized jobs indefinitely.
**How to Impress Interviewer:** Classify deterministic resource-limit failures as non-retryable.

### 72. [Proposed] How should timeouts be layered?
**Question:** Define timeout policy across the system.
**Ideal Answer:** Use short connect timeouts, bounded per-stage deadlines, an overall job deadline, and query-specific LLM deadlines.
**Expected Follow-up:** How do retries consume the budget?
**Common Mistake:** Giving every retry a fresh full timeout.
**How to Impress Interviewer:** Pass a remaining deadline through each stage.

### 73. [Proposed] Which retries are safe?
**Question:** Where should retries be applied?
**Ideal Answer:** Retry transient Git, storage, queue, and Groq errors with jitter when operations are idempotent.
**Expected Follow-up:** Which failures should not retry?
**Common Mistake:** Retrying validation, quota, or deterministic parsing failures.
**How to Impress Interviewer:** Bound attempts and send exhausted jobs to an inspectable dead-letter path.

### 74. [Proposed] How should circuit breaking work?
**Question:** What should happen during a Groq outage?
**Ideal Answer:** Fail query generation quickly after a threshold, preserve retrieval capability, and expose degraded status.
**Expected Follow-up:** Does analysis also depend on Groq?
**Common Mistake:** Stopping repository embedding because answer generation is unavailable.
**How to Impress Interviewer:** Isolate dependency health by feature path.

### 75. [Proposed] How should idempotency work?
**Question:** How can duplicate analyze submissions be controlled?
**Ideal Answer:** Accept an idempotency key and map equivalent canonical repo-plus-commit requests to one job/artifact.
**Expected Follow-up:** What is the key's retention period?
**Common Mistake:** Deduplicating only by repository basename.
**How to Impress Interviewer:** Distinguish safe cache reuse from an explicit forced re-analysis.

### 76. [Proposed] How should cache invalidation work?
**Question:** When is an existing index reusable?
**Ideal Answer:** Only when repo commit, parser/chunker version, embedding revision, and relevant policy match.
**Expected Follow-up:** What about updated default branches?
**Common Mistake:** Treating a repository URL as immutable content.
**How to Impress Interviewer:** Resolve and persist the commit before cache lookup.

### 77. [Proposed] What backup policy is needed?
**Question:** What should be backed up?
**Ideal Answer:** Durable metadata, configuration history, and expensive immutable index artifacts according to recovery objectives; temporary clones need not be.
**Expected Follow-up:** How are backups tested?
**Common Mistake:** Backing up caches without verifying restore.
**How to Impress Interviewer:** Run periodic restore drills with checksum and compatibility validation.

### 78. [Proposed] What disaster-recovery objectives fit?
**Question:** Define realistic RPO and RTO for this service.
**Ideal Answer:** Set them by data value: metadata needs tighter recovery; rebuildable indexes may tolerate a larger RPO if source commits remain accessible.
**Expected Follow-up:** What about unavailable source repositories?
**Common Mistake:** Assigning one objective to every artifact.
**How to Impress Interviewer:** Classify artifacts by rebuild cost and source durability.

### 79. [Proposed] How should secrets be delivered?
**Question:** What replaces production `.env` files?
**Ideal Answer:** A managed secret store injects short-lived or rotated credentials at runtime with least-privilege access.
**Expected Follow-up:** How does rotation avoid downtime?
**Common Mistake:** Baking `GROQ_API_KEY` into the image.
**How to Impress Interviewer:** Support overlapping credential versions and audit access without exposing values.

### 80. [Proposed] How should environments be separated?
**Question:** What isolation is needed among development, staging, and production?
**Ideal Answer:** Separate credentials, queues, storage namespaces, domains, quotas, and deployment permissions.
**Expected Follow-up:** Can staging use production repositories?
**Common Mistake:** Sharing one mutable `data` volume across environments.
**How to Impress Interviewer:** Use synthetic fixtures by default and governed exceptions for real data.

### 81. [Proposed] What infrastructure should be code?
**Question:** Which deployment components belong in IaC?
**Ideal Answer:** Networking, compute, storage, queues, secrets bindings, observability, policies, and service configuration.
**Expected Follow-up:** How is drift detected?
**Common Mistake:** Keeping manual console changes as undocumented fixes.
**How to Impress Interviewer:** Require reviewed plans and scheduled drift checks.

### 82. [Proposed] Is Kubernetes required?
**Question:** Should this project immediately adopt Kubernetes?
**Ideal Answer:** Not necessarily; a managed container platform can meet early needs with less operational burden.
**Expected Follow-up:** When does Kubernetes become justified?
**Common Mistake:** Equating production readiness with Kubernetes.
**How to Impress Interviewer:** Choose from workload, isolation, scaling, and team-operability evidence.

### 83. [Proposed] How should ingress be designed?
**Question:** What should be internet-facing?
**Ideal Answer:** A TLS-terminating ingress exposes only intended frontend/API routes; workers, queues, and artifact stores remain private.
**Expected Follow-up:** How are request limits enforced?
**Common Mistake:** Publishing Uvicorn directly.
**How to Impress Interviewer:** Enforce body size, rate limits, timeouts, and trusted proxy settings at ingress and app layers.

### 84. [Proposed] How should service networking work?
**Question:** How should Streamlit call FastAPI in production?
**Ideal Answer:** Through private service discovery using a stable internal name and encrypted/authenticated transport where required.
**Expected Follow-up:** Why not localhost?
**Common Mistake:** Coupling frontend and API replicas one-to-one.
**How to Impress Interviewer:** Make connection pools, DNS behavior, and failure telemetry explicit.

### 85. [Proposed] What release tests should run?
**Question:** What should staging validate beyond unit tests?
**Ideal Answer:** Startup, probes, clone fixture, indexing, query flow with mocked or controlled LLM, shutdown, and rollback.
**Expected Follow-up:** How do tests remain deterministic?
**Common Mistake:** Depending on arbitrary public repositories.
**How to Impress Interviewer:** Host a versioned fixture repository and assert artifact metadata.

### 86. [Proposed] What performance test is representative?
**Question:** How would you load-test this application?
**Ideal Answer:** Separate long analysis workloads from bursty queries and use small, medium, and policy-limit repository fixtures.
**Expected Follow-up:** What saturation signals matter?
**Common Mistake:** Testing only requests per second.
**How to Impress Interviewer:** Measure queue age, memory, disk, model contention, and tail latency.

### 87. [Proposed] How should chaos testing begin?
**Question:** Which failures are worth injecting first?
**Ideal Answer:** Groq timeout, Git failure, full disk, worker termination, and artifact-store unavailability.
**Expected Follow-up:** What behavior is expected?
**Common Mistake:** Random fault injection without hypotheses.
**How to Impress Interviewer:** Verify bounded retries, durable status, cleanup, and user-visible error classification.

### 88. [Proposed] How should canary releases be evaluated?
**Question:** What signals decide canary promotion?
**Ideal Answer:** Compare error rate, tail latency, worker failures, resource use, and retrieval correctness against baseline.
**Expected Follow-up:** How much traffic goes to canary?
**Common Mistake:** Promoting solely because containers remain running.
**How to Impress Interviewer:** Include a synthetic end-to-end analysis as a canary gate.

### 89. [Proposed] What runbooks are essential?
**Question:** Which incidents need documented response?
**Ideal Answer:** Queue backlog, Groq outage, disk pressure, bad deployment, corrupted index, and leaked credential.
**Expected Follow-up:** What makes a runbook useful?
**Common Mistake:** Writing architecture prose without executable checks.
**How to Impress Interviewer:** Include diagnosis queries, safe mitigations, rollback, escalation, and verification.

### 90. [Proposed] How should on-call ownership work?
**Question:** What operational ownership must accompany deployment?
**Ideal Answer:** Defined service owner, severity policy, alert routing, escalation, and post-incident review.
**Expected Follow-up:** Should every alert page?
**Common Mistake:** Treating observability as ownership.
**How to Impress Interviewer:** Tie pages to actionable user-impact symptoms and automate low-risk remediation.

### 91. [Proposed] How should costs be controlled?
**Question:** What are the main production cost drivers?
**Ideal Answer:** Embedding compute, model storage/memory, cloned disk, index storage, Groq tokens, and idle replicas.
**Expected Follow-up:** How are costs attributed?
**Common Mistake:** Optimizing only container CPU.
**How to Impress Interviewer:** Record per-job normalized usage without high-cardinality metric labels.

### 92. [Proposed] How should external quotas be managed?
**Question:** How should Groq rate limits influence design?
**Ideal Answer:** Centralize concurrency budgets, use queueing and backoff, expose quota exhaustion clearly, and avoid retry storms.
**Expected Follow-up:** What if tenants have different plans?
**Common Mistake:** Letting every replica independently consume the full assumed quota.
**How to Impress Interviewer:** Allocate tenant budgets under a global limiter.

### 93. [Proposed] How should artifact retention work?
**Question:** How long should clones and indexes be retained?
**Ideal Answer:** Delete temporary clones promptly; retain versioned indexes according to usage, cost, policy, and rebuildability.
**Expected Follow-up:** How is deletion made safe?
**Common Mistake:** Applying one TTL to active and orphaned artifacts.
**How to Impress Interviewer:** Use reference-aware lifecycle policies and auditable tombstones.

### 94. [Proposed] How should feature flags be used?
**Question:** Where could feature flags reduce release risk?
**Ideal Answer:** New chunkers, embedding models, retrieval parameters, and UI paths can be enabled gradually.
**Expected Follow-up:** What should not be a permanent flag?
**Common Mistake:** Using flags instead of compatible deployments.
**How to Impress Interviewer:** Assign owners and expiry dates, and include flag state in telemetry.

### 95. [Proposed] How should model upgrades deploy?
**Question:** How do you roll out a new embedding model?
**Ideal Answer:** Build separate versioned indexes, validate retrieval quality and cost, canary query traffic, then migrate explicitly.
**Expected Follow-up:** Can old indexes use new query vectors?
**Common Mistake:** Swapping the model under existing FAISS data.
**How to Impress Interviewer:** Support dual-read evaluation before committing migration.

### 96. [Proposed] How should API compatibility be managed?
**Question:** What prevents frontend/backend release coupling?
**Ideal Answer:** Versioned schemas, backward-compatible changes, contract tests, and independent readiness.
**Expected Follow-up:** How are breaking changes retired?
**Common Mistake:** Deploying both together and assuming atomic replacement.
**How to Impress Interviewer:** Measure old-version usage and publish a deprecation window.

### 97. [Proposed] How should provenance be captured?
**Question:** What evidence should accompany a production build?
**Ideal Answer:** Source commit, lockfile, builder identity, test results, SBOM, image digest, and signatures.
**Expected Follow-up:** Where is it verified?
**Common Mistake:** Storing provenance only in transient CI logs.
**How to Impress Interviewer:** Enforce verification at deployment admission.

### 98. [Proposed] What production `run.sh` replacement is simplest?
**Question:** If avoiding an orchestrator initially, what is the minimum safe deployment?
**Ideal Answer:** Two separately supervised services with pinned environments, explicit config, health checks, logs, restart policy, and graceful shutdown.
**Expected Follow-up:** Which supervisor could be used?
**Common Mistake:** Merely removing `--reload` from the existing script.
**How to Impress Interviewer:** Keep the design portable to later containerization.

### 99. [Proposed] What should the production-readiness checklist require?
**Question:** Name the release-blocking categories.
**Ideal Answer:** Reproducible build, tests, security scan, externalized state, limits, probes, telemetry, backup/rollback, and runbooks.
**Expected Follow-up:** Must every ideal feature ship at once?
**Common Mistake:** Treating a checklist as a substitute for risk assessment.
**How to Impress Interviewer:** Assign owners, evidence links, and risk-based exceptions with expiry.

### 100. [Proposed] What is the recommended delivery sequence?
**Question:** Prioritize the path from this demo to production.
**Ideal Answer:** First pin/build/test; then split services and configure them; next externalize jobs/artifacts; add limits and telemetry; finally automate safe deployment and scaling.
**Expected Follow-up:** Why not autoscale first?
**Common Mistake:** Adding orchestration before fixing shared global state.
**How to Impress Interviewer:** Make each stage independently operable and define measurable exit criteria.
