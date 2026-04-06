"""GitHub webhook event models.

Pydantic models for parsing and validating GitHub webhook payloads.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class GitHubEventAction(StrEnum):
    """GitHub webhook event actions."""

    OPENED = "opened"
    EDITED = "edited"
    CLOSED = "closed"
    REOPENED = "reopened"
    LABELED = "labeled"
    UNLABELED = "unlabeled"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    CREATED = "created"
    DELETED = "deleted"
    SUBMITTED = "submitted"
    SYNCHRONIZE = "synchronize"


class GitHubUser(BaseModel):
    """GitHub user model."""

    login: str = Field(..., description="Username")
    id: int = Field(..., description="User ID")
    html_url: str = Field(..., description="Profile URL")
    type: str = Field(default="User", description="User type (User, Bot, Organization)")


class GitHubLabel(BaseModel):
    """GitHub label model."""

    name: str = Field(..., description="Label name")
    color: str = Field(..., description="Label color (hex)")
    description: str | None = Field(None, description="Label description")


class GitHubIssue(BaseModel):
    """GitHub issue model."""

    number: int = Field(..., description="Issue number")
    title: str = Field(..., description="Issue title")
    body: str | None = Field(None, description="Issue body")
    state: str = Field(..., description="Issue state (open, closed)")
    html_url: str = Field(..., description="Issue URL")
    labels: list[GitHubLabel] = Field(default_factory=list, description="Labels")
    assignees: list[GitHubUser] = Field(default_factory=list, description="Assignees")
    user: GitHubUser = Field(..., description="Issue author")


class GitHubRepository(BaseModel):
    """GitHub repository model."""

    id: int = Field(..., description="Repository ID")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full name (owner/repo)")
    html_url: str = Field(..., description="Repository URL")
    private: bool = Field(default=False, description="Is repository private")


class GitHubIssueEvent(BaseModel):
    """GitHub issues webhook event payload."""

    action: GitHubEventAction = Field(..., description="Event action")
    issue: GitHubIssue = Field(..., description="Issue that triggered the event")
    repository: GitHubRepository = Field(..., description="Repository")
    sender: GitHubUser = Field(..., description="User who triggered the event")
    label: GitHubLabel | None = Field(None, description="Label (for labeled/unlabeled)")


class GitHubComment(BaseModel):
    """GitHub comment model."""

    id: int = Field(..., description="Comment ID")
    body: str | None = Field(None, description="Comment body")
    html_url: str = Field(..., description="Comment URL")
    user: GitHubUser = Field(..., description="Comment author")


class GitHubIssueCommentEvent(BaseModel):
    """GitHub issue_comment webhook event payload."""

    action: GitHubEventAction = Field(..., description="Event action")
    issue: GitHubIssue = Field(..., description="Issue the comment belongs to")
    comment: GitHubComment = Field(..., description="Comment that triggered the event")
    repository: GitHubRepository = Field(..., description="Repository")
    sender: GitHubUser = Field(..., description="User who triggered the event")


class GitHubPullRequest(BaseModel):
    """GitHub pull request model."""

    number: int = Field(..., description="PR number")
    title: str = Field(..., description="PR title")
    body: str | None = Field(None, description="PR body")
    state: str = Field(..., description="PR state (open, closed)")
    html_url: str = Field(..., description="PR URL")
    draft: bool = Field(default=False, description="Is PR a draft")
    user: GitHubUser = Field(..., description="PR author")


class GitHubPullRequestEvent(BaseModel):
    """GitHub pull_request webhook event payload."""

    action: GitHubEventAction = Field(..., description="Event action")
    pull_request: GitHubPullRequest = Field(..., description="Pull request that triggered the event")
    repository: GitHubRepository = Field(..., description="Repository")
    sender: GitHubUser = Field(..., description="User who triggered the event")


class GitHubWebhookPayload(BaseModel):
    """Generic GitHub webhook payload wrapper.

    This model can be used to parse any GitHub webhook event.
    Use the event_type field to determine which specific model to use.
    """

    raw_payload: dict[str, Any] = Field(..., description="Raw event payload")

    def get_event_type(self) -> str | None:
        """Get the event type from the X-GitHub-Event header value.

        Note: The event type is typically passed via HTTP header,
        not in the payload itself.
        """
        return None  # Override in usage
