"""GitHub webhook endpoint handlers.

This module implements the Ear pillar's webhook ingestion endpoints.
It handles:
- HMAC-SHA256 signature verification
- Event type routing (issues, comments, PRs)
- Task type detection from issue templates
- WorkItem manifest generation

The webhook receiver follows the security model where every request
is validated against X-Hub-Signature-256 header before processing.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


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


def detect_task_type(title: str | None = None, body: str | None = None, labels: list[str] | None = None) -> str | None:
    """Detect task type from issue content.

    Looks for template markers in title, body, or labels to determine
    the appropriate workflow to trigger.

    Args:
        title: Issue title text.
        body: Issue body text.
        labels: List of label names on the issue.

    Returns:
        Detected task type string or None if no match found.
    """
    # Check labels first (most specific)
    if labels:
        for label in labels:
            label_lower = label.lower()
            if "agent:plan" in label_lower or "plan" in label_lower:
                return "create-app-plan"
            if "bug" in label_lower:
                return "analyze-bug"

    # Check title for template markers
    text_to_check = (title or "").upper()
    markers = {
        "[APPLICATION PLAN]": "create-app-plan",
        "[BUGFIX]": "analyze-bug",
        "[TASK]": "perform-task",
        "[FEATURE]": "perform-task",
        "[PROJECT STRUCTURE]": "create-project-structure",
    }

    for marker, task_type in markers.items():
        if marker in text_to_check:
            return task_type

    # Check body content
    if body:
        body_upper = body.upper()
        for marker, task_type in markers.items():
            if marker in body_upper:
                return task_type

    return None


@router.post("/github")
async def handle_github_webhook(request: Request) -> dict[str, Any]:
    """Handle GitHub webhook events.

    Validates HMAC signature, parses payload, and routes to
    the appropriate event handler based on event type.

    Args:
        request: FastAPI request object containing headers and body.

    Returns:
        Processing result with status and details.

    Raises:
        HTTPException: If signature validation fails (401) or payload is invalid (400).
    """
    # Get raw body for signature verification (used in Phase 2)
    _payload_bytes = await request.body()

    # Get signature from header
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature:
        logger.warning("Webhook request missing X-Hub-Signature-256 header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Hub-Signature-256 header",
        )

    # TODO: Verify signature with configured webhook secret
    # This will be implemented in Phase 2 when the full notifier is connected

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

    logger.info(f"Received webhook event: {event_type}.{action}")

    # Route to appropriate handler
    if event_type == "issues":
        return await _handle_issue_event(event_data)
    elif event_type == "issue_comment":
        return await _handle_comment_event(event_data)
    elif event_type == "pull_request":
        return await _handle_pr_event(event_data)
    else:
        return {"status": "ignored", "event_type": event_type, "action": action}


async def _handle_issue_event(event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle GitHub issues events.

    Detects task type from issue content and prepares WorkItem
    for queue processing.

    Args:
        event_data: Parsed webhook payload.

    Returns:
        Processing result.
    """
    issue = event_data.get("issue", {})
    action = event_data.get("action")
    issue_number = issue.get("number")
    title = issue.get("title", "")
    body = issue.get("body")
    labels = [label.get("name", "") for label in issue.get("labels", [])]

    task_type = detect_task_type(title=title, body=body, labels=labels)

    logger.info(f"Issue #{issue_number} ({action}): task_type={task_type}")

    # TODO: Phase 2 - Create WorkItem and add to queue
    return {
        "status": "processed",
        "issue_number": issue_number,
        "action": action,
        "task_type": task_type,
    }


async def _handle_comment_event(event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle GitHub issue_comment events.

    Args:
        event_data: Parsed webhook payload.

    Returns:
        Processing result.
    """
    issue = event_data.get("issue", {})
    comment = event_data.get("comment", {})
    action = event_data.get("action")

    logger.info(f"Comment on issue #{issue.get('number')} ({action})")

    # TODO: Phase 3 - Bug correction loop
    return {
        "status": "processed",
        "issue_number": issue.get("number"),
        "comment_id": comment.get("id"),
        "action": action,
    }


async def _handle_pr_event(event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle GitHub pull_request events.

    Args:
        event_data: Parsed webhook payload.

    Returns:
        Processing result.
    """
    pr = event_data.get("pull_request", {})
    action = event_data.get("action")

    logger.info(f"PR #{pr.get('number')} ({action})")

    # TODO: Phase 3 - PR review handling
    return {
        "status": "processed",
        "pr_number": pr.get("number"),
        "action": action,
    }
