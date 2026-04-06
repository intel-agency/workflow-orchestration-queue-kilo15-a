"""Tests for WorkItem model and scrub_secrets utility."""


from src.models.work_item import (
    TaskType,
    WorkItem,
    WorkItemStatus,
    scrub_secrets,
)


class TestWorkItem:
    """Tests for WorkItem model."""

    def test_work_item_creation(self) -> None:
        """Test creating a valid WorkItem."""
        item = WorkItem(
            issue_number=42,
            title="Test Issue",
            repository="owner/repo",
            html_url="https://github.com/owner/repo/issues/42",
        )
        assert item.issue_number == 42
        assert item.title == "Test Issue"
        assert item.task_type == TaskType.UNKNOWN
        assert item.status == WorkItemStatus.QUEUED

    def test_work_item_with_body(self) -> None:
        """Test WorkItem with body content."""
        item = WorkItem(
            issue_number=1,
            title="Test",
            body="This is the body",
            repository="owner/repo",
            html_url="https://github.com/owner/repo/issues/1",
        )
        assert item.body == "This is the body"

    def test_work_item_labels(self) -> None:
        """Test WorkItem with labels."""
        item = WorkItem(
            issue_number=1,
            title="Test",
            repository="owner/repo",
            labels=["bug", "enhancement"],
            html_url="https://github.com/owner/repo/issues/1",
        )
        assert "bug" in item.labels
        assert "enhancement" in item.labels


class TestTaskType:
    """Tests for TaskType enum."""

    def test_task_types_exist(self) -> None:
        """Test that expected task types exist."""
        assert TaskType.CREATE_APP_PLAN == "create-app-plan"
        assert TaskType.PERFORM_TASK == "perform-task"
        assert TaskType.ANALYZE_BUG == "analyze-bug"
        assert TaskType.UNKNOWN == "unknown"


class TestWorkItemStatus:
    """Tests for WorkItemStatus enum."""

    def test_status_values(self) -> None:
        """Test that status values match GitHub labels."""
        assert WorkItemStatus.QUEUED.value == "agent:queued"
        assert WorkItemStatus.IN_PROGRESS.value == "agent:in-progress"
        assert WorkItemStatus.SUCCESS.value == "agent:success"
        assert WorkItemStatus.ERROR.value == "agent:error"


class TestScrubSecrets:
    """Tests for scrub_secrets utility."""

    def test_scrub_github_pat(self) -> None:
        """Test scrubbing GitHub PAT tokens."""
        text = "Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz123456"
        result = scrub_secrets(text)
        assert "ghp_" not in result
        assert "[REDACTED]" in result

    def test_scrub_bearer_token(self) -> None:
        """Test scrubbing Bearer tokens."""
        text = "Authorization: Bearer abc123xyz789"
        result = scrub_secrets(text)
        assert "Bearer abc123xyz789" not in result
        assert "[REDACTED]" in result

    def test_scrub_api_key(self) -> None:
        """Test scrubbing API keys."""
        text = "api_key: sk-1234567890abcdefghijklmnopqrstuvwxyz123456789012"
        result = scrub_secrets(text)
        assert "sk-" not in result
        assert "[REDACTED]" in result

    def test_scrub_preserves_normal_text(self) -> None:
        """Test that normal text is preserved."""
        text = "This is a normal log message without secrets"
        result = scrub_secrets(text)
        assert result == text

    def test_scrub_empty_string(self) -> None:
        """Test scrubbing empty string."""
        assert scrub_secrets("") == ""

    def test_scrub_no_secrets(self) -> None:
        """Test text with no secrets remains unchanged."""
        text = "User logged in successfully"
        result = scrub_secrets(text)
        assert result == text
