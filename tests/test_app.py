"""Hermetic tests for the Weeks 3-4 research assistant (mock backend)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_mock():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["backend"] == "mock"


def test_research_grounded_with_disclaimer():
    r = client.post(
        "/api/v1/research",
        json={"advisor_query": "Summarize the portfolio", "client_id": "HENDERSON"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "MSFT" in body["answer"]
    assert body["disclaimer"] in body["answer"]
    assert "tool:get_holdings" in body["sources"]


def test_memory_accumulates_per_session():
    s = "sess-xyz"
    first = client.post("/api/v1/research", json={"advisor_query": "q1", "session_id": s}).json()
    second = client.post("/api/v1/research", json={"advisor_query": "q2", "session_id": s}).json()
    assert second["memory_turns"] == first["memory_turns"] + 1


def test_pii_is_redacted():
    r = client.post(
        "/api/v1/research",
        json={"advisor_query": "Email me at john.doe@example.com about MSFT"},
    )
    body = r.json()
    assert body["redacted_input"] is True
    assert "example.com" not in body["answer"]


def test_validation_rejects_empty():
    r = client.post("/api/v1/research", json={"advisor_query": ""})
    assert r.status_code == 422
