"""Sentinel Orchestrator - The Brain of the 4-Pillar Architecture.

This module implements the background polling and dispatch service that:
- Polls GitHub Issues for agent:queued tasks
- Claims tasks using assign-then-verify pattern
- Dispatches work to the opencode worker via shell-bridge
- Posts heartbeat comments during long-running tasks
- Handles graceful shutdown (SIGTERM/SIGINT)

The Sentinel follows ADR 07: Standardized Shell-Bridge Execution,
interacting with the agentic environment exclusively via
./scripts/devcontainer-opencode.sh
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import signal
import sys

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class SentinelSettings(BaseSettings):
    """Configuration settings for the Sentinel orchestrator.

    Settings are loaded from environment variables. Required settings
    will cause startup failure if missing or set to placeholder values.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required settings
    github_token: str = Field(..., description="GitHub API token with repo scope")
    github_repo: str = Field(..., description="Repository in owner/repo format")
    sentinel_bot_login: str = Field(..., description="Sentinel bot's GitHub login")

    # Optional settings with defaults
    poll_interval_seconds: int = Field(default=60, description="Polling interval in seconds", ge=10, le=300)
    heartbeat_interval_seconds: int = Field(
        default=300, description="Heartbeat comment interval in seconds", ge=60, le=600
    )
    prompt_timeout_seconds: int = Field(default=5700, description="Prompt command timeout (95 min)", ge=300)
    infra_timeout_seconds: int = Field(default=300, description="Infrastructure command timeout", ge=30)
    max_retries: int = Field(default=3, description="Max retries for API calls", ge=0, le=10)

    def validate_not_placeholder(self) -> None:
        """Validate that required settings are not placeholder values."""
        placeholders = ["your-", "placeholder", "changeme", "xxx"]
        for field_name in ["github_token", "github_repo", "sentinel_bot_login"]:
            value = getattr(self, field_name)
            if not value or any(p in value.lower() for p in placeholders):
                raise ValueError(
                    f"Required setting {field_name} is missing or contains placeholder. "
                    f"Please set a valid value in environment or .env file."
                )


# Global shutdown flag
_shutdown_event: asyncio.Event | None = None


def handle_shutdown(signum: int, frame: object) -> None:
    """Handle shutdown signals (SIGTERM, SIGINT).

    Sets the global shutdown event to trigger graceful termination.
    """
    global _shutdown_event
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    if _shutdown_event:
        _shutdown_event.set()


async def run_polling_loop(settings: SentinelSettings) -> None:
    """Main polling loop for task discovery.

    Continuously polls GitHub Issues for agent:queued tasks,
    claims them using assign-then-verify, and dispatches to worker.

    Args:
        settings: Validated Sentinel settings.
    """
    global _shutdown_event
    _shutdown_event = asyncio.Event()

    # NOTE: Phase 1 implementation will import and initialize GitHubQueue here

    logger.info(f"Starting Sentinel polling loop for {settings.github_repo}")
    logger.info(f"Poll interval: {settings.poll_interval_seconds}s")

    while not _shutdown_event.is_set():
        try:
            # TODO: Implement in Phase 1
            # 1. Fetch queued tasks
            # 2. For each task:
            #    a. Attempt claim
            #    b. If claimed, dispatch to worker
            #    c. Monitor and heartbeat
            #    d. Finish task
            logger.debug("Polling for queued tasks...")

            # Wait for next poll or shutdown
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(_shutdown_event.wait(), timeout=settings.poll_interval_seconds)

        except Exception as e:
            logger.error(f"Error in polling loop: {e}", exc_info=True)
            # Add jittered backoff on error
            await asyncio.sleep(settings.poll_interval_seconds * 1.5)

    logger.info("Shutdown complete, exiting polling loop")


async def dispatch_to_worker(issue_number: int, prompt: str, settings: SentinelSettings) -> int:
    """Dispatch work to opencode worker via shell-bridge.

    Follows ADR 07: Shell-Bridge Execution protocol:
    1. devcontainer-opencode.sh up
    2. devcontainer-opencode.sh start
    3. devcontainer-opencode.sh prompt "..."

    Args:
        issue_number: Issue number being processed.
        prompt: The prompt to send to the agent.
        settings: Sentinel settings.

    Returns:
        Exit code (0 = success, 1-10 = infra error, 11+ = logic error)
    """
    # TODO: Implement in Phase 1
    logger.info(f"Dispatching issue #{issue_number} to worker")
    return 0


def main() -> None:
    """Main entry point for the Sentinel orchestrator.

    Validates configuration, sets up signal handlers, and starts
    the polling loop.
    """
    # Setup signal handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    # Load and validate settings
    try:
        settings = SentinelSettings()
        settings.validate_not_placeholder()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    logger.info(f"Sentinel starting for repository: {settings.github_repo}")
    logger.info(f"Bot login: {settings.sentinel_bot_login}")

    # Run the async polling loop
    asyncio.run(run_polling_loop(settings))


if __name__ == "__main__":
    main()
