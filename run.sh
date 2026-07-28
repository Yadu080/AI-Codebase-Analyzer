#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Starting FastAPI backend on :8000..."
uvicorn app.api:app --reload --host 127.0.0.1 --port 8000 &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT

if [ -d "web/node_modules" ]; then
  echo "Starting Next.js frontend on :3000..."
  (cd web && npm run dev)
else
  echo "web/node_modules missing — run: cd web && npm install"
  echo "Falling back to Streamlit on :8501..."
  streamlit run frontend.py
fi
