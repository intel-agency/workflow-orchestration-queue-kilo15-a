# workflow-orchestration-queue

> **Headless Agentic Orchestration Platform**

[![CI](https://github.com/intel-agency/workflow-orchestration-queue-kilo15-a/actions/workflows/ci.yml/badge.svg)](https://github.com/intel-agency/workflow-orchestration-queue-kilo15-a/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Overview

**workflow-orchestration-queue** (OS-APOW) is a groundbreaking headless agentic orchestration platform that transforms GitHub Issues into autonomous execution orders. It shifts AI from a passive co-pilot to an autonomous background production service capable of multi-step, specification-driven task fulfillment without human intervention.

### Key Features

- **Zero-Touch Construction:** User opens a specification issue and receives a functional, test-passed branch and PR within minutes
- **Self-Bootstrapping Evolution:** System builds itself — once Phase 1 is functional, the orchestrator builds Phase 2 and 3 using its own workflows
- **State Visibility:** Distributed state stored in GitHub via labels and comments for world-class audit trail
- **Script-First Integration:** Use existing devcontainer-opencode.sh as primary API to prevent environment drift

## Architecture

The system implements a **4-Pillar Architecture**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL STIMULUS                             │
│                     (GitHub Webhook Event)                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         THE EAR                                      │
│                   (Work Event Notifier)                              │
│          FastAPI + HMAC Validation + Event Triage                    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         THE STATE                                    │
│                      (Work Queue)                                    │
│         GitHub Issues + Labels + Milestones                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         THE BRAIN                                    │
│                 (Sentinel Orchestrator)                              │
│       Polling Loop + Claim Lock + Shell-Bridge Dispatch              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         THE HANDS                                    │
│                    (Opencode Worker)                                 │
│     DevContainer + opencode CLI + LLM Agent                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Components

| Pillar | Component | Technology | Purpose |
|--------|-----------|------------|---------|
| **The Ear** | `notifier_service.py` | FastAPI, Pydantic | Secure webhook ingestion with HMAC validation |
| **The State** | GitHub Issues | Labels, Comments | Queue storage ("Markdown as a Database") |
| **The Brain** | `orchestrator_sentinel.py` | Python async, httpx | Polling, dispatch, heartbeat management |
| **The Hands** | opencode worker | DevContainer, LLM | Autonomous task execution |

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.12+ |
| **Web Framework** | FastAPI + Uvicorn |
| **Data Validation** | Pydantic v2 |
| **HTTP Client** | HTTPX (async) |
| **Package Manager** | uv |
| **Containerization** | Docker, DevContainers |
| **Testing** | pytest, pytest-asyncio, pytest-cov |
| **Linting** | Ruff, MyPy |
| **AI/LLM** | opencode CLI, GLM-5 |

## Project Structure

```
workflow-orchestration-queue/
├── src/
│   ├── __init__.py
│   ├── notifier_service.py      # FastAPI webhook receiver (The Ear)
│   ├── orchestrator_sentinel.py # Background polling service (The Brain)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── work_item.py         # WorkItem, TaskType, scrub_secrets()
│   │   └── github_events.py     # GitHub webhook payload schemas
│   └── queue/
│       ├── __init__.py
│       └── github_queue.py      # ITaskQueue ABC + GitHubQueue
├── tests/
│   ├── __init__.py
│   ├── test_work_item.py
│   ├── test_notifier_service.py
│   └── test_github_queue.py
├── scripts/
│   ├── devcontainer-opencode.sh # Core orchestrator shell bridge
│   ├── gh-auth.ps1              # GitHub App authentication
│   └── update-remote-indices.ps1
├── docs/
│   ├── architecture/            # Architecture documentation
│   ├── api/                     # API documentation
│   └── guides/                  # User guides
├── plan_docs/                   # Planning documents
├── pyproject.toml               # Project configuration
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Multi-service orchestration
└── README.md                    # This file
```

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for containerized deployment)
- GitHub account with repository access

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/intel-agency/workflow-orchestration-queue-kilo15-a.git
   cd workflow-orchestration-queue-kilo15-a
   ```

2. **Install dependencies:**
   ```bash
   uv sync --dev
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the notifier service:**
   ```bash
   uv run uvicorn src.notifier_service:app --reload
   ```

5. **Run tests:**
   ```bash
   uv run pytest
   ```

### Docker Deployment

```bash
# Build the image
docker build -t workflow-queue .

# Run the notifier service
docker run -p 8000:8000 --env-file .env workflow-queue

# Run with docker-compose (full stack)
docker-compose --profile full up
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub API token with repo scope |
| `GITHUB_REPO` | Yes | Repository in owner/repo format |
| `WEBHOOK_SECRET` | Yes | GitHub webhook secret for HMAC validation |
| `SENTINEL_BOT_LOGIN` | Yes | Sentinel bot's GitHub login |
| `POLL_INTERVAL_SECONDS` | No | Polling interval (default: 60) |
| `HEARTBEAT_INTERVAL_SECONDS` | No | Heartbeat comment interval (default: 300) |
| `DEBUG` | No | Enable debug mode (default: false) |

### Label States

| Label | State | Description |
|-------|-------|-------------|
| `agent:queued` | Queued | Task validated, awaiting Sentinel |
| `agent:in-progress` | In Progress | Sentinel has claimed the issue |
| `agent:success` | Success | Workflow completed successfully |
| `agent:error` | Error | Technical failure occurred |
| `agent:infra-failure` | Infra Failure | Container/environment failure |
| `agent:stalled-budget` | Stalled Budget | Budget threshold exceeded |

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

### Readiness Check
```
GET /ready
```
Returns readiness status with configuration validation.

### GitHub Webhook
```
POST /webhooks/github
```
Receives GitHub webhook events with HMAC signature validation.

## Development

### Code Quality

```bash
# Run linter
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/

# Type check
uv run mypy src/

# Run all checks
uv run ruff check src/ tests/ && uv run mypy src/ && uv run pytest
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_work_item.py -v
```

## Security

### Webhook Verification

All webhook requests are validated using HMAC-SHA256 signatures before processing. The signature is verified against the `X-Hub-Signature-256` header.

### Credential Scrubbing

All worker output is passed through `scrub_secrets()` before posting to GitHub to prevent credential leakage. Scrubbed patterns include:

- GitHub PATs (`ghp_*`, `ghs_*`, `gho_*`, `github_pat_*`)
- Bearer tokens
- API keys (`sk-*`)
- ZhipuAI keys

## Documentation

- [Architecture Guide](./plan_docs/architecture.md) - Detailed system architecture
- [Tech Stack](./plan_docs/tech-stack.md) - Technology choices and rationale
- [API Documentation](./docs/api/) - Endpoint documentation
- [User Guides](./docs/guides/) - How-to guides for common tasks

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Package management by [uv](https://docs.astral.sh/uv/)
- AI orchestration via [opencode](https://github.com/opencode-ai/opencode)

---

**Repository Summary:** See [.ai-repository-summary.md](./.ai-repository-summary.md) for an AI-readable overview.
