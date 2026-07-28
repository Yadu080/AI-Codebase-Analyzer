# AI Codebase Analyzer: 100 Beginner Interview Questions

Project-specific questions based on the current implementation. Recommendations are explicitly labeled so they are not confused with existing behavior.

## Topics

- [Project Purpose and Flow (1–10)](#project-purpose-and-flow-110)
- [Repository Loading and Parsing (11–25)](#repository-loading-and-parsing-1125)
- [Chunking and Embeddings (26–40)](#chunking-and-embeddings-2640)
- [FAISS Retrieval (41–52)](#faiss-retrieval-4152)
- [Answer Generation (53–62)](#answer-generation-5362)
- [FastAPI Backend (63–76)](#fastapi-backend-6376)
- [Streamlit Frontend (77–88)](#streamlit-frontend-7788)
- [Summary, Architecture, and Operations (89–100)](#summary-architecture-and-operations-89100)

## Project Purpose and Flow (1–10)

### 1. What problem does this project solve?
- **Question:** What problem does the AI Codebase Analyzer solve?
- **Ideal Answer:** It clones a public GitHub repository, indexes supported source code semantically, and answers questions using retrieved code as LLM context.
- **Expected Follow-up:** Why use retrieval instead of sending the whole repository?
- **Common Mistake:** Calling it a code generator; its implemented purpose is repository exploration and explanation.
- **How to Impress Interviewer:** Describe it as a small retrieval-augmented generation, or RAG, developer tool.

### 2. What are the system's main layers?
- **Question:** What are the main layers in the current system?
- **Ideal Answer:** A Streamlit UI calls a FastAPI backend, which orchestrates repository loading, chunking, embedding, FAISS retrieval, and Groq answer generation.
- **Expected Follow-up:** Where does state live?
- **Common Mistake:** Saying Streamlit directly performs the complete RAG pipeline.
- **How to Impress Interviewer:** Note that Streamlit also performs dependency analysis locally, which partially crosses the layer boundary.

### 3. What happens during repository analysis?
- **Question:** Trace the current `/analyze` flow.
- **Ideal Answer:** It clones or reuses a repository, loads supported files, creates 500-character chunks, embeds them, builds an in-memory FAISS index, and stores chunks, index, and summary globally.
- **Expected Follow-up:** What can fail in that sequence?
- **Common Mistake:** Claiming the index is persisted to disk.
- **How to Impress Interviewer:** Mention that every stage is synchronous and blocks the request.

### 4. What happens when a user asks a question?
- **Question:** Trace the current `/ask` flow.
- **Ideal Answer:** The backend embeds the question, retrieves five nearest chunks from the global FAISS index, builds a prompt, calls Groq, and returns the generated answer.
- **Expected Follow-up:** What must happen first?
- **Common Mistake:** Forgetting that `/analyze` must populate the global pipeline.
- **How to Impress Interviewer:** Point out that the response currently contains only the answer, not source citations or distances.

### 5. Why is this called RAG?
- **Question:** Why does the project qualify as retrieval-augmented generation?
- **Ideal Answer:** It retrieves repository chunks using semantic vector search and augments the LLM prompt with those chunks before generation.
- **Expected Follow-up:** Does RAG guarantee truthfulness?
- **Common Mistake:** Saying retrieval eliminates hallucinations; it only grounds the model with selected context.
- **How to Impress Interviewer:** Separate retrieval quality from generation quality because either stage can fail.

### 6. Which technologies implement the pipeline?
- **Question:** Which major technologies does the project use?
- **Ideal Answer:** GitPython clones repositories, SentenceTransformers embeds text, FAISS searches vectors, Groq hosts the LLM, FastAPI exposes endpoints, and Streamlit renders the UI.
- **Expected Follow-up:** What do NetworkX and Matplotlib do?
- **Common Mistake:** Treating FAISS as a relational database.
- **How to Impress Interviewer:** Explain that `faiss.IndexFlatL2` is an exact in-memory vector index.

### 7. What data moves between stages?
- **Question:** What is the primary data shape passed through indexing?
- **Ideal Answer:** Loaded files are dictionaries with `file_path` and `content`; chunks are dictionaries with `file_path` and `chunk`; embeddings are a numeric matrix aligned by chunk position.
- **Expected Follow-up:** Why does positional alignment matter?
- **Common Mistake:** Assuming FAISS stores the chunk text.
- **How to Impress Interviewer:** State that FAISS returns integer positions used to look up metadata in the separate chunk list.

### 8. Where is repository state stored?
- **Question:** Where does the backend keep the analyzed repository state?
- **Ideal Answer:** `app/api.py` stores `chunks`, `index`, and `summary` in a module-level `pipeline` dictionary.
- **Expected Follow-up:** What happens after a server restart?
- **Common Mistake:** Saying state is stored in Streamlit session state.
- **How to Impress Interviewer:** Distinguish current process-local state from a production persistent, repository-scoped store.

### 9. What repositories work best?
- **Question:** Which repositories does the current implementation handle best?
- **Ideal Answer:** It loads Python, JavaScript, TypeScript, Java, C++, and C files, but architecture analysis only parses Python imports, so Python gets the richest support.
- **Expected Follow-up:** Are notebooks supported?
- **Common Mistake:** Repeating that only Python source can be indexed.
- **How to Impress Interviewer:** Contrast multi-language text retrieval with Python-only AST analysis.

### 10. What is the project's largest current limitation?
- **Question:** Name a central limitation of the current design.
- **Ideal Answer:** One global in-memory pipeline serves all users and repositories; a new analysis overwrites the previous index and restart loses it.
- **Expected Follow-up:** How would production differ?
- **Common Mistake:** Focusing only on UI styling.
- **How to Impress Interviewer:** Recommend repository IDs plus persistent indexes and metadata, while clearly labeling that as future work.

## Repository Loading and Parsing (11–25)

### 11. How is a repository name derived?
- **Question:** How does `clone_repository` derive the local directory name?
- **Ideal Answer:** It takes the final slash-separated URL segment and removes the substring `.git`, then joins it under `data`.
- **Expected Follow-up:** What edge cases exist?
- **Common Mistake:** Claiming GitPython determines the directory name.
- **How to Impress Interviewer:** Mention trailing slashes can produce an empty name and URL validation is absent.

### 12. What happens if the clone directory exists?
- **Question:** What does `clone_repository` do when `data/<repo>` already exists?
- **Ideal Answer:** It prints that the repository exists and returns the path without fetching or validating the checkout.
- **Expected Follow-up:** Could the content be stale?
- **Common Mistake:** Saying it automatically pulls the latest commit.
- **How to Impress Interviewer:** Recommend explicit cache semantics and commit-based refresh in production.

### 13. Which library performs cloning?
- **Question:** Which component actually clones the Git repository?
- **Ideal Answer:** `git.Repo.clone_from` from GitPython clones the supplied URL into the derived path.
- **Expected Follow-up:** Is only GitHub technically accepted?
- **Common Mistake:** Saying the code invokes the `git` shell command.
- **How to Impress Interviewer:** Note that the UI says GitHub, while GitPython may accept other reachable Git URLs.

### 14. Which source extensions are loaded?
- **Question:** Which file extensions does `load_code_files` currently accept?
- **Ideal Answer:** `.py`, `.js`, `.ts`, `.java`, `.cpp`, and `.c`.
- **Expected Follow-up:** Is matching case-sensitive?
- **Common Mistake:** Including Markdown because README documentation mentions repository analysis broadly.
- **How to Impress Interviewer:** Observe that uppercase extensions and JSX/TSX are not included.

### 15. How are repository files discovered?
- **Question:** How does the parser discover files?
- **Ideal Answer:** It recursively walks the repository with `os.walk` and checks each filename against `SUPPORTED_EXTENSIONS`.
- **Expected Follow-up:** Are generated or vendor directories excluded?
- **Common Mistake:** Saying it obeys `.gitignore`.
- **How to Impress Interviewer:** Note that no directory pruning exists, so vendored code may be indexed.

### 16. What does the parser return?
- **Question:** What does `load_code_files` return?
- **Ideal Answer:** A list of dictionaries, each containing the full local `file_path` and complete text `content`.
- **Expected Follow-up:** Are line numbers retained?
- **Common Mistake:** Saying it returns AST nodes.
- **How to Impress Interviewer:** Mention that lack of line metadata weakens precise citations later.

### 17. How are files decoded?
- **Question:** What text encoding is used when loading code?
- **Ideal Answer:** Files are opened as UTF-8.
- **Expected Follow-up:** What happens to a non-UTF-8 file?
- **Common Mistake:** Saying Python auto-detects encoding here.
- **How to Impress Interviewer:** Explain that the broad exception silently skips decoding failures.

### 18. How are parser errors handled?
- **Question:** How does `load_code_files` handle read failures?
- **Ideal Answer:** A bare `except` catches every exception and continues, so the failed file is silently omitted.
- **Expected Follow-up:** Why is that risky?
- **Common Mistake:** Claiming errors are returned to the API.
- **How to Impress Interviewer:** Recommend catching expected exceptions and recording skipped paths and reasons in production.

### 19. Does loading parse syntax?
- **Question:** Does `load_code_files` parse source syntax?
- **Ideal Answer:** No. It reads supported files as plain text; Python AST parsing occurs separately in `architecture.py`.
- **Expected Follow-up:** Why does that matter for chunking?
- **Common Mistake:** Confusing the file loader with the dependency analyzer.
- **How to Impress Interviewer:** State that semantic boundaries such as functions and classes are not preserved.

### 20. Are binary files loaded?
- **Question:** Can binary files enter the code index?
- **Ideal Answer:** Only matching extensions are attempted as UTF-8 text; binary-like content with those extensions may fail or decode unexpectedly.
- **Expected Follow-up:** Is there a size check?
- **Common Mistake:** Saying extension filtering proves content is safe text.
- **How to Impress Interviewer:** Suggest MIME/content checks and file-size limits for production ingestion.

### 21. Does the loader count all files?
- **Question:** Is the summary's `total_files` the number of indexed source files?
- **Ideal Answer:** No. `generate_repo_summary` counts every walked file, while only supported source extensions become chunks.
- **Expected Follow-up:** How could the UI label be clearer?
- **Common Mistake:** Equating total files with loaded files.
- **How to Impress Interviewer:** Recommend reporting both discovered and indexed file counts.

### 22. Are hidden directories skipped?
- **Question:** Does repository ingestion skip `.git`?
- **Ideal Answer:** No explicit pruning exists; `os.walk` can traverse `.git`, although most internal files will not match supported source extensions.
- **Expected Follow-up:** What about a supported-looking file in hidden folders?
- **Common Mistake:** Assuming `.gitignore` controls `os.walk`.
- **How to Impress Interviewer:** Recommend pruning `.git`, virtual environments, dependencies, builds, and configurable ignore patterns.

### 23. Is the clone URL validated?
- **Question:** How does the backend validate `repo_url`?
- **Ideal Answer:** Pydantic validates that it is a string, but the application does not validate scheme, host, or repository safety.
- **Expected Follow-up:** Why is that important?
- **Common Mistake:** Saying `RepoRequest` guarantees a valid GitHub URL.
- **How to Impress Interviewer:** Flag SSRF and local/file URL risks as production concerns.

### 24. How are duplicate repository names handled?
- **Question:** What happens when different URLs end in the same repository name?
- **Ideal Answer:** They map to the same `data/<name>` path, and an existing directory is reused regardless of origin.
- **Expected Follow-up:** How should identity be represented?
- **Common Mistake:** Assuming the full URL is part of the path.
- **How to Impress Interviewer:** Recommend a normalized URL or immutable commit hash as part of a cache key.

### 25. Is clone cleanup implemented?
- **Question:** Does the current project remove cloned repositories?
- **Ideal Answer:** No cleanup or retention policy is implemented; clones remain under `data`.
- **Expected Follow-up:** What production control is needed?
- **Common Mistake:** Saying process restart clears cloned data.
- **How to Impress Interviewer:** Suggest quotas, TTL cleanup, ownership tracking, and safe deletion boundaries.

## Chunking and Embeddings (26–40)

### 26. How is code chunked?
- **Question:** How does `chunk_code` split source files?
- **Ideal Answer:** It slices each file's raw string every 500 characters by default.
- **Expected Follow-up:** Does it overlap chunks?
- **Common Mistake:** Saying chunks contain 500 tokens.
- **How to Impress Interviewer:** Emphasize characters, not tokens, and no syntax awareness.

### 27. What metadata does a chunk retain?
- **Question:** Which metadata is attached to each chunk?
- **Ideal Answer:** Only `file_path` and the chunk text are retained.
- **Expected Follow-up:** Are offsets or line ranges available?
- **Common Mistake:** Claiming function names are stored.
- **How to Impress Interviewer:** Recommend start/end offsets, line ranges, language, and symbol names for production citations.

### 28. Can chunking split a token or function?
- **Question:** Can the current chunker split identifiers or functions?
- **Ideal Answer:** Yes. Fixed character slicing can cut anywhere, including inside an identifier, string, comment, or function.
- **Expected Follow-up:** What would improve it?
- **Common Mistake:** Assuming source formatting creates natural boundaries automatically.
- **How to Impress Interviewer:** Suggest AST-aware or token-aware chunks with controlled overlap.

### 29. What happens with an empty file?
- **Question:** How many chunks does an empty file produce?
- **Ideal Answer:** Zero, because `range(0, 0, chunk_size)` has no iterations.
- **Expected Follow-up:** Is the file represented elsewhere?
- **Common Mistake:** Saying it creates one empty chunk.
- **How to Impress Interviewer:** Note that the summary may count the file even though the index does not represent it.

### 30. What happens with a 501-character file?
- **Question:** How many default chunks does a 501-character file produce?
- **Ideal Answer:** Two: one 500-character chunk and one 1-character chunk.
- **Expected Follow-up:** Why might tiny tail chunks hurt?
- **Common Mistake:** Rounding down to one chunk.
- **How to Impress Interviewer:** Suggest minimum-tail merging in a production chunker.

### 31. Is there chunk overlap?
- **Question:** Does the current chunking strategy use overlap?
- **Ideal Answer:** No. Each slice starts exactly 500 characters after the previous one.
- **Expected Follow-up:** Why might overlap help?
- **Common Mistake:** Assuming semantic models compensate fully for severed context.
- **How to Impress Interviewer:** Explain that overlap can preserve context across boundaries but increases index size.

### 32. Which embedding model is used?
- **Question:** Which SentenceTransformer model generates embeddings?
- **Ideal Answer:** `all-MiniLM-L6-v2`, loaded at module import time.
- **Expected Follow-up:** What operational effect does import-time loading have?
- **Common Mistake:** Naming the Groq LLM as the embedding model.
- **How to Impress Interviewer:** Mention startup download/memory costs and one model instance per worker process.

### 33. How are chunk embeddings created?
- **Question:** How does `embed_chunks` create vectors?
- **Ideal Answer:** It extracts every chunk's text and calls `model.encode(texts)` once for the list.
- **Expected Follow-up:** Is batching configurable here?
- **Common Mistake:** Saying it loops over FAISS.
- **How to Impress Interviewer:** Note that SentenceTransformers handles internal batching, but the app exposes no batch or progress controls.

### 34. How is a query embedded?
- **Question:** What shape does `embed_query` return?
- **Ideal Answer:** It calls `model.encode([query])`, producing a two-dimensional matrix with one row.
- **Expected Follow-up:** Why does FAISS accept that shape?
- **Common Mistake:** Saying it returns a scalar score.
- **How to Impress Interviewer:** Connect the one-row shape to `index.search` and `indices[0]`.

### 35. Are embeddings normalized?
- **Question:** Does the current embedder normalize vectors?
- **Ideal Answer:** No explicit normalization option is passed to `model.encode`.
- **Expected Follow-up:** Which distance metric is used?
- **Common Mistake:** Assuming all SentenceTransformer outputs are automatically unit length.
- **How to Impress Interviewer:** Explain that L2 ranking and cosine ranking align only when vectors are normalized.

### 36. Are file paths embedded?
- **Question:** Does retrieval consider the file path semantically?
- **Ideal Answer:** No. Only each chunk's code text is embedded; `file_path` remains metadata used later in the prompt.
- **Expected Follow-up:** What query types could suffer?
- **Common Mistake:** Believing the entire chunk dictionary is encoded.
- **How to Impress Interviewer:** Suggest enriching embedding text with path and symbol metadata.

### 37. What happens when no chunks exist?
- **Question:** What happens if analysis produces no chunks?
- **Ideal Answer:** `embed_chunks` returns an empty result, then `build_index` accesses `embeddings[0]` and fails.
- **Expected Follow-up:** Where should validation occur?
- **Common Mistake:** Saying FAISS creates an empty index automatically.
- **How to Impress Interviewer:** Recommend an explicit “no supported source files” API error before embedding.

### 38. Are embeddings cached?
- **Question:** Does the project cache generated embeddings?
- **Ideal Answer:** No persistent cache is implemented; reused clone directories are still re-read, re-chunked, and re-embedded on `/analyze`.
- **Expected Follow-up:** What cache key would be safe?
- **Common Mistake:** Confusing repository clone reuse with embedding reuse.
- **How to Impress Interviewer:** Suggest model version, commit hash, and chunking configuration in the cache key.

### 39. Why align chunks and embeddings?
- **Question:** Why must embedding row order match chunk order?
- **Ideal Answer:** FAISS returns row indices, and `retrieve` uses each index directly against the original `chunks` list.
- **Expected Follow-up:** What breaks if lists are reordered?
- **Common Mistake:** Assuming FAISS stores metadata internally.
- **How to Impress Interviewer:** Describe this as an implicit positional contract that production code should encapsulate.

### 40. Is model selection configurable?
- **Question:** Can a user choose the embedding model?
- **Ideal Answer:** No. `all-MiniLM-L6-v2` is hard-coded in `app/embedder.py`.
- **Expected Follow-up:** How should configuration be added?
- **Common Mistake:** Saying `.env` controls all models.
- **How to Impress Interviewer:** Recommend configuration plus index-version compatibility checks before swapping models.

## FAISS Retrieval (41–52)

### 41. Which FAISS index is used?
- **Question:** Which FAISS index type does `build_index` create?
- **Ideal Answer:** `faiss.IndexFlatL2`, an exact exhaustive nearest-neighbor index using squared L2 distance.
- **Expected Follow-up:** Is it approximate?
- **Common Mistake:** Calling it an approximate HNSW index.
- **How to Impress Interviewer:** Note that exact search is simple but scales linearly with vector count.

### 42. How is vector dimension determined?
- **Question:** How does the code determine FAISS vector dimension?
- **Ideal Answer:** It uses `len(embeddings[0])`, the width of the first embedding row.
- **Expected Follow-up:** What precondition does that create?
- **Common Mistake:** Saying the dimension is hard-coded to 384.
- **How to Impress Interviewer:** Mention that empty embeddings cause an immediate indexing error.

### 43. Why convert embeddings to NumPy?
- **Question:** Why does `build_index` call `np.array(embeddings)`?
- **Ideal Answer:** FAISS expects a contiguous numeric matrix-like input; conversion supplies a NumPy array for `index.add`.
- **Expected Follow-up:** What dtype is preferred?
- **Common Mistake:** Saying NumPy computes the embeddings.
- **How to Impress Interviewer:** Note that production code should enforce contiguous `float32` explicitly.

### 44. What does `index.add` do?
- **Question:** What does `index.add` store?
- **Ideal Answer:** It adds embedding vectors in row order; it does not store file paths or code text.
- **Expected Follow-up:** Where is metadata stored?
- **Common Mistake:** Claiming FAISS receives chunk dictionaries.
- **How to Impress Interviewer:** Tie each vector's implicit ID to its list position.

### 45. What does retrieval return?
- **Question:** What does `retrieve` return to the QA engine?
- **Ideal Answer:** A list of chunk dictionaries selected by FAISS indices, in nearest-neighbor result order.
- **Expected Follow-up:** Are distances included?
- **Common Mistake:** Saying it returns generated answers.
- **How to Impress Interviewer:** Point out that computed distances are discarded.

### 46. What is the default retrieval depth?
- **Question:** How many chunks are retrieved by default?
- **Ideal Answer:** Five, because `top_k` defaults to 5.
- **Expected Follow-up:** Can the API caller change it?
- **Common Mistake:** Saying the user controls it in Streamlit.
- **How to Impress Interviewer:** Note that the endpoint does not expose `top_k`.

### 47. How are nearest neighbors searched?
- **Question:** Which call performs vector search?
- **Ideal Answer:** `index.search(query_embedding, top_k)` returns distance and index matrices.
- **Expected Follow-up:** Why access `indices[0]`?
- **Common Mistake:** Claiming Python manually compares every chunk.
- **How to Impress Interviewer:** Explain that row zero corresponds to the single encoded query.

### 48. What is a lower FAISS score here?
- **Question:** Under `IndexFlatL2`, what does a lower distance mean?
- **Ideal Answer:** It means the query vector is closer to the chunk vector under squared Euclidean distance.
- **Expected Follow-up:** Is that a probability?
- **Common Mistake:** Treating a larger distance as greater relevance.
- **How to Impress Interviewer:** Clarify that raw distance is not a calibrated confidence score.

### 49. Can retrieval return invalid indices?
- **Question:** What risk exists when `top_k` exceeds the number of indexed vectors?
- **Ideal Answer:** FAISS may fill missing neighbors with index `-1`; Python then selects `chunks[-1]`, incorrectly duplicating the last chunk.
- **Expected Follow-up:** How should it be fixed?
- **Common Mistake:** Assuming FAISS always shortens the result list.
- **How to Impress Interviewer:** Recommend clamping `k` and filtering negative indices.

### 50. Does retrieval filter by repository?
- **Question:** Does `retrieve` filter results by repository?
- **Ideal Answer:** No. It searches whichever single index currently occupies the global pipeline.
- **Expected Follow-up:** What happens after another user analyzes a repo?
- **Common Mistake:** Assuming chunks include a repository ID filter.
- **How to Impress Interviewer:** Describe cross-user state overwrite as correctness and isolation risk.

### 51. Are duplicate chunks removed?
- **Question:** Does the retrieval stage deduplicate results?
- **Ideal Answer:** No explicit deduplication exists; each FAISS row maps directly to a chunk result.
- **Expected Follow-up:** Could adjacent chunks dominate?
- **Common Mistake:** Saying FAISS guarantees diverse contexts.
- **How to Impress Interviewer:** Suggest maximal marginal relevance or per-file diversity as a production enhancement.

### 52. Is the index saved?
- **Question:** Is the FAISS index persisted?
- **Ideal Answer:** No. It remains in the process-level `pipeline` dictionary and disappears on restart.
- **Expected Follow-up:** What would persistence require?
- **Common Mistake:** Assuming FAISS always writes an index file.
- **How to Impress Interviewer:** Mention saving both vectors and exactly aligned metadata/version information.

## Answer Generation (53–62)

### 53. Which LLM is called?
- **Question:** Which model does `generate_answer` request?
- **Ideal Answer:** Groq's `llama-3.3-70b-versatile`.
- **Expected Follow-up:** Where is that configured?
- **Common Mistake:** Confusing it with `all-MiniLM-L6-v2`.
- **How to Impress Interviewer:** Separate the local embedding model from the hosted generation model.

### 54. How is the Groq client configured?
- **Question:** How does the application obtain its Groq API key?
- **Ideal Answer:** `load_dotenv()` loads environment variables, then `Groq` receives `os.getenv("GROQ_API_KEY")` at module import.
- **Expected Follow-up:** What happens if the key is missing?
- **Common Mistake:** Saying the key comes from a request.
- **How to Impress Interviewer:** Recommend startup validation and secret management for production.

### 55. What context enters the prompt?
- **Question:** How are retrieved chunks formatted for the LLM?
- **Ideal Answer:** Each is rendered as `File: <path>` followed by chunk text, with chunks separated by blank lines.
- **Expected Follow-up:** Are line ranges included?
- **Common Mistake:** Saying the full repository is sent.
- **How to Impress Interviewer:** Note that paths help attribution, but missing line numbers limit verifiable citations.

### 56. What instruction is given to the model?
- **Question:** What does the prompt ask the LLM to do?
- **Ideal Answer:** It asks a senior software engineer to answer the question and clearly identify the file or module handling the functionality.
- **Expected Follow-up:** Does it require abstention?
- **Common Mistake:** Claiming the prompt forbids unsupported claims.
- **How to Impress Interviewer:** Identify missing “use only context” and “say insufficient evidence” guardrails.

### 57. Why use a low temperature?
- **Question:** What is the configured generation temperature?
- **Ideal Answer:** `0.2`, favoring more stable and focused responses than a high-creativity setting.
- **Expected Follow-up:** Does low temperature ensure correctness?
- **Common Mistake:** Treating temperature as a factuality guarantee.
- **How to Impress Interviewer:** State that grounding and evaluation matter more than temperature alone.

### 58. Is there a system message?
- **Question:** Does the Groq request include a system-role message?
- **Ideal Answer:** No. It sends one user-role message containing both instructions and retrieved context.
- **Expected Follow-up:** Why might roles matter?
- **Common Mistake:** Calling the opening prompt sentence a system message.
- **How to Impress Interviewer:** Recommend a fixed system instruction and carefully delimited untrusted repository content.

### 59. Is repository content trusted?
- **Question:** Could repository text influence model instructions?
- **Ideal Answer:** Yes. Raw code is interpolated into the same prompt, so malicious comments could attempt prompt injection.
- **Expected Follow-up:** Can delimiters eliminate the risk?
- **Common Mistake:** Assuming source code cannot contain instructions.
- **How to Impress Interviewer:** Recommend explicit trust boundaries, delimiters, instruction hierarchy, and output verification.

### 60. Are model errors handled?
- **Question:** How does `generate_answer` handle Groq failures?
- **Ideal Answer:** It does not catch exceptions or implement retries, so failures propagate to the FastAPI request.
- **Expected Follow-up:** What production behavior is preferable?
- **Common Mistake:** Saying FastAPI returns a custom model error.
- **How to Impress Interviewer:** Suggest bounded retries for transient errors, timeouts, and sanitized failure responses.

### 61. Does the answer include citations?
- **Question:** Does `/ask` return structured source citations?
- **Ideal Answer:** No. It returns only `{"answer": answer}`; any file mention depends on free-form model output.
- **Expected Follow-up:** How could citations be made reliable?
- **Common Mistake:** Treating prompt file labels as API citations.
- **How to Impress Interviewer:** Return retrieved paths, line ranges, distances, and stable chunk IDs separately.

### 62. Is prompt size controlled?
- **Question:** Does the QA engine enforce a token budget?
- **Ideal Answer:** No explicit token counting or truncation exists; it concatenates the five selected character chunks.
- **Expected Follow-up:** Is it likely huge today?
- **Common Mistake:** Saying fixed `top_k` alone is a token budget.
- **How to Impress Interviewer:** Note current chunks are small, but production should budget instructions, context, question, and output explicitly.

## FastAPI Backend (63–76)

### 63. What creates the API application?
- **Question:** Where is the FastAPI application instantiated?
- **Ideal Answer:** `app = FastAPI()` in `app/api.py`.
- **Expected Follow-up:** Are title or version metadata configured?
- **Common Mistake:** Saying Uvicorn creates the route definitions.
- **How to Impress Interviewer:** Distinguish the ASGI app from the Uvicorn server process.

### 64. Which request models exist?
- **Question:** Which Pydantic request models are defined?
- **Ideal Answer:** `RepoRequest` contains `repo_url: str`, and `QuestionRequest` contains `question: str`.
- **Expected Follow-up:** Are there length constraints?
- **Common Mistake:** Saying response models are also declared.
- **How to Impress Interviewer:** Note that production should add URL, emptiness, and length validation.

### 65. Which endpoints are exposed?
- **Question:** Which application endpoints exist?
- **Ideal Answer:** Three POST endpoints: `/analyze`, `/ask`, and `/architecture`.
- **Expected Follow-up:** Why is `/architecture` POST?
- **Common Mistake:** Inventing health or status endpoints.
- **How to Impress Interviewer:** Note all three execute work rather than serving static resources.

### 66. What does `/analyze` return?
- **Question:** What fields are returned after successful analysis?
- **Ideal Answer:** A success message, the number of generated chunks, and a repository summary.
- **Expected Follow-up:** Does it return a repository identifier?
- **Common Mistake:** Saying it returns embeddings.
- **How to Impress Interviewer:** Highlight that no analysis ID exists for later query routing.

### 67. What does `/architecture` do?
- **Question:** What does the architecture endpoint return?
- **Ideal Answer:** It clones or reuses the requested repository, parses Python imports, and returns a dictionary mapping Python filenames to imported module names.
- **Expected Follow-up:** Does it return the plotted graph?
- **Common Mistake:** Saying it uses the FAISS pipeline.
- **How to Impress Interviewer:** Distinguish graph data from the separate visualization helper.

### 68. Is `/architecture` tied to `/analyze`?
- **Question:** Must `/analyze` run before `/architecture`?
- **Ideal Answer:** No. `/architecture` independently accepts a repository URL and calls `clone_repository`.
- **Expected Follow-up:** Does it share the global index?
- **Common Mistake:** Assuming all endpoints require pipeline state.
- **How to Impress Interviewer:** Note that the frontend bypasses this endpoint and performs architecture analysis locally.

### 69. What happens if `/ask` is called first?
- **Question:** What happens when `/ask` runs before successful analysis?
- **Ideal Answer:** Accessing `pipeline["index"]` or `pipeline["chunks"]` raises `KeyError`, likely producing a server error.
- **Expected Follow-up:** What status should production return?
- **Common Mistake:** Saying it returns an empty answer.
- **How to Impress Interviewer:** Recommend a repository/analysis ID and a clear 409 or 404-style readiness error.

### 70. Are route functions asynchronous?
- **Question:** Are the endpoint handlers declared with `async def`?
- **Ideal Answer:** No. They are synchronous `def` handlers.
- **Expected Follow-up:** Are their dependencies blocking?
- **Common Mistake:** Assuming FastAPI makes all code asynchronous automatically.
- **How to Impress Interviewer:** Mention cloning, embedding, and LLM calls are long blocking operations suited to jobs or controlled worker execution.

### 71. Is authentication implemented?
- **Question:** Does the backend authenticate callers?
- **Ideal Answer:** No authentication or authorization is present.
- **Expected Follow-up:** Why does that matter?
- **Common Mistake:** Treating the Groq API key as user authentication.
- **How to Impress Interviewer:** Point out that public access could trigger expensive clones, embeddings, and LLM calls.

### 72. Is CORS configured?
- **Question:** Does `app/api.py` configure CORS middleware?
- **Ideal Answer:** No CORS middleware is configured.
- **Expected Follow-up:** Why does the current UI still work?
- **Common Mistake:** Assuming server-side `requests` is subject to browser CORS.
- **How to Impress Interviewer:** Explain that Streamlit's Python process calls FastAPI server-to-server.

### 73. Are response models declared?
- **Question:** Does FastAPI validate endpoint responses with Pydantic models?
- **Ideal Answer:** No `response_model` is declared for the routes.
- **Expected Follow-up:** What value would response models add?
- **Common Mistake:** Assuming request models automatically validate responses.
- **How to Impress Interviewer:** Mention schema stability, documentation, and accidental-data prevention.

### 74. Is pipeline mutation thread-safe?
- **Question:** Is the global `pipeline` updated atomically?
- **Ideal Answer:** No. Keys are assigned separately, so concurrent requests can observe mixed or overwritten state.
- **Expected Follow-up:** What is the current visible risk?
- **Common Mistake:** Saying Python dictionaries make the whole workflow thread-safe.
- **How to Impress Interviewer:** Explain that individual assignments do not make multi-step state transitions atomic.

### 75. Does the API log structured events?
- **Question:** What logging does the backend implement?
- **Ideal Answer:** Repository cloning uses basic `print` statements; structured request, timing, and error logging is absent.
- **Expected Follow-up:** What should be logged safely?
- **Common Mistake:** Claiming Uvicorn access logs cover pipeline observability.
- **How to Impress Interviewer:** Recommend correlation IDs, stage timings, counts, and sanitized errors without secrets or source leakage.

### 76. Is there a health endpoint?
- **Question:** Does the project expose readiness or health checks?
- **Ideal Answer:** No dedicated health or readiness route exists.
- **Expected Follow-up:** What dependencies should readiness cover?
- **Common Mistake:** Calling `/analyze` a health check.
- **How to Impress Interviewer:** Separate liveness from model/index/Groq readiness.

## Streamlit Frontend (77–88)

### 77. Where does the frontend send requests?
- **Question:** What backend URL does Streamlit use?
- **Ideal Answer:** It hard-codes `http://127.0.0.1:8000` in `API_URL`.
- **Expected Follow-up:** What deployment issue follows?
- **Common Mistake:** Saying it reads the backend URL from `.env`.
- **How to Impress Interviewer:** Recommend environment-based configuration for containers and hosted deployments.

### 78. How is analysis triggered?
- **Question:** What happens when “Analyze Repository” is clicked?
- **Ideal Answer:** Streamlit posts `{"repo_url": repo_url}` to `/analyze`, then displays summary metrics and independently builds a local dependency graph.
- **Expected Follow-up:** Does it call `/architecture`?
- **Common Mistake:** Saying the backend architecture endpoint supplies the graph.
- **How to Impress Interviewer:** Identify this duplicate backend/frontend responsibility.

### 79. Which summary metrics are shown?
- **Question:** Which analysis metrics does the UI display?
- **Ideal Answer:** Total files, total chunks, languages, and up to five Python module filenames.
- **Expected Follow-up:** Where are values computed?
- **Common Mistake:** Saying the browser calculates them.
- **How to Impress Interviewer:** Note that “main modules” means first encountered Python files, not importance-ranked modules.

### 80. How are languages displayed?
- **Question:** How does the frontend render summary languages?
- **Ideal Answer:** It joins list values with commas, otherwise renders the value directly.
- **Expected Follow-up:** Is ordering stable?
- **Common Mistake:** Claiming languages are sorted.
- **How to Impress Interviewer:** Observe that the backend converts a set to a list, so order is not guaranteed.

### 81. How does the UI derive the local repo path?
- **Question:** How does Streamlit locate a cloned repository for graphing?
- **Ideal Answer:** It takes the final URL segment and joins it with `data`.
- **Expected Follow-up:** Does it strip `.git`?
- **Common Mistake:** Assuming it calls `clone_repository` for the path.
- **How to Impress Interviewer:** Spot that unlike the loader, the UI does not remove `.git`, causing a path mismatch for such URLs.

### 82. How is the dependency graph rendered?
- **Question:** Which libraries render the frontend dependency graph?
- **Ideal Answer:** Streamlit creates a NetworkX directed graph, draws it with Matplotlib, and displays the figure with `st.pyplot`.
- **Expected Follow-up:** What are graph nodes?
- **Common Mistake:** Saying FAISS renders architecture.
- **How to Impress Interviewer:** Note imported modules may be external names while source nodes are bare filenames.

### 83. How is a question submitted?
- **Question:** What payload does the “Ask AI” action send?
- **Ideal Answer:** It posts `{"question": question}` to `/ask`.
- **Expected Follow-up:** How does it identify the repository?
- **Common Mistake:** Saying the repository URL is sent with every question.
- **How to Impress Interviewer:** Highlight reliance on the backend's single global current index.

### 84. How are backend failures shown?
- **Question:** How does the UI handle non-200 responses?
- **Ideal Answer:** It displays generic `st.error` messages for analysis or asking.
- **Expected Follow-up:** Are network exceptions caught?
- **Common Mistake:** Saying all failures become friendly UI errors.
- **How to Impress Interviewer:** Note `requests.post` exceptions and JSON decoding failures are not caught.

### 85. Are request timeouts configured?
- **Question:** Do frontend HTTP calls set timeouts?
- **Ideal Answer:** No. Both `requests.post` calls omit a timeout and may wait indefinitely.
- **Expected Follow-up:** What would production use?
- **Common Mistake:** Assuming Streamlit's spinner imposes a timeout.
- **How to Impress Interviewer:** Recommend connect/read timeouts and background job polling for long analysis.

### 86. How is answer text rendered?
- **Question:** How does Streamlit render the generated answer?
- **Ideal Answer:** It interpolates the answer into an HTML `<div>` and passes `unsafe_allow_html=True`.
- **Expected Follow-up:** What risk exists?
- **Common Mistake:** Saying Streamlit always escapes this output.
- **How to Impress Interviewer:** Flag model-output HTML injection and recommend safe Markdown/text rendering or sanitization.

### 87. Does the frontend preserve analysis state?
- **Question:** Does the UI use `st.session_state` for repository identity or results?
- **Ideal Answer:** No explicit session state is used; backend global state carries the active index.
- **Expected Follow-up:** What happens on reruns?
- **Common Mistake:** Assuming Streamlit widgets imply durable analysis ownership.
- **How to Impress Interviewer:** Recommend explicit analysis IDs stored per Streamlit session.

### 88. What visual customization exists?
- **Question:** How is the frontend styled?
- **Ideal Answer:** It injects extensive custom CSS and Google Fonts through `st.markdown`, using a dark green-accented interface.
- **Expected Follow-up:** Is the font dependency local?
- **Common Mistake:** Saying styling is entirely native Streamlit theming.
- **How to Impress Interviewer:** Note external font loading and brittle `data-testid` selectors as maintenance concerns.

## Summary, Architecture, and Operations (89–100)

### 89. How are languages detected?
- **Question:** How does `generate_repo_summary` detect languages?
- **Ideal Answer:** It adds language names to a set based on `.py`, `.js`, `.ts`, and `.java` filename suffixes.
- **Expected Follow-up:** Are C and C++ reported?
- **Common Mistake:** Assuming all loader-supported extensions appear in the summary.
- **How to Impress Interviewer:** Point out the mismatch: C and C++ are indexed but omitted from language reporting.

### 90. How are main modules selected?
- **Question:** How are `main_modules` chosen?
- **Ideal Answer:** Every Python filename is appended during traversal, then the first five are returned.
- **Expected Follow-up:** Are paths preserved?
- **Common Mistake:** Calling them the five most important modules.
- **How to Impress Interviewer:** Note duplicate filenames from different directories are ambiguous.

### 91. What does `total_chunks` mean?
- **Question:** What exactly does the summary's `total_chunks` represent?
- **Ideal Answer:** It is `len(chunks)`, the number of fixed character slices created from supported files.
- **Expected Follow-up:** Does it count architecture nodes?
- **Common Mistake:** Treating it as token count.
- **How to Impress Interviewer:** Connect changes in chunk size directly to this metric.

### 92. What does the dependency analyzer parse?
- **Question:** Which files does `build_dependency_graph` parse?
- **Ideal Answer:** It walks the repository and parses only `.py` files with Python's `ast` module.
- **Expected Follow-up:** What happens on syntax errors?
- **Common Mistake:** Saying it handles JavaScript imports.
- **How to Impress Interviewer:** Distinguish indexing language support from architecture support.

### 93. Which imports are extracted?
- **Question:** Which Python AST nodes contribute dependencies?
- **Ideal Answer:** `ast.Import` contributes each alias name, and `ast.ImportFrom` contributes `node.module` when present.
- **Expected Follow-up:** Are imported symbols captured?
- **Common Mistake:** Saying `from x import y` records `y`.
- **How to Impress Interviewer:** Explain that relative-import level and imported symbol names are not represented.

### 94. What are graph keys?
- **Question:** What keys does the dependency graph dictionary use?
- **Ideal Answer:** Bare Python filenames, not relative or absolute paths.
- **Expected Follow-up:** What collision can occur?
- **Common Mistake:** Saying each key uniquely identifies a module.
- **How to Impress Interviewer:** Note two directories containing `utils.py` overwrite each other.

### 95. What does `visualize_graph` do?
- **Question:** What does the architecture module's visualization helper do?
- **Ideal Answer:** It creates a directed NetworkX graph from dependency mappings, draws it with Matplotlib, and calls `plt.show()`.
- **Expected Follow-up:** Is it used by the API?
- **Common Mistake:** Saying `/architecture` returns an image.
- **How to Impress Interviewer:** Note the frontend independently duplicates similar drawing logic.

### 96. How does `run.sh` start services?
- **Question:** How does the startup script launch the application?
- **Ideal Answer:** It starts Uvicorn with reload in the background, then runs Streamlit in the foreground.
- **Expected Follow-up:** How are processes stopped?
- **Common Mistake:** Saying both services are production-managed.
- **How to Impress Interviewer:** Identify it as a development convenience without robust signal handling or supervision.

### 97. Why is Uvicorn reload significant?
- **Question:** What does `--reload` imply in `run.sh`?
- **Ideal Answer:** Uvicorn watches source changes and restarts the backend, which is useful for development but not a production setting.
- **Expected Follow-up:** What happens to the index?
- **Common Mistake:** Saying reload preserves the in-memory pipeline.
- **How to Impress Interviewer:** Connect every reload to loss of analyzed state.

### 98. Are dependency versions pinned?
- **Question:** Does `requirements.txt` pin package versions?
- **Ideal Answer:** No. It lists package names without versions.
- **Expected Follow-up:** What risk follows?
- **Common Mistake:** Saying pip will always reproduce the same environment.
- **How to Impress Interviewer:** Recommend tested version constraints and a lockfile for reproducible deployments.

### 99. What documentation mismatch should you notice?
- **Question:** Identify one claim that is stronger than the implementation.
- **Ideal Answer:** The UI says answers have “no hallucinations,” but retrieval and prompting cannot guarantee that; sources are not structurally returned either.
- **Expected Follow-up:** How should wording change?
- **Common Mistake:** Defending the claim because RAG is used.
- **How to Impress Interviewer:** Prefer “grounded in retrieved code context” and expose citations.

### 100. How would you summarize current versus production design?
- **Question:** Give a concise current-versus-production summary.
- **Ideal Answer:** Current code is a synchronous single-process demo with fixed chunking, one global in-memory index, and minimal validation; production needs isolation, persistence, jobs, security controls, observability, and evaluation.
- **Expected Follow-up:** What would you prioritize first?
- **Common Mistake:** Describing recommended components as already implemented.
- **How to Impress Interviewer:** Prioritize safe URL ingestion and repository-scoped state before retrieval refinements.
