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

---

## Project structure

```
ai-codebase-analyzer/
├── app/                 # FastAPI RAG backend
├── web/                 # Next.js frontend (deploy to Vercel)
├── frontend.py          # Optional Streamlit UI
├── requirements.txt
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

Pick any Python host (Render, Railway, Fly.io, a VPS):

```bash
uvicorn app.api:app --host 0.0.0.0 --port $PORT
```

Set secrets on the API host:

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq LLM access |
| `CORS_ORIGINS` | Your Vercel URL(s), comma-separated |

Example:

```
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

Without a public API URL, the Vercel site still **loads and looks polished**; Analyze/Ask will fail until the backend is reachable.

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

---

## Author

Yadunandan M Nimbalkar — [github.com/Yadu080](https://github.com/Yadu080)
