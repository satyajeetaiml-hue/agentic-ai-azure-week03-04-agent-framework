# Weeks 3–4 — Microsoft Agent Framework

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week03-04-agent-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week03-04-agent-framework/actions/workflows/ci.yml)

> **Standalone lab** from the *Agentic AI on Azure — Enterprise Master Class*.
> Course hub: [azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass).

---

## 🎯 Learning goal
Use Agent Framework concepts — **memory**, **middleware**, and **grounding tools** — behind a FastAPI service.

## 🏢 Enterprise use case — "Wealth Management Research Assistant" (Financial Services)
An advisor asks for a portfolio summary. The agent pulls **holdings** and **market data** (tools), keeps
**session memory**, redacts PII on the way in, and injects a compliance **disclaimer** on the way out.

## ✅ What this repo implements
- **Memory** — per-`session_id` conversation memory (in-memory mock; **Cosmos DB** in prod).
- **Middleware** — input **PII redaction** (email/SSN/phone) + output **disclaimer injection**.
- **Grounding tools** — `get_holdings` + `get_market_data`.
- **Mock backend** (offline, tested) and **Foundry backend** (azure-ai-projects v2 Responses API).

## 🚀 Quick start
```bash
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
```bash
curl -X POST http://127.0.0.1:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"advisor_query": "Summarize the Henderson portfolio", "session_id": "demo"}'
```
Run tests: `pytest -q`. Repeated calls with the same `session_id` grow `memory_turns`.

## ☁️ Foundry mode
`az login`, then set `FOUNDRY_PROJECT_ENDPOINT` + `FOUNDRY_MODEL_NAME` in `.env`. `COSMOS_CONNECTION_STRING`
is the seam for durable memory.

## 🏗️ Architect's lens
- Memory tiers: session (Redis) vs. durable (Cosmos) vs. semantic (AI Search).
- Middleware as a **governance seam** — enforce policy without touching agent logic.
- Declarative (YAML) vs. code-first agent definitions for versioning/CI-CD.

## 🧰 Tech stack
Microsoft Agent Framework concepts, Cosmos DB (memory), Content Safety (filtering), FastAPI,
azure-ai-projects v2 (Responses API).

## 📁 Structure
```
app/service.py   # settings, schemas, memory, middleware, tools, backends
app/main.py      # POST /api/v1/research
tests/test_app.py
```

## 🗺️ Series
Prev: [Week 2](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week02-foundry-claims) ·
Next: [Week 5 — MCP & Tools](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week05-mcp-tools) ·
[All labs](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure)

## 📄 License
MIT — see [`LICENSE`](LICENSE).
