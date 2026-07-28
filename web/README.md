# Web frontend (Vercel)

Next.js 14 App Router UI for AI Codebase Analyzer.

## Develop

```bash
cp .env.local.example .env.local
npm install
npm run dev
```

## Deploy on Vercel

1. Import the GitHub repo in Vercel.
2. **Root Directory:** `web`
3. Env: `NEXT_PUBLIC_API_URL=<public FastAPI base URL>`
4. Deploy.

`vercel.json` in this folder marks the project as Next.js.
