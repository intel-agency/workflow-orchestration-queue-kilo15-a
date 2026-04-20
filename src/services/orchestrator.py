"""Sentinel Orchestrator Service.

This module implements the Brain pillar's core orchestration logic:
- Polling GitHub Issues for queued tasks
- Claiming tasks using assign-then-verify pattern
- Dispatching work to the opencode worker via shell-bridge
- Posting heartbeat comments during long-running tasks
- Managing graceful shutdown on SIGTERM/SIGINT

The orchestrator follows ADR 07: Standardized Shell-Bridge Execution,
interacting with the worker exclusively via shell scripts.
"""

from __future__ import annotations

import asyncio
import logging
import random
import signal
import sys
import uuid
from typing import TYPE_CHECKING

from src.config import SentinelSettings, get_sentinel_settings
from src.queue.github_queue import GitHubQueue

if TYPE_CHECKING:
    from src.models.work_item import WorkItem

logger = logging.getLogger(__name__)


class Sentinel:
    """Sentinel orchestrator for task discovery and dispatch.

    The Sentinel is the Brain of the 4-pillar architecture. It:
    - Polls for queued tasks on a configurable interval
    - Claims tasks using assign-then-verify distributed locking
    - Dispatches claimed tasks to the opencode worker
    - Posts heartbeat comments for visibility
    - Handles graceful shutdown

    Attributes:
        queue: GitHub queue instance for task operations.
        settings: Validated sentinel settings.
        sentinel_id: Unique identifier for this sentinel instance.
        current_backoff: Current backoff duration for rate limit handling.
    """

    def __init__(self, queue: GitHubQueue, settings: SentinelSettings) -> None:
        """Initialize the Sentinel.

        Args:
            queue: GitHub queue for task operations.
            settings: Validated sentinel configuration.
        """
        self.queue = queue
        self.settings = settings
        self.sentinel_id = f"sentinel-{uuid.uuid4().hex[:8]}"
        self.current_backoff = settings.poll_interval_seconds
        self._shutdown_requested = False

    def request_shutdown(self) -> None:
        """Signal the sentinel to shut down gracefully."""
        self._shutdown_requested = True
        logger.info(f"Sentinel {self.sentinel_id} received shutdown request")

    async def process_task(self, item: WorkItem) -> None:
        """Process a single claimed task.

        Manages the full lifecycle: initialize infrastructure, start
        worker, dispatch prompt, handle completion, and reset environment.

        Args:
            item: The work item to process.
        """
        logger.info(f"Processing task #{item.issue_number} ({item.task_type})")
        # TODO: Phase 1 - Full implementation
        # 1. Initialize infrastructure via shell-bridge
        # 2. Start opencode server
        # 3. Dispatch workflow prompt
        # 4. Monitor with heartbeat
        # 5. Handle exit code
        # 6. Update task status
        # 7. Reset environment

    async def run_forever(self) -> None:
        """Main polling loop for task discovery.

        Continuously polls GitHub for agent:queued tasks,
        claims them using assign-then-verify, and dispatches
        to the worker. Handles rate limits with jittered
        exponential backoff.
        """
        logger.info(
            f"Sentinel {self.sentinel_id} entering polling loop (interval: {self.settings.poll_interval_seconds}s)"
        )

        while not self._shutdown_requested:
            try:
                tasks = await self.queue.fetch_queued()
                if tasks:
                    logger.info(f"Found {len(tasks)} queued task(s)")
                    for task in tasks:
                        if self._shutdown_requested:
                            break
                        claimed = await self.queue.claim_task(task.issue_number, self.sentinel_id)
                        if claimed:
                            await self.process_task(task)
                            break

                # Reset backoff on successful poll
                self.current_backoff = self.settings.poll_interval_seconds

            except Exception as e:
                status_code = getattr(getattr(e, "response", None), "status_code", None)
                if status_code in (403, 429):
                    # Jittered exponential backoff on rate limits
                    jitter = random.uniform(0, self.current_backoff * 0.1)
                    wait = min(self.current_backoff + jitter, self.settings.max_backoff_seconds)
                    logger.warning(f"Rate limited ({status_code}) - backing off {wait:.0f}s")
                    self.current_backoff = min(self.current_backoff * 2, self.settings.max_backoff_seconds)
                    await asyncio.sleep(wait)
                    continue
                else:
                    logger.error(f"Polling cycle error: {e}")

            await asyncio.sleep(self.settings.poll_interval_seconds)

        logger.info(f"Sentinel {self.sentinel_id} exiting polling loop")

    async def close(self) -> None:
        """Clean up resources."""
        await self.queue.close()
        logger.info(f"Sentinel {self.sentinel_id} shut down.")


async def run_sentinel() -> None:
    """Create and run the Sentinel orchestrator.

    This is the main async entry point that initializes the queue,
    creates the Sentinel, and runs the polling loop.
    """
    settings = get_sentinel_settings()
    queue = GitHubQueue(repo=settings.github_repo, token=settings.github_token)
    sentinel = Sentinel(queue, settings)

    # Set up signal handlers
    def handle_signal(signum: int, frame: object) -> None:
        sentinel.request_shutdown()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        await sentinel.run_forever()
    finally:
        await sentinel.close()


def main() -> None:
    """Main entry point for the Sentinel orchestrator.

    Validates configuration, sets up signal handlers, and starts
    the polling loop.
    """
    try:
        asyncio.run(run_sentinel())
    except KeyboardInterrupt:
        logger.info("Sentinel shutting down gracefully.")
    except Exception as e:
        logger.error(f"Sentinel encountered fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
