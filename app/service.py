"""Weeks 3-4 — Agent Framework: Wealth Management Research Assistant.

Demonstrates the Agent Framework concepts on top of a runnable service:

* **Memory** — per-session conversation memory (in-memory mock; Cosmos DB in prod).
* **Middleware** — input PII redaction + output compliance-disclaimer injection.
* **Grounding tools** — holdings + market-data lookups the agent uses as context.

Two backends: deterministic ``MockResearchBackend`` (offline, tested) and
``FoundryResearchBackend`` (azure-ai-projects v2 Responses API, lazy-imported).
"""

from __future__ import annotations

import re
from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── settings ────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    foundry_project_endpoint: str = ""
    foundry_model_name: str = "gpt-4o"
    cosmos_connection_string: str = ""  # set to enable durable Cosmos DB memory
    cosmos_database: str = "agentmemory"
    cosmos_container: str = "sessions"

    @property
    def use_foundry(self) -> bool:
        return bool(self.foundry_project_endpoint)

    @property
    def use_cosmos(self) -> bool:
        return bool(self.cosmos_connection_string)


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ── schemas ─────────────────────────────────────────────────────────────
class ResearchRequest(BaseModel):
    advisor_query: str = Field(..., min_length=1, description="The advisor's natural-language request.")
    client_id: str = Field(default="HENDERSON", description="Portfolio/client identifier.")
    session_id: str = Field(default="default", description="Conversation session for memory.")


class ResearchResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str
    memory_turns: int
    disclaimer: str
    redacted_input: bool
    mode: str


# ── grounding tools (mock data sources) ─────────────────────────────────
_HOLDINGS = {
    "HENDERSON": [
        {"symbol": "MSFT", "shares": 1200, "weight": 0.34},
        {"symbol": "AAPL", "shares": 800, "weight": 0.21},
        {"symbol": "VTI", "shares": 500, "weight": 0.45},
    ]
}
_MARKET = {"MSFT": 432.1, "AAPL": 214.5, "VTI": 268.9, "trend": "moderately bullish"}


def get_holdings(client_id: str) -> list[dict]:
    return _HOLDINGS.get(client_id.upper(), [])


def get_market_data() -> dict:
    return _MARKET


# ── middleware ──────────────────────────────────────────────────────────
_PII_PATTERNS = [
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),          # email
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),               # SSN-like
    re.compile(r"\b(?:\+?\d[\d -]{8,}\d)\b"),           # phone
]
DISCLAIMER = (
    "This is general information, not personalized financial advice. "
    "Past performance does not guarantee future results."
)


def redact_pii(text: str) -> tuple[str, bool]:
    redacted = text
    for pat in _PII_PATTERNS:
        redacted = pat.sub("[REDACTED]", redacted)
    return redacted, redacted != text


# ── session memory: in-memory (mock) or durable Cosmos DB ───────────────
class InMemoryStore:
    """Process-local memory — fine for dev/tests, lost on restart."""

    backend = "in-memory"

    def __init__(self) -> None:
        self._data: dict[str, list[dict]] = {}

    def append(self, session_id: str, query: str, answer: str) -> int:
        turns = self._data.setdefault(session_id, [])
        turns.append({"query": query, "answer": answer})
        return len(turns)

    def recent(self, session_id: str, n: int = 2) -> list[dict]:
        return self._data.get(session_id, [])[-n:]


class CosmosMemoryStore:
    """Durable memory in Azure Cosmos DB, partitioned by ``sessionId``.

    Lazy-imports the SDK and creates the database/container on first use.
    """

    backend = "cosmos"

    def __init__(self) -> None:
        from azure.cosmos import CosmosClient, PartitionKey

        s = get_settings()
        client = CosmosClient.from_connection_string(s.cosmos_connection_string)
        db = client.create_database_if_not_exists(id=s.cosmos_database)
        self._container = db.create_container_if_not_exists(
            id=s.cosmos_container, partition_key=PartitionKey(path="/sessionId")
        )

    def append(self, session_id: str, query: str, answer: str) -> int:
        import time
        import uuid

        self._container.upsert_item(
            {
                "id": uuid.uuid4().hex,
                "sessionId": session_id,
                "query": query,
                "answer": answer,
                "ts": time.time_ns(),  # high-resolution, strictly increasing per call
            }
        )
        rows = list(
            self._container.query_items(
                query="SELECT VALUE COUNT(1) FROM c WHERE c.sessionId = @s",
                parameters=[{"name": "@s", "value": session_id}],
                partition_key=session_id,
            )
        )
        return rows[0] if rows else 0

    def recent(self, session_id: str, n: int = 2) -> list[dict]:
        items = list(
            self._container.query_items(
                query="SELECT * FROM c WHERE c.sessionId = @s ORDER BY c.ts DESC",
                parameters=[{"name": "@s", "value": session_id}],
                partition_key=session_id,
            )
        )
        return list(reversed(items[:n]))


@lru_cache
def get_memory_store():
    return CosmosMemoryStore() if get_settings().use_cosmos else InMemoryStore()


def _recent_context(session_id: str) -> str:
    turns = get_memory_store().recent(session_id, n=2)
    if not turns:
        return ""
    return " | ".join(f"Q:{t['query']}" for t in turns)


SYSTEM_INSTRUCTIONS = (
    "You are a wealth-management research assistant for financial advisors. Use the provided "
    "holdings and market data to answer concisely and professionally. Do not invent figures."
)


# ── backends ────────────────────────────────────────────────────────────
class MockResearchBackend:
    mode = "mock"

    def research(self, req: ResearchRequest) -> ResearchResponse:
        clean_query, redacted = redact_pii(req.advisor_query)
        holdings = get_holdings(req.client_id)
        market = get_market_data()

        if holdings:
            lines = [f"{h['symbol']} {h['shares']} sh @ ${market.get(h['symbol'], 0)}" for h in holdings]
            body = (
                f"Portfolio '{req.client_id}' holds: {', '.join(lines)}. "
                f"Market is {market['trend']}. Regarding '{clean_query.strip()}': the allocation looks "
                f"diversified across equities and a broad-market ETF."
            )
        else:
            body = f"No holdings found for client '{req.client_id}'."

        answer = f"{body}\n\n{DISCLAIMER}"
        turns = get_memory_store().append(req.session_id, clean_query, body)
        return ResearchResponse(
            answer=answer,
            sources=["tool:get_holdings", "tool:get_market_data"],
            session_id=req.session_id,
            memory_turns=turns,
            disclaimer=DISCLAIMER,
            redacted_input=redacted,
            mode=self.mode,
        )


class FoundryResearchBackend:
    mode = "foundry"

    def research(self, req: ResearchRequest) -> ResearchResponse:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        clean_query, redacted = redact_pii(req.advisor_query)
        holdings = get_holdings(req.client_id)
        market = get_market_data()
        context = (
            f"Holdings({req.client_id})={holdings}\nMarket={market}\n"
            f"RecentContext={_recent_context(req.session_id)}"
        )

        s = get_settings()
        with (
            DefaultAzureCredential() as cred,
            AIProjectClient(endpoint=s.foundry_project_endpoint, credential=cred) as proj,
        ):
            client = proj.get_openai_client()
            resp = client.responses.create(
                model=s.foundry_model_name,
                input=[
                    {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                    {"role": "user", "content": f"{context}\n\nAdvisor asks: {clean_query}"},
                ],
            )
            body = resp.output_text or "No response."

        answer = f"{body}\n\n{DISCLAIMER}"  # middleware: disclaimer injection
        turns = get_memory_store().append(req.session_id, clean_query, body)
        return ResearchResponse(
            answer=answer,
            sources=["tool:get_holdings", "tool:get_market_data", "foundry:responses"],
            session_id=req.session_id,
            memory_turns=turns,
            disclaimer=DISCLAIMER,
            redacted_input=redacted,
            mode=self.mode,
        )


def get_backend():
    return FoundryResearchBackend() if get_settings().use_foundry else MockResearchBackend()
