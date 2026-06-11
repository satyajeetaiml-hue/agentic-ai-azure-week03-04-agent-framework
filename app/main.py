"""Weeks 3-4 — Microsoft Agent Framework.

Wealth Management Research Assistant with memory + middleware + grounding tools.
Runs in MOCK mode out of the box. Run:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.service import ResearchRequest, ResearchResponse, get_backend, get_settings

settings = get_settings()
app = FastAPI(title="Weeks 3-4 — Agent Framework (Wealth Research)", version="0.2.0")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "week": "3-4", "backend": "foundry" if settings.use_foundry else "mock"}


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "service": "agentic-ai-azure-week03-04-agent-framework",
        "endpoint": "/api/v1/research",
        "backend": "foundry" if settings.use_foundry else "mock",
        "docs": "/docs",
    }


@app.post("/api/v1/research", response_model=ResearchResponse, tags=["week03-04"])
def research(payload: ResearchRequest) -> ResearchResponse:
    return get_backend().research(payload)
