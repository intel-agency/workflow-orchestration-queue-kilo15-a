"""Tests for GitHub queue implementation."""

import pytest

from src.queue.github_queue import GitHubQueue, TaskArtifact


class TestTaskArtifact:
    """Tests for TaskArtifact model."""

    def test_task_artifact_creation(self) -> None:
        """Test creating a TaskArtifact."""
        artifact = TaskArtifact(
            branch_name="feature/test",
            pr_url="https://github.com/owner/repo/pull/1",
            pr_number=1,
        )
        assert artifact.branch_name == "feature/test"
        assert artifact.pr_number == 1

    def test_task_artifact_optional_fields(self) -> None:
        """Test TaskArtifact with minimal fields."""
        artifact = TaskArtifact()
        assert artifact.branch_name is None
        assert artifact.pr_url is None
        assert artifact.additional_info == {}


class TestGitHubQueue:
    """Tests for GitHubQueue class."""

    @pytest.fixture
    def queue(self) -> GitHubQueue:
        """Create a GitHubQueue instance for testing."""
        return GitHubQueue(repo="owner/repo", token="test-token")

    def test_queue_initialization(self, queue: GitHubQueue) -> None:
        """Test queue initialization."""
        assert queue.repo == "owner/repo"
        assert queue.token == "test-token"
        assert queue.client is not None

    @pytest.mark.asyncio
    async def test_queue_close(self, queue: GitHubQueue) -> None:
        """Test queue close cleans up resources."""
        await queue.close()
        # Client should be closed after this

    @pytest.mark.asyncio
    async def test_fetch_queued_empty(self, queue: GitHubQueue) -> None:
        """Test fetch_queued returns empty list (placeholder)."""
        result = await queue.fetch_queued()
        assert result == []

    @pytest.mark.asyncio
    async def test_claim_task_placeholder(self, queue: GitHubQueue) -> None:
        """Test claim_task returns False (placeholder)."""
        result = await queue.claim_task(1, "sentinel-bot")
        assert result is False
