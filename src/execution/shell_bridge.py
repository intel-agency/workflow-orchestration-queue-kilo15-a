"""Shell Bridge for worker container management.

This module implements the Hands pillar's execution layer, providing
a clean interface for managing the opencode worker lifecycle via
shell scripts (devcontainer-opencode.sh).

The Shell Bridge follows ADR 07: Standardized Shell-Bridge Execution,
ensuring the agent runs in an environment identical to a local developer's.

Commands:
    up      - Provision the DevContainer environment
    start   - Launch the opencode server inside the container
    prompt  - Execute a workflow prompt via opencode
    stop    - Stop the container (keep for fast restart)
    down    - Remove the container entirely
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Default shell bridge script path
DEFAULT_BRIDGE_PATH = "./scripts/devcontainer-opencode.sh"

# Timeout defaults (seconds)
INFRA_TIMEOUT = 300  # 5 min for infrastructure commands
START_TIMEOUT = 120  # 2 min for server start
PROMPT_TIMEOUT = 5700  # 95 min for prompt execution (higher than inner watchdog)


@dataclass
class ShellResult:
    """Result from a shell bridge command execution.

    Attributes:
        args: The command and arguments that were executed.
        returncode: Process exit code (0 = success).
        stdout: Captured standard output.
        stderr: Captured standard error.
    """

    args: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def success(self) -> bool:
        """Check if the command completed successfully."""
        return self.returncode == 0


@dataclass
class BridgeConfig:
    """Configuration for the shell bridge.

    Attributes:
        bridge_path: Path to the devcontainer-opencode.sh script.
        infra_timeout: Timeout for infrastructure commands (up, down).
        start_timeout: Timeout for server start command.
        prompt_timeout: Timeout for prompt execution command.
    """

    bridge_path: str = DEFAULT_BRIDGE_PATH
    infra_timeout: int = INFRA_TIMEOUT
    start_timeout: int = START_TIMEOUT
    prompt_timeout: int = PROMPT_TIMEOUT


class ShellBridge:
    """Shell bridge for managing opencode worker lifecycle.

    Provides a clean Python interface for invoking the shell-bridge
    script that manages the DevContainer-based opencode worker.

    The bridge ensures:
    - Environment parity with local developer setup
    - Proper subprocess timeout handling
    - Structured result capture for logging and status reporting

    Usage:
        bridge = ShellBridge()
        result = await bridge.up()
        if result.success:
            result = await bridge.start()
            if result.success:
                result = await bridge.prompt("Execute workflow create-app-plan.md")
    """

    def __init__(self, config: BridgeConfig | None = None) -> None:
        """Initialize the shell bridge.

        Args:
            config: Optional bridge configuration. Uses defaults if not provided.
        """
        self.config = config or BridgeConfig()

    async def _execute(self, args: list[str], timeout: int | None = None) -> ShellResult:
        """Execute a shell command with timeout.

        Args:
            args: Command and arguments to execute.
            timeout: Maximum seconds to wait. None = no limit.

        Returns:
            ShellResult with exit code and captured output.
        """
        try:
            logger.info(f"Executing bridge command: {' '.join(args)}")
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except TimeoutError:
                logger.warning(f"Bridge command timed out after {timeout}s - killing process")
                process.kill()
                stdout, stderr = await process.communicate()
                return ShellResult(
                    args=args,
                    returncode=-1,
                    stdout=stdout.decode().strip() if stdout else "",
                    stderr=f"TIMEOUT after {timeout}s\n{stderr.decode().strip() if stderr else ''}",
                )

            return ShellResult(
                args=args,
                returncode=process.returncode or 0,
                stdout=stdout.decode().strip() if stdout else "",
                stderr=stderr.decode().strip() if stderr else "",
            )

        except Exception as e:
            logger.error(f"Critical bridge execution error: {e}")
            return ShellResult(
                args=args,
                returncode=-1,
                stderr=str(e),
            )

    async def up(self) -> ShellResult:
        """Provision the DevContainer environment.

        Returns:
            ShellResult with provision outcome.
        """
        return await self._execute(
            [self.config.bridge_path, "up"],
            timeout=self.config.infra_timeout,
        )

    async def start(self) -> ShellResult:
        """Launch the opencode server inside the container.

        Returns:
            ShellResult with start outcome.
        """
        return await self._execute(
            [self.config.bridge_path, "start"],
            timeout=self.config.start_timeout,
        )

    async def prompt(self, instruction: str) -> ShellResult:
        """Execute a workflow prompt via opencode.

        This is the primary work dispatch command. The instruction
        tells the opencode agent which workflow to execute and
        provides context (e.g., issue URL).

        Args:
            instruction: The prompt/instruction to send to the agent.

        Returns:
            ShellResult with execution outcome.
        """
        return await self._execute(
            [self.config.bridge_path, "prompt", instruction],
            timeout=self.config.prompt_timeout,
        )

    async def stop(self) -> ShellResult:
        """Stop the container (keep for fast restart).

        Returns:
            ShellResult with stop outcome.
        """
        return await self._execute(
            [self.config.bridge_path, "stop"],
            timeout=60,
        )

    async def down(self) -> ShellResult:
        """Remove the container entirely.

        Returns:
            ShellResult with teardown outcome.
        """
        return await self._execute(
            [self.config.bridge_path, "down"],
            timeout=self.config.infra_timeout,
        )
