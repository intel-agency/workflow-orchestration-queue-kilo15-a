"""Tests for notifier service endpoints."""

import hashlib
import hmac
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.notifier_service import app, verify_webhook_signature


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_settings() -> dict:
    """Mock settings for testing."""
    return {
        "webhook_secret": "test-secret",
        "github_token": "test-token",
        "github_repo": "owner/repo",
    }


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "notifier"


class TestWebhookSignature:
    """Tests for webhook signature verification."""

    def test_verify_valid_signature(self) -> None:
        """Test valid signature verification."""
        secret = "test-secret"
        payload = b'{"test": "data"}'
        expected_sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        assert verify_webhook_signature(payload, expected_sig, secret) is True

    def test_verify_invalid_signature(self) -> None:
        """Test invalid signature is rejected."""
        payload = b'{"test": "data"}'
        invalid_sig = "sha256=invalid"

        assert verify_webhook_signature(payload, invalid_sig, "secret") is False

    def test_verify_missing_sha256_prefix(self) -> None:
        """Test signature without sha256 prefix is rejected."""
        payload = b'{"test": "data"}'

        assert verify_webhook_signature(payload, "invalid", "secret") is False

    def test_verify_empty_signature(self) -> None:
        """Test empty signature is rejected."""
        payload = b'{"test": "data"}'

        assert verify_webhook_signature(payload, "", "secret") is False


class TestWebhookEndpoint:
    """Tests for webhook endpoint."""

    @patch("src.notifier_service.get_settings")
    def test_webhook_invalid_signature(self, mock_get_settings, client: TestClient, mock_settings: dict) -> None:
        """Test webhook rejects invalid signature."""
        from src.notifier_service import NotifierSettings

        mock_settings_obj = NotifierSettings.model_construct(**mock_settings)
        mock_get_settings.return_value = mock_settings_obj

        response = client.post(
            "/webhooks/github",
            json={"test": "data"},
            headers={"X-Hub-Signature-256": "sha256=invalid"},
        )
        assert response.status_code == 401
