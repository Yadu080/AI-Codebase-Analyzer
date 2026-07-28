# Chapter 15 — Deployment

## 0. Current reality vs proposed

**Current:** `./run.sh` starts Uvicorn + Streamlit on a developer machine. No Docker, no CI/CD, no cloud manifests in-repo.

Everything below marked **PROPOSED** is how you would deploy — study it for interviews, do not claim it ships today.

---

## 1. Current local deployment

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create .env with GROQ_API_KEY
./run.sh
# API :8000  UI :8501
```

### Environment variables
| Var | Required | Purpose |
|---|---|---|
| `GROQ_API_KEY` | Yes for `/ask` | LLM auth |

### Logging / monitoring / alerting
Print statements only. No structured logs, metrics, traces, alerts.

### Rollback / versioning
Git checkout locally. No blue-green.

---

## 2. PROPOSED Dockerfile (example)

```dockerfile
# PROPOSED — not in repo today
FROM python:3.11-slim
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY frontend.py .
ENV GROQ_API_KEY=""
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Notes: UI may be separate image; bake-in model download at build or first run; never bake API keys.

### Docker vs Podman
Both OCI containers; Podman daemonless/rootless often preferred in locked-down enterprises. Functionally similar for this app.

---

## 3. PROPOSED GitHub Actions CI

```yaml
# PROPOSED
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt pytest
      - run: pytest -q
```

Add: lint, SCA (pip-audit), build/push image on main.

---

## 4. Cloud options comparison

| Platform | Fit | Pros | Cons |
|---|---|---|---|
| **GCP Cloud Run** | Good for API containers | Scale to zero, simple | Cold start + model load painful |
| **AWS ECS/Fargate** | Good | Familiar AWS | Model cold start |
| **Azure Container Apps** | Good | Azure ecosystem | Same cold start |
| **GKE/EKS/AKS (K8s)** | When many services | Control, GPUs | Ops cost |
| **Single VM** | Tiny demos | Simple | No HA |

### Cloud Run vs Kubernetes
| | Cloud Run | Kubernetes |
|---|---|---|
| Ops burden | Low | High |
| Scale to 0 | Yes | Possible with care |
| GPU | Limited/varies | First-class |
| Sidecars/mesh | Limited | Rich |
| When | Few containers | Platform complexity justified |

---

## 5. Secrets

PROPOSED: Cloud secret manager → inject as env at runtime. Rotate Groq keys. Separate prod/dev projects.

---

## 6. Logging, monitoring, alerting (PROPOSED)

- Structured JSON logs with `request_id`, `repo_id`
- Metrics: analyze_seconds, ask_seconds, embed_seconds, groq_errors, queue_depth
- Traces: OpenTelemetry across API → worker → LLM
- Alerts: error rate, P95, budget burn, disk clone usage

---

## 7. Deployment strategies (PROPOSED)

| Strategy | Meaning | Use when |
|---|---|---|
| Rolling | Gradually replace | Default |
| Blue-green | Two envs, switch traffic | Fast rollback |
| Canary | % traffic to new | LLM/prompt changes |

**Versioning:** version API + **embedding model id** + index format together.

---

## 8. Rollback

Keep previous image + previous index snapshot. Prompt/model changes need paired eval.

---

## Interview questions

### Beginner

#### 1. How run?
**Question:** How do you run the app?
**Ideal Answer:** run.sh starts uvicorn and streamlit; need .env GROQ_API_KEY.
**Why interviewer asked it:** Basics.
**Common mistakes:** Claiming Kubernetes.
**Follow-up questions:** Ports?

#### 2. Docker today?
**Question:** Is it containerized?
**Ideal Answer:** Not currently; I can describe a Dockerfile I'd add.
**Why interviewer asked it:** Honesty.
**Common mistakes:** Yes we use Docker.
**Follow-up questions:** Why git in image?


### Intermediate

#### 1. Cold start
**Question:** Why Cloud Run hurts this app?
**Ideal Answer:** Loading MiniLM each cold start adds seconds; need min instances or external embed service.
**Why interviewer asked it:** Cloud tradeoffs.
**Common mistakes:** Cloud Run always best.
**Follow-up questions:** Mitigations?

#### 2. Secrets
**Question:** How manage GROQ_API_KEY in cloud?
**Ideal Answer:** Secret Manager + IAM; never in git or image layers.
**Why interviewer asked it:** Security ops.
**Common mistakes:** Hardcode.
**Follow-up questions:** Rotation?


### Advanced

#### 1. Blue green LLM
**Question:** How blue-green a prompt change?
**Ideal Answer:** Two generation configs; canary metrics on groundedness/latency/cost; auto rollback.
**Why interviewer asked it:** Release eng.
**Common mistakes:** Just push.
**Follow-up questions:** Shadow traffic?


### FAANG

#### 1. Multi-cloud
**Question:** Would you multi-cloud this?
**Ideal Answer:** Usually no initially — cost/complexity; maybe multi-region single cloud first.
**Why interviewer asked it:** Judgment.
**Common mistakes:** Always multi-cloud.
**Follow-up questions:** When yes?


### Trick

#### 1. CI present?
**Question:** Show me your CI config.
**Ideal Answer:** There isn't one in the repo yet — here's what I would add and why.
**Why interviewer asked it:** Catch resume inflation.
**Common mistakes:** Inventing files.
**Follow-up questions:** First test you'd add?



---

## Appendix A — PROPOSED docker-compose

```yaml
# PROPOSED — not shipped
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      GROQ_API_KEY: ${GROQ_API_KEY}
    volumes:
      - ./data:/app/data
  ui:
    build: .
    command: streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0
    ports: ["8501:8501"]
    depends_on: [api]
```

## Appendix B — Health checks (proposed)

- `GET /healthz` → process up
- `GET /readyz` → model loaded; disk writable
- Distinguish alive vs ready for k8s/Cloud Run

## Appendix C — Rollback narrative

1. Keep previous container image tag  
2. Keep previous FAISS snapshot beside new  
3. Canary 5% traffic on new prompt/model  
4. Watch groundedness + error rate + $ / query  
5. Instant traffic revert if burn  

