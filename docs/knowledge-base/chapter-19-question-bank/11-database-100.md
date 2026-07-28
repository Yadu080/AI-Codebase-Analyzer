# Database Interview Question Bank

The current system has no database. It builds one in-memory FAISS index through a global pipeline and writes cloned repositories to disk. Answers below distinguish that reality from proposed production designs.

## 1. What persistence exists today?
- **Question:** What persistence exists in the current analyzer?
- **Ideal Answer:** There is no database. Repository clones live on disk; embeddings and metadata feed one RAM-resident FAISS index owned by a global pipeline, so process loss removes indexed state.
- **Expected Follow-up:** Which artifacts can be rebuilt, and at what cost?
- **Common Mistake:** Calling FAISS or the clone directory a database.
- **How to Impress Interviewer:** Separate durable source artifacts, derived index state, and process-local coordination explicitly.

## 2. Why add a database?
- **Question:** What concrete problems would justify adding a database?
- **Ideal Answer:** Durable job history, multi-user isolation, resumability, auditability, metadata filtering, idempotency, and coordination across workers. A database should answer identified requirements, not merely modernize the stack.
- **Expected Follow-up:** Which requirement should be implemented first?
- **Common Mistake:** Proposing PostgreSQL without identifying a failing workflow.
- **How to Impress Interviewer:** Tie each new store to an owner, consistency need, retention policy, and measurable failure mode.

## 3. What should be stored first?
- **Question:** If persistence is introduced incrementally, what data should be stored first?
- **Ideal Answer:** Persist analysis jobs, repository identity, commit SHA, status transitions, configuration, timestamps, and artifact pointers. Keep large clones and reproducible embeddings outside transactional rows initially.
- **Expected Follow-up:** Why prioritize job metadata over vectors?
- **Common Mistake:** Migrating every in-memory object at once.
- **How to Impress Interviewer:** Choose the smallest schema that enables restart recovery and operational visibility.

## 4. Relational or document database?
- **Question:** Would you choose a relational or document database for analyzer metadata?
- **Ideal Answer:** Relational storage fits jobs, repositories, users, permissions, commits, and status constraints. JSON columns can hold evolving analyzer configuration without abandoning joins and transactions.
- **Expected Follow-up:** When would a document store be preferable?
- **Common Mistake:** Choosing based on payloads being JSON.
- **How to Impress Interviewer:** Explain access patterns, invariants, schema evolution, and operational expertise before naming a product.

## 5. Propose a minimal relational schema
- **Question:** What is a minimal production schema?
- **Ideal Answer:** `repositories`, `repository_versions`, `analysis_jobs`, `artifacts`, and `job_events`; add users and permissions only when tenancy requires them. Reference immutable commit SHAs and give jobs explicit states.
- **Expected Follow-up:** Which columns need uniqueness constraints?
- **Common Mistake:** Storing the whole analysis as one unstructured row.
- **How to Impress Interviewer:** Model immutable versions separately from mutable repository identity.

## 6. Natural keys or surrogate keys?
- **Question:** Should repository records use URLs or generated IDs as primary keys?
- **Ideal Answer:** Use stable surrogate IDs internally and a normalized provider/owner/name or canonical URL uniqueness constraint. URLs can change and may contain credentials or aliases.
- **Expected Follow-up:** How do you normalize SSH and HTTPS URLs?
- **Common Mistake:** Treating raw clone URLs as permanent identifiers.
- **How to Impress Interviewer:** Preserve provider-native IDs where available and redact secrets before persistence.

## 7. Model repository versions
- **Question:** How should branches and commits be represented?
- **Ideal Answer:** Store immutable commit SHAs as analyzed versions; branches are mutable references observed at a timestamp. A job records both requested ref and resolved SHA.
- **Expected Follow-up:** What happens after a force push?
- **Common Mistake:** Keying analysis only by branch name.
- **How to Impress Interviewer:** Make reproducibility depend on content identity, not a moving label.

## 8. Model job states
- **Question:** How would you model analysis job lifecycle?
- **Ideal Answer:** Use constrained states such as queued, cloning, parsing, embedding, indexing, completed, failed, and cancelled, with timestamps and a durable transition history.
- **Expected Follow-up:** Who is allowed to perform each transition?
- **Common Mistake:** Using a free-text status field with no transition rules.
- **How to Impress Interviewer:** Enforce transitions atomically and retain append-only events for diagnosis.

## 9. Store large artifacts
- **Question:** Should reports, clones, and serialized indexes be stored as database blobs?
- **Ideal Answer:** Usually store them in object or filesystem storage and persist content hashes, sizes, versions, and URIs transactionally. Small reports may remain inline when access and backup costs justify it.
- **Expected Follow-up:** How do you prevent dangling artifact references?
- **Common Mistake:** Putting arbitrary multi-gigabyte indexes into OLTP rows.
- **How to Impress Interviewer:** Describe staging, checksum verification, atomic publication, and garbage collection.

## 10. Normalize or denormalize?
- **Question:** How normalized should the metadata schema be?
- **Ideal Answer:** Normalize entities and invariants first; denormalize read-heavy summaries only after profiling. Derived counts should identify their source version and refresh semantics.
- **Expected Follow-up:** Which fields are safe to cache?
- **Common Mistake:** Treating normalization as an absolute goal.
- **How to Impress Interviewer:** State the write-amplification and staleness budget for each denormalized field.

## 11. What is atomicity?
- **Question:** Explain atomicity using an analysis completion example.
- **Ideal Answer:** Completion should publish all required metadata or none: mark artifacts ready and the job completed in one transaction, preventing a completed job from referencing missing records.
- **Expected Follow-up:** Can object-store publication join that transaction?
- **Common Mistake:** Defining atomicity as fast execution.
- **How to Impress Interviewer:** Use a staged artifact plus transactional outbox or final pointer swap across storage boundaries.

## 12. What is consistency in ACID?
- **Question:** What does ACID consistency mean here?
- **Ideal Answer:** Every committed transaction preserves declared invariants: valid status transitions, existing repository versions, unique idempotency keys, and completed jobs with publishable artifacts.
- **Expected Follow-up:** Is replication consistency the same concept?
- **Common Mistake:** Confusing ACID consistency with CAP consistency.
- **How to Impress Interviewer:** Distinguish application invariants from replica visibility guarantees.

## 13. What is isolation?
- **Question:** Why does transaction isolation matter for workers claiming jobs?
- **Ideal Answer:** Isolation prevents two workers from both believing they exclusively claimed the same job. An atomic conditional update or `FOR UPDATE SKIP LOCKED` can serialize claims.
- **Expected Follow-up:** Which isolation level is sufficient?
- **Common Mistake:** Reading status and updating it in separate unprotected operations.
- **How to Impress Interviewer:** Prefer a single compare-and-set statement and test concurrent claim races.

## 14. What is durability?
- **Question:** What durability guarantee should job completion have?
- **Ideal Answer:** Once acknowledged complete, metadata must survive process and host failure according to the database's configured commit and replication policy. Derived vectors may have a weaker rebuildable guarantee.
- **Expected Follow-up:** Does a successful client response prove replica durability?
- **Common Mistake:** Assuming any write API call implies durable media.
- **How to Impress Interviewer:** Define acknowledgment, WAL flush, replica quorum, and recovery-point objectives.

## 15. Choose an isolation level
- **Question:** Which isolation level would you use for analyzer metadata?
- **Ideal Answer:** Read committed often suffices with explicit constraints and atomic claims. Use repeatable read or serializable only for workflows whose multi-row decisions require stable snapshots.
- **Expected Follow-up:** What anomaly are you preventing?
- **Common Mistake:** Selecting serializable universally without throughput analysis.
- **How to Impress Interviewer:** Map each transaction to dirty-read, non-repeatable-read, phantom, and write-skew risks.

## 16. Prevent write skew
- **Question:** How could write skew affect quota enforcement?
- **Ideal Answer:** Concurrent jobs may each observe spare quota and both start. Lock the quota row, perform an atomic bounded increment, or use serializable isolation with retry.
- **Expected Follow-up:** How should serialization failures be handled?
- **Common Mistake:** Checking quota in application code before inserting.
- **How to Impress Interviewer:** Make the invariant executable as a constraint or conditional write.

## 17. Optimistic concurrency control
- **Question:** Where would optimistic concurrency control help?
- **Ideal Answer:** For infrequently contested job updates, include a version number and update only when the expected version matches; retry or reject stale writers.
- **Expected Follow-up:** When is pessimistic locking better?
- **Common Mistake:** Overwriting newer state after a stale read.
- **How to Impress Interviewer:** Return the conflicting current version and make retries idempotent.

## 18. Pessimistic locking
- **Question:** When would row locking be appropriate?
- **Ideal Answer:** Use short row locks for scarce, highly contested coordination such as leasing a job or updating a strict tenant quota. Never hold them during cloning or embedding.
- **Expected Follow-up:** How do you avoid deadlocks?
- **Common Mistake:** Keeping a transaction open around network and CPU work.
- **How to Impress Interviewer:** Lock in a consistent order and keep transactional sections bounded.

## 19. Deadlock handling
- **Question:** How should the service handle database deadlocks?
- **Ideal Answer:** Prevent predictable cycles with consistent lock ordering, then detect deadlock errors and retry the entire idempotent transaction with bounded jitter.
- **Expected Follow-up:** What should be logged?
- **Common Mistake:** Retrying individual statements inside a partially failed transaction.
- **How to Impress Interviewer:** Capture involved operation names and contention metrics without logging sensitive values.

## 20. Long-running work and transactions
- **Question:** Should cloning and embedding run inside a database transaction?
- **Ideal Answer:** No. Persist a lease or state transition, commit, perform work, then publish results in another short transaction. Long transactions retain locks and old row versions.
- **Expected Follow-up:** What if the worker dies between phases?
- **Common Mistake:** Equating workflow atomicity with one giant transaction.
- **How to Impress Interviewer:** Use a durable state machine, leases, heartbeats, and compensating cleanup.

## 21. ACID versus BASE
- **Question:** Compare ACID and BASE for this system.
- **Ideal Answer:** Core job state and authorization benefit from ACID invariants. Search indexes, metrics, and caches can be basically available and eventually consistent because they are derived and rebuildable.
- **Expected Follow-up:** Where is stale data unacceptable?
- **Common Mistake:** Treating ACID and BASE as mutually exclusive system-wide choices.
- **How to Impress Interviewer:** Assign consistency per data class and user-visible promise.

## 22. Eventual consistency
- **Question:** What eventual-consistency behavior is acceptable for vector search?
- **Ideal Answer:** A newly completed analysis may become searchable after a bounded indexing delay, provided the UI exposes indexing status and direct artifact retrieval remains correct.
- **Expected Follow-up:** How do you define the bound?
- **Common Mistake:** Saying “eventually” without a service objective.
- **How to Impress Interviewer:** Publish freshness watermarks and measure commit-to-searchable latency.

## 23. Read-your-writes
- **Question:** How can users see their just-completed analysis despite replica lag?
- **Ideal Answer:** Route the immediate read to the writer, use a session consistency token, or wait until a replica reaches the returned commit position.
- **Expected Follow-up:** Which approach scales best?
- **Common Mistake:** Randomly reading replicas after a write.
- **How to Impress Interviewer:** Provide monotonic session behavior without globally forcing primary reads.

## 24. CAP theorem
- **Question:** Explain CAP in the context of metadata replication.
- **Ideal Answer:** During a network partition, a distributed store must choose between serving every request and preserving a single consistent view. Without a partition, CAP does not force a choice.
- **Expected Follow-up:** Which side should job ownership choose?
- **Common Mistake:** Claiming a system permanently chooses only two of three.
- **How to Impress Interviewer:** Discuss partition behavior operation by operation, not with a product label.

## 25. CP operations
- **Question:** Which analyzer operations should prefer consistency during partition?
- **Ideal Answer:** Exclusive job claims, quota reservation, permission changes, and completion publication should reject or delay uncertain writes rather than create duplicate ownership or unauthorized access.
- **Expected Follow-up:** Can analysis execution remain available?
- **Common Mistake:** Making every read unavailable because one invariant is strict.
- **How to Impress Interviewer:** Separate control-plane CP operations from rebuildable data-plane work.

## 26. AP operations
- **Question:** Which operations could prefer availability during partition?
- **Ideal Answer:** Serving cached public reports, collecting telemetry, and accepting deduplicable progress events may remain available with later reconciliation.
- **Expected Follow-up:** How are conflicts resolved?
- **Common Mistake:** Allowing AP writes for permissions or billing counters.
- **How to Impress Interviewer:** Specify deterministic merge rules and bounded stale behavior.

## 27. PACELC
- **Question:** What does PACELC add to CAP analysis?
- **Ideal Answer:** It asks both what happens under partition and whether normal operation trades latency for consistency. Synchronous cross-region commits may be consistent but increase steady-state latency.
- **Expected Follow-up:** What would you choose for job metadata?
- **Common Mistake:** Discussing only rare partitions.
- **How to Impress Interviewer:** Quantify regional latency and state which operations need global ordering.

## 28. Leader-based replication
- **Question:** What are the benefits and risks of leader-based replication?
- **Ideal Answer:** A leader simplifies write ordering and constraints; followers scale reads and recovery. Risks include failover delay, replica lag, stale reads, and lost acknowledged writes under weak durability settings.
- **Expected Follow-up:** How do you detect split brain?
- **Common Mistake:** Assuming replicas are instantly current.
- **How to Impress Interviewer:** Mention fencing terms and commit-position-aware reads.

## 29. Multi-leader replication
- **Question:** Would multi-leader replication suit analyzer metadata?
- **Ideal Answer:** Usually not for strict job ownership because conflict resolution is difficult. It may suit region-local, mergeable events when every record has deterministic ownership.
- **Expected Follow-up:** How would duplicate jobs reconcile?
- **Common Mistake:** Assuming last-write-wins preserves invariants.
- **How to Impress Interviewer:** Prefer home-region writes or globally unique idempotency keys over semantic conflict repair.

## 30. Quorum reads and writes
- **Question:** Explain quorum consistency with N, R, and W.
- **Ideal Answer:** With N replicas, overlapping quorums such as `R + W > N` can observe recent writes under assumptions about versions and failures; sloppy quorums and clocks complicate the guarantee.
- **Expected Follow-up:** Does quorum guarantee linearizability?
- **Common Mistake:** Repeating the inequality as a complete proof.
- **How to Impress Interviewer:** Discuss version reconciliation, hinted handoff, and concurrent writes.

## 31. Horizontal partitioning
- **Question:** How would you shard metadata?
- **Ideal Answer:** Start unsharded. If required, tenant or repository ID gives locality and predictable ownership, while globally queried job queues may need a separate partition strategy.
- **Expected Follow-up:** What creates hot shards?
- **Common Mistake:** Sharding before a measured capacity limit.
- **How to Impress Interviewer:** Include resharding, cross-tenant analytics, and large-tenant isolation in the design.

## 32. Vertical partitioning
- **Question:** Where could vertical partitioning help?
- **Ideal Answer:** Separate frequently accessed job metadata from large reports, verbose events, or configuration blobs so hot rows and indexes remain compact.
- **Expected Follow-up:** Does this require separate databases?
- **Common Mistake:** Splitting tables without an access-pattern reason.
- **How to Impress Interviewer:** Estimate row width, cache residency, and join frequency.

## 33. Partition key choice
- **Question:** What makes a good partition key?
- **Ideal Answer:** High cardinality, even load, access locality, stable ownership, and compatibility with dominant queries. It should avoid sequential hotspots and unbounded single-tenant concentration.
- **Expected Follow-up:** Is commit SHA a good key?
- **Common Mistake:** Optimizing only distribution while forcing scatter-gather reads.
- **How to Impress Interviewer:** Evaluate both bytes and requests per partition, not row counts alone.

## 34. Consistent hashing
- **Question:** Why use consistent hashing?
- **Ideal Answer:** It limits key movement when nodes join or leave and supports virtual nodes for balancing. It does not itself solve replication, hotspots, or transactional queries.
- **Expected Follow-up:** How are large tenants handled?
- **Common Mistake:** Saying no keys move during membership changes.
- **How to Impress Interviewer:** Mention weighted virtual nodes and explicit hot-key splitting.

## 35. Range partitioning
- **Question:** When is range partitioning useful?
- **Ideal Answer:** Time ranges suit job events and retention because recent scans and partition drops are efficient. Monotonic inserts can hotspot the newest partition.
- **Expected Follow-up:** How would you mitigate that hotspot?
- **Common Mistake:** Using time partitions for every table.
- **How to Impress Interviewer:** Combine time partitions with hash subpartitioning only when measurements justify complexity.

## 36. Primary indexes
- **Question:** What does a primary-key index provide?
- **Ideal Answer:** It gives efficient unique row lookup and often determines physical clustering, depending on the engine. A wide or random key can increase secondary-index and write costs.
- **Expected Follow-up:** UUIDv4 or time-ordered UUID?
- **Common Mistake:** Assuming primary keys are always physically ordered.
- **How to Impress Interviewer:** Explain engine-specific clustered versus heap storage.

## 37. Composite indexes
- **Question:** Design an index for listing a tenant's newest jobs by status.
- **Ideal Answer:** A likely index is `(tenant_id, status, created_at DESC)` with selected included columns, validated against exact filters and pagination.
- **Expected Follow-up:** Can it serve a query without status?
- **Common Mistake:** Ignoring leftmost-prefix behavior.
- **How to Impress Interviewer:** Compare alternate indexes using actual query plans and cardinalities.

## 38. Covering indexes
- **Question:** What is a covering index?
- **Ideal Answer:** It contains every column needed by a query, avoiding table lookups. Faster reads cost storage, cache pressure, and extra write maintenance.
- **Expected Follow-up:** Which columns belong in `INCLUDE`?
- **Common Mistake:** Adding every selected column to the key.
- **How to Impress Interviewer:** Keep predicates and ordering in keys, payload columns included where supported.

## 39. Partial indexes
- **Question:** How could a partial index help the job queue?
- **Ideal Answer:** Index only claimable rows such as queued jobs, making the hot index small. Its predicate must match queue semantics exactly.
- **Expected Follow-up:** What happens when status changes?
- **Common Mistake:** Expecting the index to help queries that do not imply its predicate.
- **How to Impress Interviewer:** Monitor churn and vacuum behavior for rapidly entering and leaving rows.

## 40. Expression indexes
- **Question:** When would an expression index be useful?
- **Ideal Answer:** It can index normalized repository identifiers such as lowercase provider and owner, provided queries use the same deterministic expression.
- **Expected Follow-up:** Why not normalize on write?
- **Common Mistake:** Indexing unstable or locale-dependent expressions.
- **How to Impress Interviewer:** Prefer canonical stored values when normalization is a domain invariant.

## 41. B-tree indexes
- **Question:** Why are B-trees the default index for metadata?
- **Ideal Answer:** They support equality, ordered ranges, sorting, and prefix scans with logarithmic navigation and good page locality.
- **Expected Follow-up:** When are they poor?
- **Common Mistake:** Claiming constant-time lookup.
- **How to Impress Interviewer:** Relate fan-out, page splits, clustering, and cache behavior to workload.

## 42. Hash indexes
- **Question:** When would a hash index be appropriate?
- **Ideal Answer:** For equality-only lookups where the engine's implementation and durability are mature. It cannot support range ordering or prefix scans.
- **Expected Follow-up:** Why might a B-tree still win?
- **Common Mistake:** Choosing hash because theoretical lookup is O(1).
- **How to Impress Interviewer:** Include collision, resizing, and buffer-cache considerations.

## 43. Full-text indexes
- **Question:** Should code and reports use database full-text search?
- **Ideal Answer:** It can serve lexical report search, but code-aware tokenization and large corpora may require a dedicated search engine. It does not replace semantic vector retrieval.
- **Expected Follow-up:** How would hybrid search work?
- **Common Mistake:** Treating keyword and semantic search as interchangeable.
- **How to Impress Interviewer:** Fuse ranked lexical and vector results, then evaluate on real questions.

## 44. Index selectivity
- **Question:** Why does index selectivity matter?
- **Ideal Answer:** An index on a low-cardinality status may touch much of the table, so a sequential scan can be cheaper. Composite or partial indexes add useful selectivity.
- **Expected Follow-up:** Why might the optimizer estimate poorly?
- **Common Mistake:** Assuming any indexed predicate uses the index.
- **How to Impress Interviewer:** Discuss statistics, skew, correlation, and extended statistics.

## 45. Too many indexes
- **Question:** What is the cost of over-indexing?
- **Ideal Answer:** Every write updates more structures, increasing latency, WAL, storage, vacuum work, and cache pressure. Redundant indexes also complicate planning.
- **Expected Follow-up:** How do you identify unused indexes?
- **Common Mistake:** Measuring only read improvements.
- **How to Impress Interviewer:** Use workload statistics, constraint dependencies, and safe staged removal.

## 46. Query plans
- **Question:** How do you investigate a slow metadata query?
- **Ideal Answer:** Capture the exact query and parameters, inspect `EXPLAIN ANALYZE`, compare estimates to actual rows, and check I/O, locks, sorts, spills, and index suitability.
- **Expected Follow-up:** Why can production parameters matter?
- **Common Mistake:** Adding an index before examining the plan.
- **How to Impress Interviewer:** Separate planning, execution, contention, and network latency.

## 47. N+1 queries
- **Question:** What is an N+1 query problem?
- **Ideal Answer:** One query loads jobs, then one query per job fetches its repository or artifacts, multiplying round trips. Use joins, batching, or prefetching.
- **Expected Follow-up:** When can a join be worse?
- **Common Mistake:** Fixing it by loading an unbounded object graph.
- **How to Impress Interviewer:** Measure query count, returned bytes, and duplication together.

## 48. Cursor pagination
- **Question:** Why prefer cursor pagination for job history?
- **Ideal Answer:** Seek pagination using a stable tuple such as `(created_at, id)` avoids large offset scans and reduces duplicates or omissions during concurrent inserts.
- **Expected Follow-up:** What belongs in the cursor?
- **Common Mistake:** Using a non-unique timestamp alone.
- **How to Impress Interviewer:** Sign opaque cursors and define snapshot versus live-list semantics.

## 49. Connection pooling
- **Question:** Why is database connection pooling necessary?
- **Ideal Answer:** Connections are expensive and databases support a bounded number. Pools amortize setup and provide backpressure, but must be sized across all service replicas.
- **Expected Follow-up:** How do you choose pool size?
- **Common Mistake:** Allocating the database maximum to every process.
- **How to Impress Interviewer:** Use Little's Law, transaction duration, and total deployment concurrency.

## 50. Pool exhaustion
- **Question:** How should pool exhaustion be handled?
- **Ideal Answer:** Bound acquisition time, fail or shed load clearly, and investigate long transactions, leaked sessions, or overload. Unlimited waiting hides saturation.
- **Expected Follow-up:** Which metrics matter?
- **Common Mistake:** Increasing pool size until the database collapses.
- **How to Impress Interviewer:** Track wait time, active/idle counts, transaction age, and database CPU/I/O.

## 51. Idempotency keys
- **Question:** How would you make analysis creation idempotent?
- **Ideal Answer:** Store a client-scoped idempotency key with request hash and result under a uniqueness constraint. A retry returns the original job or rejects a mismatched payload.
- **Expected Follow-up:** How long are keys retained?
- **Common Mistake:** Deduplicating solely by repository URL.
- **How to Impress Interviewer:** Atomically reserve the key and job in one transaction.

## 52. Exactly-once processing
- **Question:** Can the job system guarantee exactly-once execution?
- **Ideal Answer:** End-to-end exactly-once is generally impractical across crashes and external effects. Use at-least-once delivery with idempotent state transitions and deduplicated artifact publication.
- **Expected Follow-up:** Can embedding computation run twice?
- **Common Mistake:** Equating exactly-once queue delivery with exactly-once effects.
- **How to Impress Interviewer:** Define the observable effect that must occur once.

## 53. Transactional outbox
- **Question:** Why use a transactional outbox?
- **Ideal Answer:** Write the business state and an event row in one transaction; a relay publishes events and marks them delivered. This avoids committing state but losing its message.
- **Expected Follow-up:** Can the relay publish duplicates?
- **Common Mistake:** Publishing to a broker before committing the database.
- **How to Impress Interviewer:** Require idempotent consumers and monitor outbox age.

## 54. Change data capture
- **Question:** Where could change data capture help?
- **Ideal Answer:** CDC can stream committed job or artifact changes into search, analytics, and audit systems without application dual writes.
- **Expected Follow-up:** How is schema evolution handled?
- **Common Mistake:** Treating the database log as a permanent public API.
- **How to Impress Interviewer:** Version event contracts and preserve ordering per aggregate.

## 55. Soft deletion
- **Question:** Should analyses be soft-deleted?
- **Ideal Answer:** Use soft deletion only when recovery, audit, or asynchronous purge requires it. Authorization queries must exclude deleted rows, and policy must eventually remove underlying artifacts.
- **Expected Follow-up:** How do unique constraints behave?
- **Common Mistake:** Adding `deleted_at` without updating every query.
- **How to Impress Interviewer:** Separate user-visible deletion, legal hold, and physical erasure.

## 56. Retention
- **Question:** How would you enforce retention policies?
- **Ideal Answer:** Record retention class and deletion deadline, partition time-series data where useful, purge in bounded batches, and verify deletion across replicas, backups, caches, and artifacts.
- **Expected Follow-up:** Can backups erase one tenant immediately?
- **Common Mistake:** Deleting only the primary metadata row.
- **How to Impress Interviewer:** Document cryptographic erasure or backup-expiry semantics.

## 57. Multi-tenancy
- **Question:** Shared tables or one database per tenant?
- **Ideal Answer:** Shared tables with mandatory tenant keys are simpler and efficient for most tenants; isolated databases suit regulatory or very large tenants but increase operations.
- **Expected Follow-up:** How do you prevent cross-tenant reads?
- **Common Mistake:** Relying only on controller filters.
- **How to Impress Interviewer:** Combine scoped data access, row-level security where appropriate, and isolation tests.

## 58. Row-level security
- **Question:** What can row-level security provide?
- **Ideal Answer:** Database-enforced tenant predicates provide defense in depth when session identity is set correctly. Misconfigured privileged roles or pooled-session context can bypass it.
- **Expected Follow-up:** How do pools reset tenant context?
- **Common Mistake:** Treating RLS as a complete authorization system.
- **How to Impress Interviewer:** Test policies under every application role and failure path.

## 59. Encrypt data at rest
- **Question:** What does encryption at rest protect?
- **Ideal Answer:** It protects stolen disks, snapshots, and backups, depending on key separation. It does not stop an authorized or compromised application from reading plaintext.
- **Expected Follow-up:** Where are encryption keys stored?
- **Common Mistake:** Claiming disk encryption prevents SQL injection.
- **How to Impress Interviewer:** Describe envelope encryption, rotation, audit, and key-access boundaries.

## 60. Encrypt data in transit
- **Question:** How should database traffic be protected?
- **Ideal Answer:** Require TLS with certificate validation, private networking, short-lived credentials, and least-privilege roles. Encrypt replica and backup transport too.
- **Expected Follow-up:** Is TLS inside a VPC still needed?
- **Common Mistake:** Enabling TLS without verifying server identity.
- **How to Impress Interviewer:** Automate certificate rotation and reject insecure fallback.

## 61. Secrets in clone URLs
- **Question:** What database risk arises from repository clone URLs?
- **Ideal Answer:** URLs may embed tokens. Canonicalize and redact them before persistence or logs; store credentials in a secret manager and reference them indirectly.
- **Expected Follow-up:** How are credentials scoped?
- **Common Mistake:** Encrypting a token but also logging the raw URL.
- **How to Impress Interviewer:** Use provider installation tokens with short lifetime and repository scope.

## 62. Audit logging
- **Question:** What should an audit log capture?
- **Ideal Answer:** Actor, action, target, authorization context, timestamp, request ID, and outcome for sensitive reads and mutations, without source contents or secrets.
- **Expected Follow-up:** Should audit records be mutable?
- **Common Mistake:** Using ordinary application logs as a complete audit trail.
- **How to Impress Interviewer:** Make records append-only, access-controlled, exportable, and retention-aware.

## 63. SQL injection
- **Question:** How do you prevent SQL injection?
- **Ideal Answer:** Use parameterized statements or a safe query builder, allowlist identifiers that cannot be bound, restrict database privileges, and test dynamic search paths.
- **Expected Follow-up:** Are ORMs sufficient?
- **Common Mistake:** Escaping strings manually.
- **How to Impress Interviewer:** Note that sort columns and raw fragments need explicit allowlists.

## 64. Schema migrations
- **Question:** How should schema migrations be deployed?
- **Ideal Answer:** Version them, test on production-like volume, make application and schema changes backward compatible, and separate risky data backfills from locking DDL.
- **Expected Follow-up:** What is expand-contract?
- **Common Mistake:** Renaming or dropping a column in one deployment.
- **How to Impress Interviewer:** Define rollback limits and observe lock duration and replica lag.

## 65. Expand-contract migration
- **Question:** Explain an expand-contract column migration.
- **Ideal Answer:** Add the new nullable column, deploy code that can read both and write both, backfill safely, switch reads, enforce constraints, then remove the old column later.
- **Expected Follow-up:** How do you verify the backfill?
- **Common Mistake:** Dual-writing indefinitely without reconciliation.
- **How to Impress Interviewer:** Add metrics comparing old and new values before cutover.

## 66. Backfills
- **Question:** How would you backfill millions of job rows?
- **Ideal Answer:** Process bounded primary-key ranges, commit each batch, throttle on database health and replica lag, make progress resumable, and avoid rewriting already-correct rows.
- **Expected Follow-up:** How do concurrent writes remain correct?
- **Common Mistake:** Running one unbounded transaction.
- **How to Impress Interviewer:** Establish dual-write or deterministic recomputation before starting.

## 67. Zero-downtime indexes
- **Question:** How do you add a large index safely?
- **Ideal Answer:** Use the engine's online or concurrent index build, verify validity and plan adoption, monitor I/O and lag, then deploy dependent queries.
- **Expected Follow-up:** What can still block?
- **Common Mistake:** Assuming “concurrent” means zero resource impact.
- **How to Impress Interviewer:** Rehearse cancellation and cleanup of an invalid build.

## 68. Vector database need
- **Question:** Does the current system already use a vector database?
- **Ideal Answer:** No. It uses one in-memory FAISS index in a global pipeline. FAISS is a similarity-search library; current vectors lack durable, distributed database semantics.
- **Expected Follow-up:** When should that change?
- **Common Mistake:** Calling any vector index a vector database.
- **How to Impress Interviewer:** Evaluate persistence, metadata filtering, updates, tenancy, replication, and operations separately from ANN speed.

## 69. FAISS strengths
- **Question:** Why might FAISS remain a good choice?
- **Ideal Answer:** It offers efficient local similarity search, many index types, GPU options, and control with low service overhead. It fits a single-process prototype with rebuildable data.
- **Expected Follow-up:** What breaks at multiple workers?
- **Common Mistake:** Replacing it solely because it is in-process.
- **How to Impress Interviewer:** Keep it when scale and failure requirements do not justify distributed complexity.

## 70. FAISS limitations here
- **Question:** What are the current FAISS design limitations?
- **Ideal Answer:** One RAM index and global pipeline create process-local state, limited isolation, restart loss, update coordination problems, and a scaling bottleneck. Disk clones do not solve index durability.
- **Expected Follow-up:** Which limitation should be fixed first?
- **Common Mistake:** Focusing only on vector capacity.
- **How to Impress Interviewer:** Distinguish library capability from this application's ownership model.

## 71. Vector store selection
- **Question:** How would you select a vector store?
- **Ideal Answer:** Benchmark recall, latency, ingestion, filtering, deletion, durability, backup, tenant isolation, operational burden, and cost on representative code queries.
- **Expected Follow-up:** Managed or self-hosted?
- **Common Mistake:** Choosing from vendor benchmark charts.
- **How to Impress Interviewer:** Define acceptance thresholds and a reproducible evaluation corpus first.

## 72. Vector dimensionality
- **Question:** How does embedding dimensionality affect storage?
- **Ideal Answer:** Raw float32 storage is roughly dimensions times four bytes per vector, before index and metadata overhead. Higher dimensions increase memory, bandwidth, and often search cost.
- **Expected Follow-up:** Can dimensions be reduced?
- **Common Mistake:** Estimating only raw vector bytes.
- **How to Impress Interviewer:** Include graph edges, replicas, allocator overhead, and quantization in capacity models.

## 73. Distance metric
- **Question:** Cosine similarity, dot product, or Euclidean distance?
- **Ideal Answer:** Match the metric used during embedding training. Cosine equals dot product for normalized vectors; changing normalization can change ranking.
- **Expected Follow-up:** Where should normalization occur?
- **Common Mistake:** Picking a metric by intuition.
- **How to Impress Interviewer:** Validate metric and preprocessing together using retrieval relevance.

## 74. Exact versus approximate search
- **Question:** When should vector search be approximate?
- **Ideal Answer:** Exact search is simplest for small corpora or strict recall. ANN becomes useful when latency or cost at corpus size exceeds budget, accepting tunable recall loss.
- **Expected Follow-up:** How do you measure recall?
- **Common Mistake:** Assuming ANN is always faster overall.
- **How to Impress Interviewer:** Compare against exact top-k ground truth on production-like queries.

## 75. HNSW
- **Question:** What are HNSW trade-offs?
- **Ideal Answer:** HNSW provides high recall and low query latency but consumes substantial memory and has costly construction and deletion behavior. `efSearch` trades latency for recall.
- **Expected Follow-up:** What does `M` control?
- **Common Mistake:** Tuning only query-time parameters.
- **How to Impress Interviewer:** Discuss filtered search, tombstones, and rebuild strategy.

## 76. IVF
- **Question:** What are inverted-file vector index trade-offs?
- **Ideal Answer:** IVF clusters vectors and searches selected lists, reducing work. Training quality and `nprobe` affect recall; skewed or changing distributions may require retraining.
- **Expected Follow-up:** How many centroids should be used?
- **Common Mistake:** Training on an unrepresentative sample.
- **How to Impress Interviewer:** Monitor list imbalance and recall drift after corpus changes.

## 77. Product quantization
- **Question:** Why use product quantization?
- **Ideal Answer:** PQ compresses vectors into short codes, reducing memory and improving scan throughput at a recall cost. Training must represent the target distribution.
- **Expected Follow-up:** Can original vectors be retained?
- **Common Mistake:** Treating compression as lossless.
- **How to Impress Interviewer:** Use reranking with full-precision vectors when quality warrants it.

## 78. Hybrid retrieval
- **Question:** Why combine lexical and vector search for code?
- **Ideal Answer:** Lexical search excels at exact symbols and literals; vectors capture conceptual similarity. Fusion improves coverage when calibrated on code-oriented queries.
- **Expected Follow-up:** How are scores combined?
- **Common Mistake:** Averaging incomparable raw scores.
- **How to Impress Interviewer:** Use reciprocal-rank fusion or learned ranking and report per-query-class gains.

## 79. Metadata filtering
- **Question:** What metadata filters are essential for code vectors?
- **Ideal Answer:** Tenant, repository, commit SHA, path, language, artifact type, and deletion state. Filters must be applied safely during retrieval, not only after an oversized global search.
- **Expected Follow-up:** Why is post-filtering risky?
- **Common Mistake:** Forgetting tenant filtering in vector search.
- **How to Impress Interviewer:** Treat authorization filters as non-bypassable query constraints.

## 80. Chunk identity
- **Question:** How should embedded chunks be identified?
- **Ideal Answer:** Use a stable content-derived ID plus repository version, path, span, parser version, and embedding version. This supports deduplication and traceability.
- **Expected Follow-up:** What happens when lines shift?
- **Common Mistake:** Using only sequential vector positions.
- **How to Impress Interviewer:** Separate content identity from location identity and preserve provenance.

## 81. Embedding versioning
- **Question:** How do you handle a new embedding model?
- **Ideal Answer:** Store model and preprocessing version with every vector, build a parallel index, evaluate it, then atomically route queries. Never mix incompatible vector spaces.
- **Expected Follow-up:** Can migration be lazy?
- **Common Mistake:** Overwriting vectors in place while serving queries.
- **How to Impress Interviewer:** Support dual-read evaluation and rollback before deleting the old index.

## 82. Incremental indexing
- **Question:** How would you index a new commit incrementally?
- **Ideal Answer:** Diff files, reuse unchanged content-addressed chunks, embed changed chunks, write a new immutable version manifest, and publish only after all references are valid.
- **Expected Follow-up:** How are deleted files handled?
- **Common Mistake:** Mutating the currently served index without a consistency boundary.
- **How to Impress Interviewer:** Make version publication an atomic pointer change.

## 83. Vector deletion
- **Question:** How should deleted code be removed from vector search?
- **Ideal Answer:** Mark the version or chunks unavailable immediately through metadata, then compact or rebuild indexes asynchronously if physical deletion is expensive.
- **Expected Follow-up:** What about privacy deletion?
- **Common Mistake:** Assuming a tombstone physically erases vector data.
- **How to Impress Interviewer:** Define immediate query exclusion and audited physical purge separately.

## 84. Global versus per-tenant indexes
- **Question:** Should vectors live in one global index?
- **Ideal Answer:** A global index improves utilization but raises isolation, filtering, and noisy-neighbor risks. Per-tenant or per-repository indexes simplify boundaries but fragment resources.
- **Expected Follow-up:** What hybrid design is possible?
- **Common Mistake:** Keeping the current global index when adding untrusted tenants.
- **How to Impress Interviewer:** Segment large tenants and pool small ones behind mandatory namespace filters.

## 85. Vector index persistence
- **Question:** Could serialized FAISS files provide durability?
- **Ideal Answer:** They can checkpoint index state, but require versioned manifests, atomic writes, checksums, compatible metadata, replication, and recovery testing. A file alone is not transactional durability.
- **Expected Follow-up:** How are concurrent readers updated?
- **Common Mistake:** Writing directly over the active index file.
- **How to Impress Interviewer:** Write immutable snapshots and atomically swap a validated manifest.

## 86. Cache strategy
- **Question:** What database reads should be cached?
- **Ideal Answer:** Cache stable repository metadata, completed report summaries, or expensive query results with explicit keys and TTLs. Avoid caching fast-changing authorization without robust invalidation.
- **Expected Follow-up:** Cache-aside or write-through?
- **Common Mistake:** Adding a cache before measuring database pressure.
- **How to Impress Interviewer:** Include stampede control, negative caching, and tenant-safe keys.

## 87. Cache invalidation
- **Question:** How would you invalidate cached analysis results?
- **Ideal Answer:** Key by immutable repository version and analyzer configuration so most results never need mutation; invalidate mutable aliases when their resolved version changes.
- **Expected Follow-up:** What if invalidation events are lost?
- **Common Mistake:** Caching by branch name indefinitely.
- **How to Impress Interviewer:** Prefer immutable keys and bounded TTL as a correctness backstop.

## 88. Backup types
- **Question:** Compare full, incremental, and differential backups.
- **Ideal Answer:** Full captures everything; incremental captures changes since the last backup; differential captures changes since the last full. Restore complexity and storage differ.
- **Expected Follow-up:** Which minimizes recovery time?
- **Common Mistake:** Choosing only by backup duration.
- **How to Impress Interviewer:** Evaluate the complete restore chain against RTO and failure domains.

## 89. Logical versus physical backups
- **Question:** When use logical versus physical database backups?
- **Ideal Answer:** Logical backups aid selective restore and portability but can be slow and lose physical details. Physical backups enable faster full recovery but are engine/version specific.
- **Expected Follow-up:** Which supports point-in-time recovery?
- **Common Mistake:** Treating a replica as a backup.
- **How to Impress Interviewer:** Maintain both when selective recovery and rapid disaster recovery matter.

## 90. Point-in-time recovery
- **Question:** How does point-in-time recovery work?
- **Ideal Answer:** Restore a base backup, then replay retained transaction logs to a chosen moment before corruption or deletion. Log continuity and tested procedures are essential.
- **Expected Follow-up:** What determines the achievable RPO?
- **Common Mistake:** Keeping backups without archived logs.
- **How to Impress Interviewer:** Regularly recover to an isolated environment and verify application-level invariants.

## 91. RPO and RTO
- **Question:** Define RPO and RTO for analyzer data.
- **Ideal Answer:** RPO is acceptable data loss measured in time; RTO is acceptable restoration time. Durable job metadata may need tighter targets than rebuildable embeddings.
- **Expected Follow-up:** Who sets these targets?
- **Common Mistake:** Declaring zero RPO and RTO without cost analysis.
- **How to Impress Interviewer:** Set objectives per data class and test them with timed recovery exercises.

## 92. Backup encryption
- **Question:** How should backups be secured?
- **Ideal Answer:** Encrypt with separately managed keys, restrict and audit access, use immutable retention where appropriate, validate checksums, and prevent production credentials from granting backup access.
- **Expected Follow-up:** How are keys recovered during disaster?
- **Common Mistake:** Securing the database but leaving snapshots broadly readable.
- **How to Impress Interviewer:** Test key recovery and rotation without exposing plaintext.

## 93. Backup testing
- **Question:** Why is a successful backup job insufficient?
- **Ideal Answer:** It proves data was written, not that the chain, keys, schema, or application can restore correctly. Only regular restore tests validate recoverability.
- **Expected Follow-up:** What should a restore test assert?
- **Common Mistake:** Monitoring backup completion alone.
- **How to Impress Interviewer:** Automate checksum, row-count, constraint, and representative application-query validation.

## 94. Disaster recovery
- **Question:** Design disaster recovery for metadata and vector artifacts.
- **Ideal Answer:** Replicate encrypted database backups and immutable artifact snapshots across failure domains, document dependency order, restore metadata, validate manifests, then load or rebuild indexes.
- **Expected Follow-up:** What if embeddings are missing?
- **Common Mistake:** Restoring components without checking version compatibility.
- **How to Impress Interviewer:** Practice regional failover and record actual RPO/RTO.

## 95. Corruption handling
- **Question:** How would you detect silent data corruption?
- **Ideal Answer:** Use storage checksums, artifact content hashes, database consistency checks, immutable manifests, and periodic restore verification. Compare derived artifacts to source versions.
- **Expected Follow-up:** How do you choose a clean recovery point?
- **Common Mistake:** Assuming replication protects against logical corruption.
- **How to Impress Interviewer:** Preserve multiple recovery generations because replicas may copy corruption.

## 96. Database observability
- **Question:** Which database metrics matter most?
- **Ideal Answer:** Query latency and errors, throughput, lock waits, deadlocks, connection saturation, cache hit rate, I/O, storage growth, replica lag, transaction age, and backup freshness.
- **Expected Follow-up:** Which are user-facing symptoms?
- **Common Mistake:** Watching CPU alone.
- **How to Impress Interviewer:** Correlate query fingerprints and job stages with service-level objectives.

## 97. Slow-query governance
- **Question:** How should slow queries be managed over time?
- **Ideal Answer:** Collect normalized fingerprints, rank by total impact and tail latency, assign ownership, verify plans after schema or data changes, and regression-test critical queries.
- **Expected Follow-up:** How do you capture parameters safely?
- **Common Mistake:** Optimizing the single slowest sample.
- **How to Impress Interviewer:** Consider frequency times cost and redact sensitive literals.

## 98. Database overload
- **Question:** What should happen when the database is overloaded?
- **Ideal Answer:** Apply admission control, bounded queues, timeouts, load shedding, and degraded reads where safe. Protect core state transitions before optional analytics.
- **Expected Follow-up:** Should clients retry?
- **Common Mistake:** Allowing synchronized unlimited retries.
- **How to Impress Interviewer:** Publish retry hints and use exponential backoff with jitter and retry budgets.

## 99. Migration from current state
- **Question:** How would you migrate from the current no-database design?
- **Ideal Answer:** First persist job metadata alongside existing behavior, reconcile and observe it, then make it authoritative. Add artifact manifests and durable vector snapshots or a vector service in later stages.
- **Expected Follow-up:** How do you roll back?
- **Common Mistake:** Replacing the global pipeline and storage model in one release.
- **How to Impress Interviewer:** Use shadow writes, consistency checks, feature flags, and explicit ownership cutovers.

## 100. Production readiness decision
- **Question:** What evidence would justify introducing each database component?
- **Ideal Answer:** Show requirements and measurements: lost work after restarts, coordination races, query latency, corpus size, tenant count, recovery objectives, and operator capacity. Choose the least complex design meeting them.
- **Expected Follow-up:** What would you defer?
- **Common Mistake:** Designing for hypothetical planetary scale.
- **How to Impress Interviewer:** Present staged thresholds for PostgreSQL metadata, artifact storage, FAISS snapshots, and eventually distributed vector search.
