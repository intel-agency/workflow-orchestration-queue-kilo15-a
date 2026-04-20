"""FastAPI application entry point for workflow-orchestration-queue.

This module provides the main FastAPI application that serves as the unified
entry point for the OS-APOW system. It aggregates routes from the api/ sub-package
and provides health/readiness endpoints.

Usage:
    # Development
    uv run uvicorn src.main:app --reload

    # Production
    uvicorn src.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from fastapi import FastAPI

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager.

    Handles startup and shutdown events for the OS-APOW system.
    """
    logger.info("OS-APOW system starting up...")
    logger.info("Components: Ear (webhook receiver) | State (GitHub Issues) | Brain (orchestrator) | Hands (worker)")
    yield
    logger.info("OS-APOW system shutting down...")


# Create FastAPI application
app = FastAPI(
    title="OS-APOW - Workflow Orchestration Queue",
    description=(
        "Headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestration.

    Returns:
        Health status indicating the service is operational.
    """
    return {"status": "healthy", "service": "os-apow", "version": "0.1.0"}


@app.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint.

    Verifies that essential configuration is available for the
    system to process requests.

    Returns:
        Readiness status with configuration validation.
    """
    # Basic readiness - the system is ready if the app is running
    # Detailed readiness checks for specific components (notifier, sentinel)
    # are handled by their respective modules
    return {"status": "ready", "service": "os-apow"}


def main() -> None:
    """Main entry point for running the FastAPI application.

    Starts the uvicorn server with configured host and port.
    """
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
