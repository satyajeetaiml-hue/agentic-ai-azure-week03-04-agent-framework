# Weeks 3–4 — Microsoft Agent Framework

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week03-04-agent-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week03-04-agent-framework/actions/workflows/ci.yml)

> ▶️ **Run in VS Code — no Azure needed.** `pip install -r requirements.txt`, then `uvicorn app.main:app --reload` and open http://127.0.0.1:8000/docs. Runs in **mock mode** by default — no `az login`, keys, or `.env` required. Wiring real Azure (below) is optional.

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
`az login`, then set `FOUNDRY_PROJECT_ENDPOINT` + `FOUNDRY_MODEL_NAME` in `.env`.

## 🧠 Wire durable memory (Azure Cosmos DB)

Session memory is pluggable: **in-memory** by default, **Cosmos DB** when a connection string is set
(`app/service.py` → `get_memory_store()`). Memory is partitioned by `sessionId`, so conversations survive
restarts and scale across instances.

### 1. Provision (Azure CLI)
```bash
az login
RG=rg-agentic-mem
az group create -n $RG -l eastus
az cosmosdb create -g $RG -n my-agent-cosmos --default-consistency-level Session
az cosmosdb keys list -g $RG -n my-agent-cosmos --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv   # copy this
```
The app **auto-creates** the database (`agentmemory`) and container (`sessions`, partition key
`/sessionId`) on first use — no manual schema step.

### 2. Configure `.env`
```
COSMOS_CONNECTION_STRING=<connection-string>
COSMOS_DATABASE=agentmemory
COSMOS_CONTAINER=sessions
```

### 3. Run — memory is now durable
```bash
uvicorn app.main:app --reload   # GET /health -> "memory": "cosmos"
```
```bash
# Same session_id across calls -> memory_turns keeps growing, even after a restart
curl -X POST http://127.0.0.1:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"advisor_query": "Summarize the Henderson portfolio", "session_id": "advisor-42"}'
```
Each turn is upserted as an item; `memory_turns` is a `SELECT VALUE COUNT(1)` scoped to the partition, and
recent context is a partition-scoped `ORDER BY c.ts DESC` query.

## 🏗️ Architect's lens
- Memory tiers: session (Redis) vs. durable (Cosmos) vs. semantic (AI Search) — cost & consistency.
- Partition strategy: `/sessionId` keeps each conversation's reads/writes single-partition (cheap & fast).
- Middleware as a **governance seam** — enforce policy without touching agent logic.

## 🧰 Tech stack
Microsoft Agent Framework concepts, **Azure Cosmos DB** (durable memory), Content Safety (filtering),
FastAPI, azure-ai-projects v2 (Responses API).

## 📁 Structure
```
app/service.py     # settings, schemas, memory stores (in-memory + Cosmos), middleware, tools, backends
app/main.py        # POST /api/v1/research
tests/test_app.py  # mock backend + middleware + memory increment
tests/test_memory.py  # Cosmos store logic (fake container; no live Cosmos needed)
```

## 🗺️ Series
Prev: [Week 2](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week02-foundry-claims) ·
Next: [Week 5 — MCP & Tools](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week05-mcp-tools) ·
[All labs](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure)

## 📄 License
MIT — see [`LICENSE`](LICENSE).

## 📊 Teaching slides

Download the **7-slide deck** for classroom use: [`agentic-ai-azure-week03-04-agent-framework.pptx`](slides/agentic-ai-azure-week03-04-agent-framework.pptx)

> Slides: Title · Learning goal · Enterprise use case · Architecture/flow · Key concepts · Run it · Architect's takeaways.

