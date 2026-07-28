import streamlit as st
import requests
from app.architecture import build_dependency_graph
import networkx as nx
import matplotlib.pyplot as plt
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="AI Codebase Analyzer",
    page_icon="🤖",
    layout="wide"
)

# ─── GLOBAL STYLES ───────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">

<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #06060a !important;
    color: #e2e2f0 !important;
}

[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(rgba(0,255,157,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,157,0.025) 1px, transparent 1px),
        #06060a !important;
    background-size: 40px 40px, 40px 40px, auto !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebarNav"] {
    background: transparent !important;
}

/* ── Typography ── */
h1, h2, h3, h4, p, label, div {
    font-family: 'Syne', sans-serif !important;
}

/* ── Hero Banner ── */
.hero-wrap {
    position: relative;
    padding: 56px 0 40px;
    text-align: center;
    overflow: hidden;
}

.hero-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 70% 60% at 50% 0%, rgba(0,255,157,0.07) 0%, transparent 70%);
    pointer-events: none;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,255,157,0.08);
    border: 1px solid rgba(0,255,157,0.22);
    border-radius: 2px;
    padding: 5px 14px;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px;
    color: #00ff9d;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 22px;
}

.hero-badge-dot {
    width: 6px; height: 6px;
    background: #00ff9d;
    border-radius: 50%;
    display: inline-block;
    animation: blink 2s infinite;
}

@keyframes blink {
    0%,100% { opacity:1; } 50% { opacity:0.3; }
}

.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(36px, 5vw, 68px);
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
    color: #e2e2f0;
    margin: 0 0 12px;
}

.hero-title .accent { color: #00ff9d; }

.hero-sub {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px;
    color: #6b6b8a;
    margin-bottom: 28px;
    line-height: 1.7;
}

.hero-author {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: #0d0d14;
    border: 1px solid #1e1e2e;
    border-radius: 2px;
    padding: 10px 20px;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px;
    color: #9090b8;
}

.hero-author a {
    color: #ff6b35;
    text-decoration: none;
    border-bottom: 1px solid rgba(255,107,53,0.35);
    padding-bottom: 1px;
    transition: color 0.2s;
}

.hero-author a:hover { color: #00ff9d; border-color: #00ff9d; }

/* ── Section Cards ── */
.section-card {
    background: #0d0d14;
    border: 1px solid #1e1e2e;
    border-radius: 4px;
    padding: 32px 36px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

.section-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00ff9d, transparent);
}

.section-label {
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px;
    color: #00ff9d;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 20px;
}

.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #1e1e2e, transparent);
}

.section-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 22px;
    font-weight: 700;
    color: #e2e2f0;
    margin-bottom: 6px;
}

.section-desc {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px;
    color: #6b6b8a;
    margin-bottom: 22px;
    line-height: 1.7;
}

/* ── Divider ── */
.custom-divider {
    height: 1px;
    background: linear-gradient(to right, transparent, #1e1e2e 30%, #1e1e2e 70%, transparent);
    margin: 36px 0;
}

/* ── Input overrides ── */
[data-testid="stTextInput"] input {
    background: #06060a !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 2px !important;
    color: #e2e2f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #00ff9d !important;
    box-shadow: 0 0 0 3px rgba(0,255,157,0.08) !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: #3a3a5c !important;
}

/* ── Button overrides ── */
[data-testid="stButton"] button {
    background: #00ff9d !important;
    color: #06060a !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.06em !important;
    padding: 10px 28px !important;
    transition: opacity 0.2s, transform 0.15s !important;
    cursor: pointer !important;
}

[data-testid="stButton"] button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

[data-testid="stButton"] button:active {
    transform: translateY(0) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: #00ff9d !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

/* ── Success / Error alerts ── */
[data-testid="stAlert"] {
    background: rgba(0,255,157,0.06) !important;
    border: 1px solid rgba(0,255,157,0.2) !important;
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: #00ff9d !important;
}

/* Error variant */
[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(255,107,53,0.06) !important;
    border-color: rgba(255,107,53,0.2) !important;
    color: #ff6b35 !important;
}

/* ── Metric / Summary cards ── */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}

.metric-card {
    background: #06060a;
    border: 1px solid #1e1e2e;
    border-radius: 2px;
    padding: 16px 20px;
}

.metric-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px;
    color: #6b6b8a;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.metric-value {
    font-family: 'Syne', sans-serif !important;
    font-size: 22px;
    font-weight: 800;
    color: #00ff9d;
}

.module-pill {
    display: inline-block;
    background: rgba(124,58,237,0.1);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 2px;
    padding: 3px 10px;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px;
    color: #c4b5fd;
    margin: 3px 4px 3px 0;
}

/* ── Answer box ── */
.answer-box {
    background: #06060a;
    border: 1px solid #1e1e2e;
    border-left: 3px solid #00ff9d;
    border-radius: 2px;
    padding: 20px 24px;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px;
    color: #c8c8e0;
    line-height: 1.8;
    white-space: pre-wrap;
}

/* ── Footer ── */
.footer-bar {
    border-top: 1px solid #1e1e2e;
    padding: 28px 0 16px;
    text-align: center;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px;
    color: #3a3a5c;
    letter-spacing: 0.12em;
}

.footer-bar a {
    color: #ff6b35;
    text-decoration: none;
}

/* Hide streamlit default chrome */
#MainMenu, footer[data-testid="stFooter"] { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">
        <span class="hero-badge-dot"></span>
        RAG · Retrieval-Augmented Generation
    </div>
    <div class="hero-title">
        AI Codebase <span class="accent">Analyzer</span>
    </div>
    <div class="hero-sub">
        Clone any GitHub repo · Semantic search across code · Ask AI anything
    </div>
    <div class="hero-author">
        <span>⚡</span>
        <span>Yadunandan M Nimbalkar</span>
        <span style="color:#1e1e2e">·</span>
        <a href="https://www.github.com/Yadu080" target="_blank">github.com/Yadu080</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── SECTION 1: ANALYZE ───────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
    <div class="section-label">Step 01</div>
    <div class="section-title">Analyze Repository</div>
    <div class="section-desc">Enter a GitHub URL — the system clones, chunks, and indexes it into a vector database.</div>
</div>
""", unsafe_allow_html=True)

repo_url = st.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/pallets/flask",
    label_visibility="collapsed"
)

if st.button("⟶  Analyze Repository"):
    with st.spinner("Cloning and indexing repository..."):
        response = requests.post(
            f"{API_URL}/analyze",
            json={"repo_url": repo_url}
        )

        if response.status_code == 200:
            data = response.json()
            summary = data["summary"]

            st.success("✓ Repository indexed successfully")

            # Metrics row
            st.markdown(f"""
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Files</div>
                    <div class="metric-value">{summary['total_files']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Chunks</div>
                    <div class="metric-value">{summary['total_chunks']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Languages</div>
                    <div class="metric-value" style="font-size:15px; padding-top:4px; color:#e2e2f0">
                        {', '.join(summary['languages']) if isinstance(summary['languages'], list) else summary['languages']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Modules
            modules_html = "".join(
                f'<span class="module-pill">{m}</span>'
                for m in summary["main_modules"]
            )
            st.markdown(f"""
            <div style="margin-top:4px">
                <div class="metric-label" style="margin-bottom:10px">Main Modules</div>
                {modules_html}
            </div>
            """, unsafe_allow_html=True)
            repo_name = repo_url.split("/")[-1]
            repo_path = os.path.join("data", repo_name)
            graph = build_dependency_graph(repo_path)
            st.subheader("Repository Dependency Graph")

            for file, deps in graph.items():
                st.write(f"{file} → {deps}")
            G = nx.DiGraph()

            for file, deps in graph.items():
                for dep in deps:
                    G.add_edge(file, dep)

            fig, ax = plt.subplots()
            nx.draw(G, with_labels=True, node_size=2000, node_color="lightblue", ax=ax)

            st.pyplot(fig)

        else:
            st.error("✗ Failed to analyze repository. Check the URL and try again.")

# ─── DIVIDER ──────────────────────────────────────────────────────────────────
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ─── SECTION 2: ASK ───────────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
    <div class="section-label">Step 02</div>
    <div class="section-title">Ask the AI</div>
    <div class="section-desc">The retriever finds relevant code chunks, then the LLM answers with full context — no hallucinations.</div>
</div>
""", unsafe_allow_html=True)

question = st.text_input(
    "Your question",
    placeholder="How does Flask implement routing?",
    label_visibility="collapsed"
)

if st.button("⟶  Ask AI"):
    with st.spinner("Retrieving context and generating answer..."):
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question}
        )

        if response.status_code == 200:
            answer = response.json()["answer"]
            st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
        else:
            st.error("✗ Error getting answer from API. Make sure the repository is indexed first.")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
    Built by <a href="https://www.github.com/Yadu080">Yadunandan M Nimbalkar</a>
    &nbsp;·&nbsp; RAG · FAISS · SentenceTransformers · FastAPI
</div>
""", unsafe_allow_html=True)