# Dockerfile for workflow-orchestration-queue
# Multi-stage build for optimized production image

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

# Install uv - fast Python package installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./

# Copy README for package metadata
COPY README.md LICENSE* ./

# Copy source code BEFORE editable install
COPY src/ ./src/

# Install dependencies (including dev dependencies for now)
RUN uv pip install --no-cache -e ".[dev]"

# -----------------------------------------------------------------------------
# Stage 2: Runtime
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Install uv in runtime for any dynamic installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH"

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy source code and config
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup pyproject.toml uv.lock* ./
COPY --chown=appuser:appgroup README.md LICENSE* ./

# Copy scripts for shell-bridge execution
COPY --chown=appuser:appgroup scripts/ ./scripts/

# Switch to non-root user
USER appuser

# Expose port for notifier service
EXPOSE 8000

# Health check using Python stdlib (not curl)
# This checks the notifier service health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default command runs the notifier service
CMD ["uvicorn", "src.notifier_service:app", "--host", "0.0.0.0", "--port", "8000"]
