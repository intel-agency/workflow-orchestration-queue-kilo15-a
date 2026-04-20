"""Unified configuration management for workflow-orchestration-queue.

Provides Pydantic Settings classes for all components of the 4-pillar
architecture. Settings are loaded from environment variables with optional
.env file support.

Each component (Notifier, Sentinel) has its own settings class, but shared
configuration is consolidated here for consistency.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Base application settings shared across all components.

    Settings are loaded from environment variables and/or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application metadata
    app_name: str = Field(default="workflow-orchestration-queue", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")

    # GitHub configuration
    github_token: str = Field(default="", description="GitHub API token with repo scope")
    github_repo: str = Field(default="", description="Repository in owner/repo format")
    github_org: str = Field(default="", description="GitHub organization")

    def validate_required(self, fields: list[str]) -> None:
        """Validate that specified fields are not empty or placeholder values.

        Args:
            fields: List of field names to validate.

        Raises:
            ValueError: If any field is empty or contains a placeholder.
        """
        placeholders = ["your-", "placeholder", "changeme", "xxx"]
        for field_name in fields:
            value = getattr(self, field_name, "")
            if not value or any(p in value.lower() for p in placeholders):
                raise ValueError(
                    f"Required setting '{field_name}' is missing or contains a placeholder. "
                    f"Please set a valid value in environment or .env file."
                )


class NotifierSettings(AppSettings):
    """Configuration settings for the Notifier service (The Ear).

    Extends base settings with webhook-specific configuration.
    """

    webhook_secret: str = Field(default="", description="GitHub webhook secret for HMAC validation")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port", ge=1, le=65535)

    def validate_all(self) -> None:
        """Validate all required notifier settings."""
        self.validate_required(["github_token", "github_repo", "webhook_secret"])


class SentinelSettings(AppSettings):
    """Configuration settings for the Sentinel orchestrator (The Brain).

    Extends base settings with polling and execution configuration.
    """

    sentinel_bot_login: str = Field(default="", description="Sentinel bot's GitHub login")
    poll_interval_seconds: int = Field(default=60, description="Polling interval in seconds", ge=10, le=300)
    heartbeat_interval_seconds: int = Field(
        default=300, description="Heartbeat comment interval in seconds", ge=60, le=600
    )
    prompt_timeout_seconds: int = Field(default=5700, description="Prompt command timeout in seconds (95 min)", ge=300)
    infra_timeout_seconds: int = Field(default=300, description="Infrastructure command timeout in seconds", ge=30)
    max_retries: int = Field(default=3, description="Max retries for API calls", ge=0, le=10)
    max_backoff_seconds: int = Field(default=960, description="Max backoff on rate limits (16 min)")
    subprocess_timeout_seconds: int = Field(default=5700, description="Safety net timeout for subprocess calls")

    def validate_all(self) -> None:
        """Validate all required sentinel settings."""
        self.validate_required(["github_token", "github_repo"])


# Singleton settings instances
_notifier_settings: NotifierSettings | None = None
_sentinel_settings: SentinelSettings | None = None


def get_notifier_settings() -> NotifierSettings:
    """Get or create the Notifier settings instance.

    Returns:
        Cached NotifierSettings instance.

    Raises:
        ValueError: If required settings are missing or invalid.
    """
    global _notifier_settings
    if _notifier_settings is None:
        _notifier_settings = NotifierSettings()
        _notifier_settings.validate_all()
    return _notifier_settings


def get_sentinel_settings() -> SentinelSettings:
    """Get or create the Sentinel settings instance.

    Returns:
        Cached SentinelSettings instance.

    Raises:
        ValueError: If required settings are missing or invalid.
    """
    global _sentinel_settings
    if _sentinel_settings is None:
        _sentinel_settings = SentinelSettings()
        _sentinel_settings.validate_all()
    return _sentinel_settings


def reset_settings() -> None:
    """Reset cached settings instances.

    Useful for testing or when configuration changes at runtime.
    """
    global _notifier_settings, _sentinel_settings
    _notifier_settings = None
    _sentinel_settings = None
