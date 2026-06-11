"""Smoke tests for Weeks 3–4 — Microsoft Agent Framework."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_endpoint_accepts_input():
    r = client.post("/api/v1/research", json={"advisor_query": "Summarize the risk exposure of the Henderson portfolio this quarter."})
    assert r.status_code == 200


def test_endpoint_rejects_empty():
    r = client.post("/api/v1/research", json={"advisor_query": ""})
    assert r.status_code == 422
