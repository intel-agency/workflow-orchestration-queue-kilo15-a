"""GitHub-based task queue implementation.

This module provides the ITaskQueue abstract base class and GitHubQueue
implementation for interacting with GitHub Issues as a task queue.

The implementation follows ADR 09: Provider-Agnostic Interface Layer,
allowing future swapping to Linear, Notion, or SQL queues.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import httpx
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.models.work_item import WorkItem, WorkItemStatus


class TaskArtifact(BaseModel):
    """Artifacts produced by task completion."""

    branch_name: str | None = Field(None, description="Git branch created")
    pr_url: str | None = Field(None, description="Pull request URL")
    pr_number: int | None = Field(None, description="Pull request number")
    commit_sha: str | None = Field(None, description="Commit SHA")
    additional_info: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ITaskQueue(ABC):
    """Abstract base class for task queue implementations.

    This interface abstracts queue operations to allow provider-agnostic
    task processing. Implementations can target GitHub, Linear, Jira, etc.
    """

    @abstractmethod
    async def fetch_queued(self) -> list[WorkItem]:
        """Fetch all queued tasks from the queue.

        Returns:
            List of WorkItem objects with QUEUED status.
        """
        ...

    @abstractmethod
    async def claim_task(self, issue_number: int, sentinel_id: str) -> bool:
        """Attempt to claim a task using assign-then-verify pattern.

        This implements a distributed lock using GitHub assignees
        to prevent race conditions between multiple sentinel instances.

        Args:
            issue_number: The issue number to claim.
            sentinel_id: The sentinel bot's GitHub login.

        Returns:
            True if claim was successful, False otherwise.
        """
        ...

    @abstractmethod
    async def update_progress(self, issue_number: int, log_line: str, heartbeat: bool = False) -> None:
        """Update task progress by posting a comment.

        Args:
            issue_number: The issue number to update.
            log_line: The log line or status message to post.
            heartbeat: If True, mark as heartbeat comment.
        """
        ...

    @abstractmethod
    async def finish_task(
        self,
        issue_number: int,
        status: WorkItemStatus,
        artifacts: TaskArtifact | None = None,
        error_message: str | None = None,
    ) -> None:
        """Mark task as finished with final status.

        Args:
            issue_number: The issue number to finish.
            status: Final status (SUCCESS, ERROR, INFRA_FAILURE, etc.).
            artifacts: Optional artifacts produced by the task.
            error_message: Optional error message for failed tasks.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the queue connection and cleanup resources.

        Should be called during graceful shutdown.
        """
        ...


class GitHubQueue(ITaskQueue):
    """GitHub Issues-based task queue implementation.

    Uses GitHub Issues as the task queue, with labels for state management
    and comments for progress tracking. This implements the "Markdown as a
    Database" philosophy.

    Attributes:
        repo: Repository in owner/repo format.
        token: GitHub API token with repo scope.
        client: Shared httpx AsyncClient for connection pooling.
    """

    GITHUB_API_BASE = "https://api.github.com"

    def __init__(self, repo: str, token: str) -> None:
        """Initialize GitHub queue.

        Args:
            repo: Repository in owner/repo format.
            token: GitHub API token with repo scope.
        """
        self.repo = repo
        self.token = token
        self.client = httpx.AsyncClient(
            base_url=self.GITHUB_API_BASE,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=httpx.Timeout(30.0),
        )

    async def fetch_queued(self) -> list[WorkItem]:
        """Fetch all issues with agent:queued label.

        Returns:
            List of WorkItem objects ready for processing.
        """
        # TODO: Implement in Phase 1
        return []

    async def claim_task(self, issue_number: int, sentinel_id: str) -> bool:
        """Claim task using assign-then-verify pattern.

        Implements concurrency control via GitHub assignees:
        1. Attempt to assign sentinel to issue
        2. Re-fetch the issue
        3. Verify assignment before proceeding
        4. If verification fails, skip gracefully

        Args:
            issue_number: Issue to claim (unused in scaffold).
            sentinel_id: Sentinel bot's GitHub login (unused in scaffold).

        Returns:
            True if claim successful, False if already claimed.
        """
        # Phase 1: Implement assign-then-verify pattern
        _ = issue_number, sentinel_id  # Scaffolding: will be used in Phase 1
        return False

    async def update_progress(self, issue_number: int, log_line: str, heartbeat: bool = False) -> None:
        """Post progress comment to issue.

        Heartbeat comments are posted every 5 minutes during
        long-running tasks to provide visibility.

        Args:
            issue_number: Issue to update.
            log_line: Progress message.
            heartbeat: Whether this is a heartbeat comment.
        """
        # TODO: Implement in Phase 1
        pass

    async def finish_task(
        self,
        issue_number: int,
        status: WorkItemStatus,
        artifacts: TaskArtifact | None = None,
        error_message: str | None = None,
    ) -> None:
        """Update labels and post completion comment.

        Args:
            issue_number: Issue to finish.
            status: Final status.
            artifacts: Optional task artifacts.
            error_message: Optional error details.
        """
        # TODO: Implement in Phase 1
        pass

    async def close(self) -> None:
        """Close HTTP client connection pool."""
        await self.client.aclose()
