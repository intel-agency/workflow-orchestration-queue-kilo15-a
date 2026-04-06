"""Work Event Notifier Service - The Ear of the 4-Pillar Architecture.

This module implements the FastAPI webhook receiver that:
- Receives GitHub webhook events
- Validates HMAC-SHA256 signatures for security
- Parses and triages events (issues, comments, PRs)
- Applies appropriate labels to trigger workflows
- Generates WorkItem manifests for machine-readable state

The Notifier follows the security model where every request
is validated against X-Hub-Signature-256 header before processing.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class NotifierSettings(BaseSettings):
    """Configuration settings for the Notifier service.

    Settings are loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required settings
    webhook_secret: str = Field(..., description="GitHub webhook secret for HMAC validation")
    github_token: str = Field(..., description="GitHub API token for label operations")
    github_repo: str = Field(..., description="Repository in owner/repo format")

    # Optional settings with defaults
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port", ge=1, le=65535)
    debug: bool = Field(default=False, description="Enable debug mode")

    def validate_not_placeholder(self) -> None:
        """Validate that required settings are not placeholder values."""
        placeholders = ["your-", "placeholder", "changeme", "xxx"]
        for field_name in ["webhook_secret", "github_token", "github_repo"]:
            value = getattr(self, field_name)
            if not value or any(p in value.lower() for p in placeholders):
                raise ValueError(
                    f"Required setting {field_name} is missing or contains placeholder. "
                    f"Please set a valid value in environment or .env file."
                )


# Global settings instance
_settings: NotifierSettings | None = None


def get_settings() -> NotifierSettings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = NotifierSettings()
        _settings.validate_not_placeholder()
    return _settings


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature.

    Args:
        payload: Raw request body bytes.
        signature: Value of X-Hub-Signature-256 header (sha256=<hex>).
        secret: Webhook secret configured in GitHub.

    Returns:
        True if signature is valid, False otherwise.
    """
    if not signature.startswith("sha256="):
        return False

    expected_sig = signature[7:]  # Remove 'sha256=' prefix
    computed_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected_sig, computed_sig)


def detect_task_type(body: str | None) -> str | None:
    """Detect task type from issue body content.

    Looks for template markers like [Application Plan], [Bugfix], etc.

    Args:
        body: Issue body text.

    Returns:
        Detected task type or None.
    """
    if not body:
        return None

    body_upper = body.upper()
    markers = {
        "[APPLICATION PLAN]": "create-app-plan",
        "[BUGFIX]": "analyze-bug",
        "[TASK]": "perform-task",
        "[FEATURE]": "perform-task",
        "[PROJECT STRUCTURE]": "create-project-structure",
    }

    for marker, task_type in markers.items():
        if marker in body_upper:
            return task_type

    return None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager.

    Handles startup and shutdown events.
    """
    logger.info("Notifier service starting up...")
    try:
        settings = get_settings()
        logger.info(f"Repository: {settings.github_repo}")
        logger.info(f"Listening on {settings.host}:{settings.port}")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

    yield

    logger.info("Notifier service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Workflow Orchestration Queue - Notifier",
    description="Headless agentic orchestration webhook receiver",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestration.

    Returns:
        Simple health status.
    """
    return {"status": "healthy", "service": "notifier"}


@app.get("/ready", response_model=None)
async def readiness_check() -> dict[str, str] | JSONResponse:
    """Readiness check endpoint.

    Verifies that all required configuration is available.

    Returns:
        Readiness status.
    """
    try:
        get_settings()
        return {"status": "ready", "service": "notifier"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "error": str(e)},
        )


@app.post("/webhooks/github")
async def handle_github_webhook(request: Request) -> dict[str, Any]:
    """Handle GitHub webhook events.

    Validates signature, parses payload, and routes to appropriate handler.

    Args:
        request: FastAPI request object.

    Returns:
        Processing result.

    Raises:
        HTTPException: If signature validation fails.
    """
    settings = get_settings()

    # Get raw body for signature verification
    payload = await request.body()

    # Verify HMAC signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_webhook_signature(payload, signature, settings.webhook_secret):
        logger.warning("Invalid webhook signature rejected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # Parse JSON payload
    try:
        event_data = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    # Get event type from header
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    action = event_data.get("action", "unknown")

    logger.info(f"Received {event_type}.{action} event")

    # Route to appropriate handler
    # TODO: Implement full event handling in Phase 2
    if event_type == "issues":
        return await handle_issue_event(event_data)
    elif event_type == "issue_comment":
        return await handle_comment_event(event_data)
    elif event_type == "pull_request":
        return await handle_pr_event(event_data)
    else:
        return {"status": "ignored", "event_type": event_type}


async def handle_issue_event(event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle GitHub issues events.

    Args:
        event_data: Parsed webhook payload.

    Returns:
        Processing result.
    """
    # TODO: Implement in Phase 2
    # - Parse issue body for template markers
    # - Apply agent:queued label if matches
    # - Generate WorkItem manifest
    issue = event_data.get("issue", {})
    issue_number = issue.get("number")
    action = event_data.get("action")

    logger.info(f"Issue #{issue_number} - action: {action}")

    return {
        "status": "processed",
        "issue_number": issue_number,
        "action": action,
    }


async def handle_comment_event(event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle GitHub issue_comment events.

    Args:
        event_data: Parsed webhook payload.

    Returns:
        Processing result.
    """
    # TODO: Implement in Phase 3 (bug correction loop)
    issue = event_data.get("issue", {})
    issue_number = issue.get("number")
    action = event_data.get("action")

    return {
        "status": "processed",
        "issue_number": issue_number,
        "action": action,
    }


async def handle_pr_event(event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle GitHub pull_request events.

    Args:
        event_data: Parsed webhook payload.

    Returns:
        Processing result.
    """
    # TODO: Implement in Phase 3 (PR review handling)
    pr = event_data.get("pull_request", {})
    pr_number = pr.get("number")
    action = event_data.get("action")

    return {
        "status": "processed",
        "pr_number": pr_number,
        "action": action,
    }


def main() -> None:
    """Main entry point for the Notifier service.

    Loads configuration and starts the FastAPI server.
    """
    import uvicorn

    try:
        settings = get_settings()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    uvicorn.run(
        "src.notifier_service:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
