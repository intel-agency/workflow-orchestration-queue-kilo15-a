"""Unified data model for workflow orchestration queue.

This module defines the core data structures used across all components
of the 4-pillar architecture.
"""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, Field


class TaskType(StrEnum):
    """Enumeration of supported task types.

    Each task type corresponds to a different workflow template
    that the agent can execute.
    """

    CREATE_APP_PLAN = "create-app-plan"
    PERFORM_TASK = "perform-task"
    ANALYZE_BUG = "analyze-bug"
    CREATE_PROJECT_STRUCTURE = "create-project-structure"
    UNKNOWN = "unknown"


class WorkItemStatus(StrEnum):
    """Work item status corresponding to label states.

    These statuses map directly to GitHub labels:
    - agent:queued -> QUEUED
    - agent:in-progress -> IN_PROGRESS
    - agent:success -> SUCCESS
    - agent:error -> ERROR
    - agent:infra-failure -> INFRA_FAILURE
    - agent:stalled-budget -> STALLED_BUDGET
    """

    QUEUED = "agent:queued"
    IN_PROGRESS = "agent:in-progress"
    RECONCILING = "agent:reconciling"
    SUCCESS = "agent:success"
    ERROR = "agent:error"
    INFRA_FAILURE = "agent:infra-failure"
    STALLED_BUDGET = "agent:stalled-budget"


class WorkItem(BaseModel):
    """Unified work item representation.

    This model encapsulates all information needed by the Sentinel
    orchestrator to process a task from the queue.
    """

    issue_number: int = Field(..., description="GitHub issue number", ge=1)
    title: str = Field(..., description="Issue title", min_length=1)
    body: str | None = Field(None, description="Issue body content")
    repository: str = Field(..., description="Repository in owner/repo format")
    task_type: TaskType = Field(default=TaskType.UNKNOWN, description="Detected task type")
    status: WorkItemStatus = Field(default=WorkItemStatus.QUEUED, description="Current status")
    labels: list[str] = Field(default_factory=list, description="Current labels")
    assignees: list[str] = Field(default_factory=list, description="Current assignees")
    html_url: str = Field(..., description="GitHub issue URL")

    model_config = {"frozen": False, "extra": "forbid"}


# Secret patterns to scrub from output before posting to GitHub
SECRET_PATTERNS = [
    # GitHub Personal Access Tokens
    r"ghp_[a-zA-Z0-9]{36}",
    r"ghs_[a-zA-Z0-9]{36}",
    r"gho_[a-zA-Z0-9]{36}",
    r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}",
    # Bearer tokens
    r"Bearer\s+[a-zA-Z0-9\-._~+/]+=*",
    # API keys
    r"sk-[a-zA-Z0-9]{48,}",
    r"sk_live_[a-zA-Z0-9]{24,}",
    r"sk_test_[a-zA-Z0-9]{24,}",
    # ZhipuAI keys
    r"[a-f0-9]{32}\.[a-zA-Z0-9]{32}",
    # Generic secrets (key=value patterns)
    r"(?i)(api_key|secret|token|password|credential)\s*[=:]\s*['\"]?[^\s'\"]{8,}['\"]?",
]


def scrub_secrets(text: str) -> str:
    """Scrub sensitive secrets from text.

    Replaces known secret patterns with [REDACTED] before posting
    to GitHub to prevent credential leakage.

    Args:
        text: The text to scrub.

    Returns:
        The text with secrets replaced by [REDACTED].
    """
    result = text
    for pattern in SECRET_PATTERNS:
        result = re.sub(pattern, "[REDACTED]", result)
    return result
