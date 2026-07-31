#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# Always use an isolated venv, called by full path, so this never collides
# with (or silently runs inside) an active conda/pyenv shell environment.
if [ ! -d "venv" ]; then
  echo "==> Creating virtual environment..."
  python3 -m venv venv
fi

if [ ! -f "venv/bin/uvicorn" ]; then
  echo "==> Installing backend dependencies (first run takes a few minutes)..."
  venv/bin/pip install --upgrade pip >/dev/null
  venv/bin/pip install -r requirements.txt
fi

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo "Created .env — open it and set your GROQ_API_KEY, then rerun ./run.sh"
  exit 1
fi

if grep -q "your_groq_api_key_here" .env; then
  echo ""
  echo "Your .env still has the placeholder GROQ_API_KEY."
  echo "Get a free key at https://console.groq.com/keys, put it in .env, then rerun ./run.sh"
  exit 1
fi

for port in 8000 3000; do
  if lsof -ti:"$port" >/dev/null 2>&1; then
    echo "==> Port $port is in use — freeing it..."
    lsof -ti:"$port" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
done

# No --reload: cloning a repo writes into data/, which would trigger a
# reloader restart and throw away the in-memory index mid-session.
echo "==> Starting FastAPI backend on http://127.0.0.1:8000 ..."
venv/bin/uvicorn app.api:app --host 127.0.0.1 --port 8000 &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT

if [ ! -d "web/node_modules" ]; then
  echo "==> Installing frontend dependencies..."
  (cd web && npm install)
fi

if [ ! -f "web/.env.local" ]; then
  cp web/.env.local.example web/.env.local
fi

echo "==> Starting Next.js frontend on http://localhost:3000 ..."
(cd web && npm run dev)
