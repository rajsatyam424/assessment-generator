"""
Integration tests for the FastAPI endpoints.
Requires the server to be running (or use TestClient).

Run: pytest tests/ -v
"""

import json
import pytest
from fastapi.testclient import TestClient

from assessment_engine.api import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "model" in data
        assert "provider" in data


class TestGenerate:
    def test_generate_rejects_empty_name(self):
        resp = client.post("/generate", json={"course_name": ""})
        assert resp.status_code == 422  # validation error

    def test_generate_rejects_missing_name(self):
        resp = client.post("/generate", json={})
        assert resp.status_code == 422

    def test_generate_rejects_long_name(self):
        resp = client.post("/generate", json={"course_name": "x" * 201})
        assert resp.status_code == 422

    def test_generate_without_api_key_gets_server_error(self):
        """If no API key is configured, the server should return 500."""
        import assessment_engine.config as cfg
        original_key = cfg.API_KEY
        try:
            cfg.API_KEY = ""
            resp = client.post("/generate", json={"course_name": "Test Course"})
            assert resp.status_code == 500
        finally:
            cfg.API_KEY = original_key


class TestDownload:
    def test_download_nonexistent_file(self):
        resp = client.get("/download/nonexistent.docx")
        assert resp.status_code == 404

    def test_download_with_path_traversal(self):
        resp = client.get("/download/../../../etc/passwd")
        assert resp.status_code == 404
