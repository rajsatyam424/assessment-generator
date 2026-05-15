"""
Integration tests for the FastAPI endpoints.
Run with server running or pytest.

Run: pytest tests/ -v
"""

from fastapi.testclient import TestClient
from assessment_engine.api import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestGenerate:
    def test_rejects_empty_name(self):
        resp = client.post("/generate", json={"course_name": ""})
        assert resp.status_code == 422

    def test_rejects_missing_name(self):
        resp = client.post("/generate", json={})
        assert resp.status_code == 422
