# Tech Stack: workflow-orchestration-queue (OS-APOW)

> **Document Version:** 1.0  
> **Last Updated:** April 2026  
> **Status:** Planning Phase

---

## Overview

workflow-orchestration-queue is a headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders. The technology stack is chosen for its asynchronous capabilities, strong type safety, and reproducibility guarantees.

---

## Languages

| Language | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.12+ | Primary language for orchestrator, webhook receiver, and all system logic |
| **PowerShell Core (pwsh)** | 7.x | Shell Bridge scripts, GitHub authentication, cross-platform CLI |
| **Bash** | 5.x | DevContainer lifecycle scripts, Docker orchestration |

---

## Frameworks & Runtimes

| Framework | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | Latest | High-performance async web framework for webhook receiver (The Ear) |
| **Uvicorn** | Latest | Lightning-fast ASGI server for production deployment |
| **Pydantic** | Latest | Strict data validation, settings management, schema definitions |
| **httpx** | Latest | Fully asynchronous HTTP client for GitHub API calls |

---

## Package Management

| Tool | Version | Purpose |
|------|---------|---------|
| **uv** | 0.10+ | Rust-based Python package installer and resolver (orders of magnitude faster than pip/poetry) |
| **pyproject.toml** | — | Core definition file for dependencies and metadata |
| **uv.lock** | — | Deterministic lockfile for exact package versions |

---

## Containerization & Infrastructure

| Technology | Purpose |
|------------|---------|
| **Docker** | Core execution engine providing sandboxing and environment consistency |
| **DevContainers** | Reproducible development environment for worker containers |
| **Docker Compose** | Multi-container orchestration for complex workflows |

### Container Configuration
- **Network Isolation:** Dedicated bridge network (worker containers cannot access host subnet)
- **Resource Constraints:** 2 CPUs, 4GB RAM per worker container
- **Ephemeral Credentials:** Secrets injected as temporary environment variables

---

## Testing Framework

| Tool | Purpose |
|------|---------|
| **pytest** | Primary testing framework |
| **pytest-asyncio** | Async test support |
| **pytest-cov** | Coverage reporting |
| **httpx test client** | FastAPI endpoint testing |

---

## Security

| Component | Technology |
|-----------|------------|
| **Webhook Verification** | HMAC-SHA256 signature validation |
| **Credential Scrubbing** | Regex-based sanitization (`scrub_secrets()` utility) |
| **Token Management** | GitHub App Installation Tokens (5,000 requests/hr) |

### Secret Patterns Scrubbed
- GitHub PATs: `ghp_*`, `ghs_*`, `gho_*`, `github_pat_*`
- Bearer tokens: `Bearer `
- API keys: `sk-*`
- ZhipuAI keys

---

## AI/LLM Integration

| Component | Details |
|-----------|---------|
| **Agent Runtime** | opencode CLI (v1.2.24+) |
| **Primary Model** | GLM-5 (ZhipuAI) |
| **Alternative Model** | Claude 3.5 Sonnet |
| **MCP Servers** | `@modelcontextprotocol/server-sequential-thinking`, `@modelcontextprotocol/server-memory` |

---

## Development Tools

| Tool | Purpose |
|------|---------|
| **GitHub CLI (gh)** | Repository operations, issue management, API interactions |
| **Git** | Version control |
| **opencode** | AI agent runtime for autonomous development |

---

## Key Design Principles

1. **Script-First Integration:** Use existing `devcontainer-opencode.sh` as the primary API to prevent environment drift
2. **Polling-First Resiliency:** Webhooks as optimization; polling ensures self-healing on restart
3. **Provider-Agnostic Interface:** `ITaskQueue` abstraction allows future provider swapping (Linear, Jira, etc.)
4. **Markdown as Database:** GitHub Issues as persistence layer for world-class audit trail

---

## Dependencies (Core)

```toml
[project]
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
]
```

---

## Version Requirements Summary

| Component | Minimum Version |
|-----------|-----------------|
| Python | 3.12 |
| Docker | 24.0 |
| uv | 0.10.9 |
| Node.js (for MCP) | 20.0 |
| opencode | 1.2.24 |

---

## References

- [Architecture Guide v3.2](./OS-APOW%20Architecture%20Guide%20v3.2.md)
- [Development Plan v4.2](./OS-APOW%20Development%20Plan%20v4.2.md)
- [Implementation Specification v1.2](./OS-APOW%20Implementation%20Specification%20v1.2.md)
