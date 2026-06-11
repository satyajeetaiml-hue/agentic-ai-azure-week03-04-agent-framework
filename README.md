# Weeks 3–4 — Microsoft Agent Framework

> **Standalone lab** from the *Agentic AI on Azure — Enterprise Master Class* (12 weeks).
> Each lab is an independent, runnable FastAPI starter. Part of the
> [course series](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure).

---

## 🎯 Learning goal
Use the Agent Framework for memory, connectors, middleware, multi-channel deploy, and YAML-defined orchestration.

## 🏢 Enterprise use case — "Wealth Management Research Assistant" (Financial Services)
An advisor asks for a portfolio summary. A grounded agent pulls holdings (tool) and market data (tool), applies compliance disclaimers (middleware), and streams a narrative back. Memory keeps the advisor's context across the session.

---

## 🧪 What you'll build (lab)
1. Build the agent with short-term + persistent memory (Cosmos DB).
2. Add **middleware** for input/output filtering (PII redaction, disclaimer injection).
3. Define the agent + workflow in **YAML** and stream responses via FastAPI **SSE**.
4. Wire a session cache (Redis) for short-term memory.

> This starter ships with a **runnable mock** of the endpoint so you can run and test
> immediately, then progressively replace the mock with the real Azure implementation.

## 🏗️ Architect's lens
- Memory tiers: session (Redis) vs. durable (Cosmos DB) vs. semantic (AI Search) — cost & consistency trade-offs.
- Middleware as a governance seam — enforce policy without touching agent logic.
- Declarative (YAML) vs. code-first definitions for versioning and CI/CD.

## 🧰 Tech stack
Microsoft Agent Framework 1.0, Semantic Kernel concepts, Azure Cosmos DB, Azure Cache for Redis, FastAPI (SSE/StreamingResponse), Azure Content Safety.

---

## 🚀 Quick start

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) copy the env template — runs in MOCK mode without it
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

# 4. Run the API
uvicorn app.main:app --reload
```

Open the interactive docs at **http://127.0.0.1:8000/docs**.

### Try the endpoint
```bash
curl -X POST http://127.0.0.1:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"advisor_query": "Summarize the risk exposure of the Henderson portfolio this quarter."}'
```

### Run the tests
```bash
pytest -q
```

### Run with Docker
```bash
docker build -t agentic-ai-azure-week03-04-agent-framework .
docker run -p 8000:8000 agentic-ai-azure-week03-04-agent-framework
```

---

## 📁 Project structure
```
agentic-ai-azure-week03-04-agent-framework/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI app + the /api/v1/research endpoint
├── tests/
│   └── test_smoke.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 🗺️ Where this fits
This repo covers **Weeks 3–4 — Microsoft Agent Framework**. The full 12-week path and reference architecture
live in the master-class companion repo:
**[azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass)**.

## 📄 License
MIT — see [`LICENSE`](LICENSE).
