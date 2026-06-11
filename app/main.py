"""Weeks 3–4 — Microsoft Agent Framework — starter FastAPI service.

Use case: Wealth Management Research Assistant (Financial Services).
See README.md for the full lab brief. Run:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Weeks 3–4 — Microsoft Agent Framework", version="0.1.0")


class LabRequest(BaseModel):
    advisor_query: str = Field(..., min_length=1, description="The advisor's natural-language request.")


@app.get("/health")
def health():
    return {"status": "ok", "week": "3-4", "use_case": "Wealth Management Research Assistant"}


@app.get("/")
def root():
    return {
        "service": "agentic-ai-azure-week03-04-agent-framework",
        "week": "3-4",
        "endpoint": "/api/v1/research",
        "docs": "/docs",
    }


@app.post("/api/v1/research")
def handler(payload: LabRequest):
    """Mock handler for the Wealth Management Research Assistant.

    TODO (lab): replace this stub with the real implementation described in
    README.md (the Azure services for this week are listed in the Tech Stack).
    """
    return {
        "week": "3-4",
        "use_case": "Wealth Management Research Assistant",
        "received": payload.advisor_query,
        "status": "accepted",
        "note": "Mock response — implement the real agent per README.md.",
    }
