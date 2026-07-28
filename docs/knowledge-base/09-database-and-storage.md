# Chapter 9 — Database and Storage

## Why storage architecture matters

The analyzer turns repositories into several different kinds of state: cloned source files, metadata, text chunks, dense vectors, and generated answers. These objects have different consistency, durability, query, and lifecycle needs. Treating all of them as a single “vector database” hides the most important engineering decisions: what survives restart, what can be rebuilt, what must be transactionally correct, and what may be eventually consistent.

This chapter therefore starts with the system that actually exists. The production designs later in the chapter are recommendations, not descriptions of implemented behavior.

## Current implementation: there is no database

No relational, document, key-value, or managed vector database is configured in this repository. `requirements.txt` contains no database driver or ORM. The UI calls FAISS a “vector database,” but the code creates a process-local `faiss.IndexFlatL2`; FAISS here is an in-memory similarity index, not a durable system of record.

### What is stored where

| State | Current location | Lifetime | Evidence and consequence |
|---|---|---|---|
| Cloned repository | Filesystem under relative `data/<repo_name>` | Survives process restart until deleted externally | `clone_repository()` derives a path and returns an existing directory without fetching updates |
| Parsed files | Python list of dictionaries | One `/analyze` request | `load_code_files()` reads supported source files into RAM |
| Chunks | Global `pipeline["chunks"]` | Until process restart or next successful analysis | A new analysis overwrites the only active corpus |
| Embeddings | Temporary NumPy-like array, then FAISS-owned vectors | Until request finishes / index is replaced | The standalone embedding array is not retained in `pipeline` |
| Vector index | Global `pipeline["index"]` in RAM | Until process restart or next analysis | No `faiss.write_index`, object storage, or database persistence exists |
| Summary | Global `pipeline["summary"]` | Until process restart or next analysis | No per-repository key or durable record |
| Questions and answers | Not stored | Response lifetime | `/ask` returns an answer directly |
| API key | Environment loaded through `.env` | Process configuration | Not a database record |

### Important current behaviors

1. **One mutable active corpus.** `pipeline = {}` is module-global. All users share it, and analyzing repository B replaces repository A’s chunks and index.
2. **No isolation.** Concurrent `/analyze` and `/ask` calls can observe mismatched state because chunks and index are assigned separately.
3. **No durability for the index.** A backend restart requires embedding and indexing again, although the cloned directory may remain.
4. **Potentially stale clones.** If `data/<repo_name>` exists, it is reused without validating remote URL, branch, or commit and without pulling.
5. **Name collisions.** Repositories with the same trailing name map to the same directory. URL parsing is not a stable repository identity.
6. **No lifecycle controls.** There are no quotas, retention periods, garbage collection, migrations, backups, or deletion APIs.
7. **No multi-process correctness.** Each Uvicorn worker would have an independent global dictionary and index.
8. **Rebuildability is partial.** Vectors can be recomputed from a known immutable commit, but the current clone does not record that commit as indexed metadata.

## Storage requirements before technology selection

Why define requirements first? A database choice is only defensible against access patterns and failure semantics.

### Core entities and invariants

- A repository has a canonical provider identity, owner, name, remote URL, and tenant.
- An indexing run targets one immutable commit and one version of the parser, chunker, and embedding model.
- Every chunk belongs to exactly one source file and indexing run.
- Every embedding belongs to exactly one chunk and model version.
- An index version becomes queryable atomically only after all required artifacts are complete.
- A question must search a specific tenant and index version.
- Deleting a tenant or repository must eventually remove metadata, source snapshots, vectors, and cached answers.

### Access patterns

- Look up repository by tenant and provider identity.
- List indexing runs and find the latest `READY` version.
- Upsert files and chunks for a commit.
- Perform filtered nearest-neighbor search by tenant, repository, commit, language, and path.
- Retrieve chunk text and line metadata for returned vector IDs.
- Record job status, failures, model versions, latency, token usage, and audit events.
- Expire caches and old index versions without interrupting current queries.

## Proposed production data model

Why separate metadata, blobs, and vectors? Relational metadata needs constraints and transactions; repository snapshots can be large and immutable; vectors need nearest-neighbor access. A polyglot design lets each workload use suitable storage while keeping PostgreSQL as the authority.

### Relational schema

```sql
CREATE TABLE tenants (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE repositories (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  provider text NOT NULL,
  provider_repo_id text NOT NULL,
  canonical_url text NOT NULL,
  default_branch text,
  created_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  UNIQUE (tenant_id, provider, provider_repo_id)
);

CREATE TABLE indexing_runs (
  id uuid PRIMARY KEY,
  repository_id uuid NOT NULL REFERENCES repositories(id),
  commit_sha text NOT NULL,
  status text NOT NULL CHECK (status IN
    ('QUEUED','CLONING','PARSING','EMBEDDING','PUBLISHING','READY','FAILED')),
  parser_version text NOT NULL,
  chunker_version text NOT NULL,
  embedding_model text NOT NULL,
  embedding_dimensions integer NOT NULL,
  artifact_uri text,
  started_at timestamptz,
  completed_at timestamptz,
  error_code text,
  UNIQUE (repository_id, commit_sha, parser_version, chunker_version, embedding_model)
);

CREATE TABLE source_files (
  id uuid PRIMARY KEY,
  indexing_run_id uuid NOT NULL REFERENCES indexing_runs(id) ON DELETE CASCADE,
  path text NOT NULL,
  language text,
  content_hash text NOT NULL,
  byte_size bigint NOT NULL,
  object_uri text,
  UNIQUE (indexing_run_id, path)
);

CREATE TABLE chunks (
  id uuid PRIMARY KEY,
  source_file_id uuid NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
  ordinal integer NOT NULL,
  start_byte integer NOT NULL,
  end_byte integer NOT NULL,
  start_line integer,
  end_line integer,
  content text NOT NULL,
  content_hash text NOT NULL,
  token_count integer,
  symbol_name text,
  UNIQUE (source_file_id, ordinal),
  CHECK (start_byte >= 0 AND end_byte > start_byte)
);

CREATE TABLE query_events (
  id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  indexing_run_id uuid NOT NULL REFERENCES indexing_runs(id),
  question_hash text,
  retrieved_chunk_ids uuid[],
  retrieval_ms integer,
  generation_ms integer,
  input_tokens integer,
  output_tokens integer,
  created_at timestamptz NOT NULL DEFAULT now()
);
```

Do not store raw questions by default; they can contain secrets copied from private code. If product requirements require them, encrypt them, define retention, and offer deletion.

### Vector representation

With PostgreSQL and `pgvector`, an `embeddings` table can contain `chunk_id`, `model_version`, and `vector(n)`. With a dedicated vector service, PostgreSQL stores the authoritative vector record ID and publication state while the service stores the searchable copy. IDs must be deterministic or idempotently upserted so retries do not duplicate vectors.

For the current `all-MiniLM-L6-v2`, vectors have 384 dimensions. This is a model fact, but production code should obtain and validate dimensions rather than hard-code an assumption.

### Indexes

- B-tree on `repositories(tenant_id, provider, provider_repo_id)` for identity lookup.
- Partial B-tree on `indexing_runs(repository_id, completed_at DESC) WHERE status='READY'`.
- B-tree on `source_files(indexing_run_id, path)` for path filters.
- B-tree on `chunks(source_file_id, ordinal)` for ordered reconstruction.
- GIN/trigram or full-text index on path, symbol, and content only if lexical/hybrid search is required.
- HNSW or IVFFlat vector index when the corpus outgrows exact search. Index the distance operator matching training and query semantics.

An index accelerates reads by increasing write cost, storage, and maintenance. Create only indexes justified by measured query plans.

## Query and publication flow

### Indexing transaction

Why not expose vectors as they are inserted? Partial corpora produce silently incomplete answers.

1. Resolve and authorize the tenant and repository.
2. Create an `indexing_runs` row in `QUEUED`.
3. Clone an immutable commit into isolated scratch storage.
4. Parse, chunk, and embed outside a long database transaction.
5. Bulk-write metadata and vectors under the run ID using idempotent operations.
6. Verify expected file/chunk/vector counts and artifact checksums.
7. In a short transaction, change the run to `READY` and update the repository’s active run pointer.
8. Emit an outbox event for cache invalidation and old-version cleanup.

The active pointer swap is the atomic publication boundary. Readers use the old complete version or the new complete version, never a half-built version.

### Query flow

1. Authenticate the principal and authorize repository access.
2. Read the active `READY` run.
3. Embed the normalized question with the run’s exact model version.
4. Search vectors with mandatory tenant and run filters.
5. Join vector IDs to chunk metadata; discard missing, deleted, or unauthorized records.
6. Optionally run lexical retrieval and reranking.
7. Generate an answer and record privacy-safe telemetry.

Parameterize all SQL. Apply tenant filters in the data layer, preferably with PostgreSQL row-level security as defense in depth.

## Transactions and concurrency

### Required transaction boundaries

- Repository creation plus ownership mapping should commit together.
- Run publication plus active-version change should commit together.
- Deletion intent plus outbox event should commit together.
- Usage accounting should use atomic increments or append-only events.

Do not hold a SQL transaction open while cloning, embedding, or calling Groq. External calls are slow and cannot participate in a normal database atomic commit. Use a state machine, idempotency keys, retries, and a transactional outbox.

### Isolation

`READ COMMITTED` is usually sufficient for ordinary metadata operations. Use a row lock, advisory lock, or uniqueness constraint to prevent duplicate indexing of the same repository/version. Publication can use `SELECT ... FOR UPDATE` or optimistic versioning. `SERIALIZABLE` is appropriate only where a demonstrated invariant cannot be protected more cheaply; retry serialization failures.

## ACID, BASE, and CAP

### ACID

- **Atomicity:** a transaction’s metadata changes all commit or all roll back.
- **Consistency:** constraints preserve valid relationships and states.
- **Isolation:** concurrent operations behave according to the selected isolation level.
- **Durability:** committed data survives qualifying failures under the database’s durability configuration.

Use ACID for tenant authorization, repository identity, billing, active index version, and deletion state.

### BASE

- **Basically available**
- **Soft state**
- **Eventually consistent**

Vector replicas, answer caches, metrics pipelines, and cleanup can be eventually consistent. BASE does not mean “no correctness”; it requires explicit convergence rules, idempotency, and bounded staleness.

### CAP

CAP concerns behavior during a network partition in a distributed data system: consistency versus availability while partition tolerance is required. It is not a blanket claim that every database permanently chooses only two letters. For this application:

- Authorization and publication metadata should fail closed or favor consistency.
- Search replicas may favor availability and serve a slightly stale, previously complete index.
- The UI should expose indexing status rather than pretending a partial update is current.

## Replication and high availability

Why replicate? To reduce recovery time and distribute reads—not to replace backups.

- Run PostgreSQL with synchronous replication within a region when low data-loss objectives justify the latency; use asynchronous cross-region replicas for disaster recovery.
- Route normal writes to the primary. Read replicas are safe for history and analytics, but active-version reads can be stale unless the application tolerates it.
- Replicate object storage across availability zones and enable versioning.
- Build vector replicas from immutable index versions. Publish only after replicas pass checksum and count validation.
- Use health checks, automatic failover, connection pooling, and tested fencing to avoid split brain.

## Partitioning and sharding

Do not shard a small system preemptively. First use vertical scaling, correct indexes, batching, and table partitioning.

### Partitioning

Partition large append-heavy tables such as `query_events` by time for retention. Partition chunks/embeddings by tenant hash or repository only when pruning and maintenance benefits are measured.

### Sharding

A practical shard key is `tenant_id`, because authorization and most repository queries remain local. Large tenants may need dedicated shards. A directory service maps tenants to shards. Cross-tenant analytics then becomes asynchronous.

Vector shards can be partitioned by tenant or index version. Global top-k over shards requires querying each relevant shard and merging candidates; latency rises with fan-out. Replicate small corpora instead of sharding them.

## Backup and disaster recovery

Why back up rebuildable data? Re-embedding may be slow, expensive, or impossible if source access or model versions change.

- Define RPO (maximum acceptable data loss) and RTO (maximum acceptable recovery time) per data class.
- Use continuous PostgreSQL WAL archiving plus encrypted full backups and point-in-time recovery.
- Enable object-storage versioning, retention, lifecycle rules, and cross-region copies where required.
- Snapshot or export vector indexes together with a manifest containing commit, model, dimensions, metric, count, and checksum.
- Keep secrets in a secret manager; do not put `.env` files into backups indiscriminately.
- Test restores on a schedule. A backup that has not been restored is an assumption.
- Run reconciliation after restore: metadata row counts, object checksums, vector counts, tenant filters, and sample queries.

## Technology alternatives

### PostgreSQL

PostgreSQL is the strongest default because the control plane is relational and transactional. JSONB handles evolving metadata, full-text search supports lexical retrieval, and `pgvector` can support modest-to-large vector workloads with one authorization boundary. Tradeoffs include vector index tuning, vacuum/maintenance, and eventual need to separate vector scale from transactional scale.

### MongoDB

MongoDB fits document-shaped repository manifests and flexible parser outputs. Atlas Vector Search can combine metadata filters and vector search. Transactions exist, but data modeling should still favor bounded documents and deliberate indexes; embedding every chunk inside one repository document would hit document-size and update-contention limits. Choose it when document workflows and team expertise outweigh relational constraints.

### MySQL

MySQL is capable for metadata, identities, jobs, and transactional publication. Its ecosystem and managed offerings are mature. Vector capabilities vary by version/provider, so a dedicated vector engine may be paired with it. Compared with PostgreSQL, integrated vector and advanced text-search ergonomics may be less uniform; verify the exact deployment rather than relying on generic product claims.

### Dedicated vector engines

Pinecone, Weaviate, Milvus, Qdrant, or OpenSearch can offer distributed ANN, filtering, and operational tooling. They do not remove the need for authoritative metadata, access-control enforcement, deletion workflows, backups, and model-version management. Evaluate filter correctness, consistency, tenancy, exportability, cost, and p95 latency on the real corpus.

## Recommended evolution

1. Record canonical repository identity and commit SHA.
2. Replace the single global pipeline with per-run state and atomic publication.
3. Persist metadata in PostgreSQL and snapshots in object storage.
4. Start with exact or pgvector search while the corpus is small.
5. Add background jobs, idempotency, outbox events, retention, and restore tests.
6. Adopt ANN or a dedicated vector service only after benchmarks show exact search no longer meets latency or cost goals.

## Interview 1 — Describe the current persistence model

**Question:** What database does this application use, and what survives a restart?

**Ideal Answer:** It uses no database. Git clones survive on the local filesystem under `data/`; chunks, summary, and `IndexFlatL2` live in a module-global dictionary and disappear on restart. Questions and answers are not persisted. Existing clones may be stale because the loader returns them without fetching.

**Why asked:** Tests whether the candidate distinguishes a library index from a durable database and reads code rather than UI copy.

**Common mistakes:** Calling FAISS a persistent vector database; claiming embeddings are saved to disk; overlooking overwrite of the single active corpus.

**Follow-ups:** What happens with two Uvicorn workers? What race can occur during concurrent analyze and ask requests?

## Interview 2 — Design an atomic index publication

**Question:** How would you prevent users from querying a partially built index?

**Ideal Answer:** Build an immutable version under a run ID, validate all artifacts, then atomically change a metadata pointer from the old `READY` run to the new one in a short transaction. Readers pin a version. Failed builds never become active and can be retried idempotently.

**Why asked:** Evaluates transactional reasoning across long-running external work.

**Common mistakes:** Holding one SQL transaction open during cloning and embedding; replacing vectors in place; relying only on a status string without an atomic pointer.

**Follow-ups:** How do you roll back? How do you garbage-collect the old version safely?

## Interview 3 — Choose PostgreSQL, MongoDB, or MySQL

**Question:** Which database would you choose for production and why?

**Ideal Answer:** PostgreSQL is a good default because repository ownership, job states, versions, and deletion require relational constraints and transactions, while JSONB, text search, and pgvector reduce operational components. MongoDB is credible for document-centric workloads; MySQL is strong for metadata but may be paired with a vector engine. The final choice requires corpus and workload benchmarks.

**Why asked:** Looks for requirements-driven selection rather than brand preference.

**Common mistakes:** Claiming one database is universally fastest; ignoring authorization filters and operational expertise; evaluating vectors but not metadata correctness.

**Follow-ups:** At what scale would you separate vector search? Which benchmark would trigger that move?

## Interview 4 — Explain ACID, BASE, and CAP here

**Question:** Where would you require strong consistency, and where is eventual consistency acceptable?

**Ideal Answer:** Ownership, authorization, billing, deletion state, and active-version publication need strong consistency. Search replicas, caches, analytics, and cleanup may be eventually consistent if they serve only complete authorized versions and converge predictably. During partitions, authorization should fail closed while search may serve a stale complete index.

**Why asked:** Tests application of distributed-systems concepts rather than memorized definitions.

**Common mistakes:** Saying CAP means “pick any two” outside partitions; treating eventual consistency as arbitrary inconsistency; requiring global serializability for metrics.

**Follow-ups:** How would you communicate staleness? Which operations need idempotency?

## Interview 5 — Partition and shard the corpus

**Question:** When and how would you shard this system?

**Ideal Answer:** Only after measured limits remain after indexing, batching, and vertical scaling. Shard primarily by tenant so authorization and repository queries stay local, with dedicated shards for very large tenants. Vector fan-out must merge per-shard candidates, so avoid it when replication or per-tenant routing suffices.

**Why asked:** Reveals whether the candidate understands the operational cost of distribution.

**Common mistakes:** Sharding immediately; using repository name as a key; ignoring hot tenants, resharding, and cross-shard top-k.

**Follow-ups:** How does a tenant move shards? How do you prevent cross-tenant leakage?

## Interview 6 — Prove recoverability

**Question:** What backup and recovery plan would you implement?

**Ideal Answer:** Define RPO/RTO, use PostgreSQL PITR, version and replicate immutable artifacts, export vector manifests and checksums, protect encryption keys separately, and regularly restore into an isolated environment. Reconciliation must verify metadata, blobs, vectors, tenant scoping, and sample retrieval before traffic returns.

**Why asked:** Distinguishes having backups from having a tested recovery capability.

**Common mistakes:** Treating replicas as backups; backing up vectors without model/version metadata; never testing restore; omitting deletion and retention obligations.

**Follow-ups:** Which data can be rebuilt? What happens if the old embedding model is no longer available?
