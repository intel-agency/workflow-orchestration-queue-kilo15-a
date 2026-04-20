"""Tests for the main FastAPI application entry point."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

from src.main import app


class TestMainApp:
    """Tests for the main FastAPI application."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "os-apow"
        assert "version" in data

    def test_readiness_check(self, client: TestClient) -> None:
        """Test readiness endpoint returns ready status."""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "os-apow"

    def test_app_metadata(self) -> None:
        """Test FastAPI app has correct metadata."""
        assert app.title == "OS-APOW - Workflow Orchestration Queue"
        assert app.version == "0.1.0"
