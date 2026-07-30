# AI Codebase Analyzer

AI Codebase Analyzer explores GitHub repositories with **Retrieval-Augmented Generation (RAG)**.

It clones a public repo, chunks source files, embeds them with SentenceTransformers (`all-MiniLM-L6-v2`), indexes vectors in FAISS (`IndexFlatL2`), retrieves the nearest chunks for a question, and explains them with Groq (`llama-3.3-70b-versatile`).

---

## Features

- Analyze public GitHub repositories
- Semantic code search with FAISS
- Grounded Q&A via Groq
- Repository summary + Python import graph
- **Modern Next.js UI** (Vercel-ready)
- Optional Streamlit UI for quick local demos

---

## Architecture

```
Browser (Next.js on Vercel)
        │  HTTPS
        ▼
FastAPI backend (local / Render / Railway / Fly)
        │
        ├── Git clone
        ├── Chunk (500 chars)
        ├── Embed (MiniLM 384-d)
        ├── FAISS IndexFlatL2
        └── Groq LLM
```

> **Note:** The heavy ML stack (SentenceTransformers + FAISS) cannot run inside Vercel serverless. Deploy the **UI on Vercel** and the **API on a Python host**.
> **RAM note:** SentenceTransformers + FAISS comfortably need 1-2GB resident memory. Render's free/Starter tiers cap out at 512MB, so this repo deploys the API to **Hugging Face Spaces** (free Docker CPU tier = 16GB RAM) by default — see [Deploy the API](#deploy-the-api-required-for-live-analyzeask) below for why, and for the Render option if you'd rather stay there.

---

## Project structure

```
ai-codebase-analyzer/
├── app/                    # FastAPI RAG backend
├── web/                    # Next.js frontend (deploy to Vercel)
├── frontend.py             # Optional Streamlit UI
├── requirements.txt        # Full deps (local dev incl. Streamlit)
├── requirements-api.txt    # Lean deps for deploying just the API
├── Dockerfile              # For Hugging Face Spaces / any Docker host
├── render.yaml             # Render blueprint (optional, see RAM note)
├── Procfile
├── run.sh
└── .env.example
```

---

## Local setup

### 1. Backend

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # set GROQ_API_KEY
uvicorn app.api:app --reload --port 8000
```

### 2. Frontend (Next.js)

```bash
cd web
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### One-command (API + Next.js)

```bash
cd web && npm install && cd ..
./run.sh
```

### Optional Streamlit UI

```bash
streamlit run frontend.py
```

---

## Deploy on Vercel (frontend)

1. Push this repo to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) → import the repo.
3. Set **Root Directory** to `web`.
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your public FastAPI URL  
     Example: `https://ai-codebase-analyzer-api.onrender.com`
5. Deploy.

The Vercel project settings should look like:

| Setting | Value |
|---|---|
| Framework | Next.js |
| Root Directory | `web` |
| Build Command | `npm run build` (default) |
| Output | Next.js default |

Config files used:

- `web/vercel.json`
- `web/package.json`
- `web/.env.local.example`

### Deploy the API (required for live analyze/ask)

Set these secrets on whichever host you pick:

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq LLM access |
| `CORS_ORIGINS` | Your Vercel URL(s), comma-separated |

Example:

```
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

Without a public API URL, the Vercel site still **loads and looks polished**; Analyze/Ask will fail until the backend is reachable.

#### Why Render's free tier alone isn't enough

SentenceTransformers (`all-MiniLM-L6-v2`) + FAISS realistically need **1-2GB** of resident memory once the model, its inference buffers, and the vector index are loaded. Render's Free *and* Starter plans are hard-capped at **512MB** — that's a platform limit, not something a config change can lift. This repo already trims what it can for free (see below), but it can still tip over 512MB on a real repo, so the recommended path is to deploy the same, unmodified backend to a host whose free tier actually has the RAM.

**Option A — Hugging Face Spaces (recommended, free, no card required, ~16GB RAM)**

The exact same FastAPI/SentenceTransformers/FAISS/Groq code, just running on a host with real headroom. Uses the `Dockerfile` at the repo root.

1. Create a Space at [huggingface.co/new-space](https://huggingface.co/new-space) → SDK: **Docker** → hardware: **CPU basic (free)**.
2. Add it as a git remote and push this repo to it:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/<space-name>
   git push space claude/frontend-design-deploy-ram-mn3kie:main
   ```
3. In the Space's **Settings → Repository secrets**, add `GROQ_API_KEY` and `CORS_ORIGINS`.
4. The Space builds the `Dockerfile` and serves the API at `https://<your-username>-<space-name>.hf.space`. Use that as `NEXT_PUBLIC_API_URL` in Vercel.

Free Spaces sleep after a period of inactivity and wake on the next request (~30-60s cold start) — same trade-off as Render's free tier, just with enough RAM to actually run this stack.

**Option B — Render (works, but needs the paid Standard plan for headroom)**

`render.yaml` is included for a one-click blueprint deploy (Root: repo root, uses `requirements-api.txt`). It'll deploy fine on the Free plan, but you're likely to see the process get OOM-killed on non-trivial repos. To run it reliably on Render, switch the plan to **Standard (2GB RAM, ~$25/mo)** in `render.yaml` or the dashboard.

```bash
uvicorn app.api:app --host 0.0.0.0 --port $PORT --workers 1
```

**Memory trims already applied in this repo** (free, don't change the RAG pipeline itself):

- CPU-only PyTorch wheel (`requirements.txt` / `requirements-api.txt`) — the default PyPI `torch` wheel silently pulls ~1-2GB of unused CUDA/NVIDIA packages even on CPU-only hosts.
- The embedding model loads lazily on first `/analyze` or `/ask` call instead of at import time, so idle memory (and `/health`) stays light.
- `matplotlib`/`networkx` (only used by an unused local-visualization helper) are imported lazily instead of at module load.
- `/analyze` caps indexing at `MAX_CHUNKS` (env var, default 4000) so one huge repo can't blow past a host's memory ceiling.
- `--workers 1` — extra Uvicorn workers each load a full copy of the model into memory.

---

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness + whether an index is loaded |
| POST | `/analyze` | Clone + index a repo |
| POST | `/ask` | Question → retrieved chunks → LLM answer |
| POST | `/architecture` | Python AST import graph |

Interactive docs: `http://127.0.0.1:8000/docs`

---

## Tech stack

| Layer | Tech |
|---|---|
| UI | Next.js 14, React, TypeScript |
| API | FastAPI, Uvicorn |
| Embeddings | SentenceTransformers `all-MiniLM-L6-v2` |
| Vectors | FAISS `IndexFlatL2` |
| LLM | Groq `llama-3.3-70b-versatile` |
| Deploy UI | Vercel |

---

## Limitations

- Vector index is **in-memory** (lost on API restart)
- Best results on repos with supported source extensions
- Backend must run where Git + ML deps are available (not Vercel Functions)
- Backend needs **~1-2GB RAM** at peak (model + index) — see [Deploy the API](#deploy-the-api-required-for-live-analyzeask) for free hosts with enough headroom
- `/analyze` truncates indexing to `MAX_CHUNKS` (default 4000) on very large repositories to protect low-RAM hosts

---

## Author

Yadunandan M Nimbalkar — [github.com/Yadu080](https://github.com/Yadu080)
