"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  analyzeRepo,
  askQuestion,
  fetchArchitecture,
  getApiUrl,
  type RepoSummary,
} from "@/lib/api";

const EXAMPLE_QUESTIONS = [
  "How does routing work?",
  "Where is authentication handled?",
  "What is the main entry point?",
];

function useCountUp(target: number, duration = 900) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!target) {
      setValue(0);
      return;
    }
    let start: number | null = null;
    let raf = 0;

    const step = (ts: number) => {
      if (start === null) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));
      if (progress < 1) raf = requestAnimationFrame(step);
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);

  return value;
}

function handleSpotlight(e: React.MouseEvent<HTMLElement>) {
  const rect = e.currentTarget.getBoundingClientRect();
  e.currentTarget.style.setProperty("--mx", `${e.clientX - rect.left}px`);
  e.currentTarget.style.setProperty("--my", `${e.clientY - rect.top}px`);
}

export function AnalyzerApp() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/pallets/flask");
  const [question, setQuestion] = useState("");
  const [summary, setSummary] = useState<RepoSummary | null>(null);
  const [architecture, setArchitecture] = useState<Record<
    string,
    string[]
  > | null>(null);
  const [answer, setAnswer] = useState("");
  const [analyzeStatus, setAnalyzeStatus] = useState<{
    type: "ok" | "err" | "busy";
    text: string;
  } | null>(null);
  const [askStatus, setAskStatus] = useState<{
    type: "ok" | "err" | "busy";
    text: string;
  } | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [asking, setAsking] = useState(false);

  const ready = Boolean(summary);
  const filesCount = useCountUp(summary?.total_files ?? 0);
  const chunksCount = useCountUp(summary?.total_chunks ?? 0);
  const apiHost = useMemo(() => {
    try {
      return new URL(getApiUrl()).host;
    } catch {
      return getApiUrl();
    }
  }, []);

  async function onAnalyze(e: FormEvent) {
    e.preventDefault();
    if (!repoUrl.trim()) {
      setAnalyzeStatus({ type: "err", text: "Enter a GitHub repository URL." });
      return;
    }

    setAnalyzing(true);
    setAnalyzeStatus({
      type: "busy",
      text: "Cloning, chunking, and building the vector index…",
    });
    setAnswer("");
    setAskStatus(null);
    setArchitecture(null);

    try {
      const data = await analyzeRepo(repoUrl.trim());
      setSummary(data.summary);
      setAnalyzeStatus({
        type: "ok",
        text: `${data.message} · ${data.chunks} chunks indexed`,
      });

      try {
        const arch = await fetchArchitecture(repoUrl.trim());
        setArchitecture(arch.architecture);
      } catch {
        setArchitecture(null);
      }
    } catch (err) {
      setSummary(null);
      setAnalyzeStatus({
        type: "err",
        text:
          err instanceof Error
            ? err.message
            : "Analyze failed. Is the API running and reachable?",
      });
    } finally {
      setAnalyzing(false);
    }
  }

  async function onAsk(e: FormEvent) {
    e.preventDefault();
    if (!question.trim()) {
      setAskStatus({ type: "err", text: "Type a question about the codebase." });
      return;
    }
    if (!ready) {
      setAskStatus({
        type: "err",
        text: "Analyze a repository first so the index exists.",
      });
      return;
    }

    setAsking(true);
    setAskStatus({
      type: "busy",
      text: "Retrieving relevant chunks and generating an answer…",
    });
    setAnswer("");

    try {
      const data = await askQuestion(question.trim());
      setAnswer(data.answer);
      setAskStatus({ type: "ok", text: "Answer grounded in retrieved code." });
    } catch (err) {
      setAskStatus({
        type: "err",
        text:
          err instanceof Error
            ? err.message
            : "Ask failed. Re-analyze if the API restarted.",
      });
    } finally {
      setAsking(false);
    }
  }

  const graphEntries = architecture
    ? Object.entries(architecture).slice(0, 40)
    : [];

  return (
    <div className="app-shell">
      <header className="topnav">
        <div className="brand">
          <div className="brand-mark" aria-hidden />
          <div className="brand-text">
            <span className="brand-name">AI Codebase Analyzer</span>
            <span className="brand-sub">RAG · FAISS · Groq</span>
          </div>
        </div>
        <div className="nav-links">
          <span className="nav-chip">API · {apiHost}</span>
          <a
            className="nav-chip"
            href="https://github.com/Yadu080"
            target="_blank"
            rel="noreferrer"
          >
            github.com/Yadu080
          </a>
        </div>
      </header>

      <section className="hero">
        <div className="hero-badge">
          <span className="pulse" aria-hidden />
          Retrieval-Augmented Generation
        </div>
        <h1>
          Read any repo with <span>semantic precision</span>
        </h1>
        <p className="hero-copy">
          Clone a public GitHub repository, embed code into a FAISS index, and
          ask questions answered from real retrieved snippets — not guesswork.
        </p>
        <div className="hero-meta">
          <span>Built by Yadunandan M Nimbalkar</span>
          <span>·</span>
          <a href="https://github.com/Yadu080" target="_blank" rel="noreferrer">
            Portfolio on GitHub
          </a>
        </div>
      </section>

      <main className="workspace">
        <section className="panel" onMouseMove={handleSpotlight}>
          <div className="panel-head">
            <div>
              <div className="step-label">Step 01</div>
              <h2>Analyze repository</h2>
              <p>
                Clone, filter source files, chunk at 500 characters, embed with
                MiniLM, and index with FAISS IndexFlatL2.
              </p>
            </div>
          </div>
          <div className="panel-body">
            <form className="field-row" onSubmit={onAnalyze}>
              <input
                className="field"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/owner/repo"
                aria-label="GitHub repository URL"
                disabled={analyzing}
              />
              <button className="btn btn-primary" type="submit" disabled={analyzing}>
                {analyzing ? (
                  <>
                    <span className="spinner" aria-hidden />
                    Analyzing
                  </>
                ) : (
                  <>Analyze repository</>
                )}
              </button>
            </form>

            {analyzeStatus && (
              <div className={`status status-${analyzeStatus.type}`} role="status">
                {analyzeStatus.text}
              </div>
            )}

            {summary && (
              <>
                <div className="metrics">
                  <div className="metric">
                    <div className="metric-label">Total files</div>
                    <div className="metric-value">{filesCount}</div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">Total chunks</div>
                    <div className="metric-value">{chunksCount}</div>
                  </div>
                  <div className="metric">
                    <div className="metric-label">Languages</div>
                    <div className="metric-value sm">
                      {summary.languages?.length
                        ? summary.languages.join(", ")
                        : "—"}
                    </div>
                  </div>
                </div>

                {summary.main_modules?.length > 0 && (
                  <div className="module-row">
                    {summary.main_modules.map((m) => (
                      <span className="pill" key={m}>
                        {m}
                      </span>
                    ))}
                  </div>
                )}

                {graphEntries.length > 0 && (
                  <div className="graph-wrap">
                    <h3>Python import graph</h3>
                    <ul className="graph-list">
                      {graphEntries.map(([file, deps]) => (
                        <li key={file}>
                          <span className="graph-file">{file}</span>
                          <span className="graph-deps">
                            {deps.length ? deps.join(", ") : "—"}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        </section>

        <section className="panel" onMouseMove={handleSpotlight}>
          <div className="panel-head">
            <div>
              <div className="step-label">Step 02</div>
              <h2>Ask the AI</h2>
              <p>
                Retrieve the top-5 nearest code chunks, then generate an
                explanation with Groq Llama 3.3 70B.
              </p>
            </div>
          </div>
          <div className="panel-body">
            <form className="field-row" onSubmit={onAsk}>
              <input
                className="field"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="How does routing work in this project?"
                aria-label="Question about the codebase"
                disabled={asking}
              />
              <button
                className="btn btn-primary"
                type="submit"
                disabled={asking || !ready}
              >
                {asking ? (
                  <>
                    <span className="spinner" aria-hidden />
                    Asking
                  </>
                ) : (
                  <>Ask AI</>
                )}
              </button>
            </form>

            <div className="examples">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  className="example"
                  onClick={() => setQuestion(q)}
                >
                  {q}
                </button>
              ))}
            </div>

            {askStatus && (
              <div className={`status status-${askStatus.type}`} role="status">
                {askStatus.text}
              </div>
            )}

            {answer && <pre className="answer">{answer}</pre>}
          </div>
        </section>
      </main>

      <footer className="footer">
        <span>
          FastAPI · SentenceTransformers · FAISS · Groq · Deployed UI on Vercel
        </span>
        <a href="https://github.com/Yadu080" target="_blank" rel="noreferrer">
          Yadunandan M Nimbalkar
        </a>
      </footer>
    </div>
  );
}
