"""Pytest fixtures and configuration for workflow-orchestration-queue tests.

Provides shared fixtures for FastAPI test clients, mock settings,
and other test utilities used across the test suite.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI test client.

    Returns:
        TestClient configured against the main app.
    """
    return TestClient(app)


@pytest.fixture
def mock_notifier_settings() -> dict[str, str]:
    """Provide mock notifier settings for testing.

    Returns:
        Dictionary of settings suitable for constructing NotifierSettings.
    """
    return {
        "webhook_secret": "test-webhook-secret-for-testing",
        "github_token": "ghp_test_token_1234567890",
        "github_repo": "test-org/test-repo",
        "debug": "true",
    }


@pytest.fixture
def mock_sentinel_settings() -> dict[str, str]:
    """Provide mock sentinel settings for testing.

    Returns:
        Dictionary of settings suitable for constructing SentinelSettings.
    """
    return {
        "github_token": "ghp_test_token_1234567890",
        "github_repo": "test-org/test-repo",
        "sentinel_bot_login": "test-sentinel-bot",
        "poll_interval_seconds": "10",
        "heartbeat_interval_seconds": "60",
    }


@pytest.fixture
def sample_issue_payload() -> dict:
    """Provide a sample GitHub issue webhook payload.

    Returns:
        Dictionary representing a GitHub issue opened event.
    """
    return {
        "action": "opened",
        "issue": {
            "number": 42,
            "title": "[Application Plan] Test Plan",
            "body": "This is a test issue body",
            "state": "open",
            "html_url": "https://github.com/test-org/test-repo/issues/42",
            "labels": [],
            "assignees": [],
            "user": {
                "login": "test-user",
                "id": 12345,
                "html_url": "https://github.com/test-user",
            },
        },
        "repository": {
            "id": 99999,
            "name": "test-repo",
            "full_name": "test-org/test-repo",
            "html_url": "https://github.com/test-org/test-repo",
        },
        "sender": {
            "login": "test-user",
            "id": 12345,
        },
    }
