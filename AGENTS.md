# AGENTS.md

> Project-specific instructions for AI coding agents working on **OS-APOW (workflow-orchestration-queue)**.

## Project Overview

**OS-APOW** is a headless agentic orchestration platform that transforms GitHub Issues into autonomous AI-executed work orders. It replaces manual AI co-pilot interactions with a persistent, event-driven infrastructure.

The codebase implements a **4-Pillar Architecture**:

| Pillar | Component | Module | Responsibility |
|--------|-----------|--------|----------------|
| **The Ear** | Work Event Notifier | `src/notifier_service.py`, `src/api/webhooks.py` | FastAPI webhook receiver with HMAC validation |
| **The State** | Work Queue | `src/models/`, `src/queue/github_queue.py` | GitHub Issues as task queue ("Markdown as a Database") |
| **The Brain** | Sentinel Orchestrator | `src/orchestrator_sentinel.py`, `src/services/orchestrator.py` | Background polling, claim-lock, shell-bridge dispatch |
| **The Hands** | Opencode Worker | `src/execution/shell_bridge.py` | DevContainer-based LLM worker execution |

- **Language:** Python 3.12+
- **Framework:** FastAPI + Uvicorn
- **Validation:** Pydantic v2 + pydantic-settings
- **HTTP Client:** httpx (async)
- **Package Manager:** uv
- **Container:** Docker, DevContainers

See [.ai-repository-summary.md](./.ai-repository-summary.md) for the full machine-readable overview and [plan_docs/architecture.md](./plan_docs/architecture.md) for detailed architecture docs.

## Setup Commands

All commands have been validated. Use `uv` for all package operations.

```bash
# Install all dependencies (dev + extras)
uv sync --all-extras

# Run the application
uv run uvicorn src.main:app --reload              # Unified FastAPI app
uv run uvicorn src.notifier_service:app --reload  # Notifier (The Ear) only
uv run python -m src.orchestrator_sentinel        # Sentinel (The Brain)

# Verify import works
uv run python -c "from src.main import app; print(app)"
```

### Environment Setup

Copy `.env.example` to `.env` and configure. Required variables:

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub API token with repo scope |
| `GITHUB_REPO` | Target repository in `owner/repo` format |
| `WEBHOOK_SECRET` | GitHub webhook secret for HMAC validation |
| `SENTINEL_BOT_LOGIN` | Sentinel bot's GitHub login |

Optional: `POLL_INTERVAL_SECONDS` (default 60), `HEARTBEAT_INTERVAL_SECONDS` (default 300), `DEBUG` (default false).

## Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # Dependencies, tool config (ruff, pytest, mypy, coverage)
├── uv.lock                      # Deterministic lockfile
├── Dockerfile                   # Multi-stage build with uv
├── docker-compose.yml           # Multi-service orchestration
├── .env.example                 # Environment variable template
├── src/
│   ├── __init__.py              # Package version
│   ├── main.py                  # Unified FastAPI entry point (health + ready + webhooks)
│   ├── config.py                # Pydantic Settings (AppSettings, NotifierSettings, SentinelSettings)
│   ├── notifier_service.py      # FastAPI webhook receiver (The Ear)
│   ├── orchestrator_sentinel.py # Background polling service (The Brain)
│   ├── api/
│   │   └── webhooks.py          # GitHub webhook handlers
│   ├── models/
│   │   ├── work_item.py         # WorkItem, TaskType, WorkItemStatus, scrub_secrets()
│   │   └── github_events.py     # GitHub webhook payload schemas
│   ├── queue/
│   │   └── github_queue.py      # ITaskQueue ABC + GitHubQueue implementation
│   ├── services/
│   │   └── orchestrator.py      # Sentinel orchestrator service logic
│   └── execution/
│       └── shell_bridge.py      # Shell bridge for worker lifecycle
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   ├── test_main.py             # Main app health/readiness tests
│   ├── test_work_item.py        # Model tests (WorkItem, TaskType, scrub_secrets)
│   ├── test_notifier_service.py # Notifier webhook tests
│   ├── test_github_queue.py     # Queue tests (ITaskQueue, GitHubQueue)
│   ├── test_api/                # API test package
│   ├── test_models/             # Model test package
│   └── test_services/           # Services test package
├── docs/
│   ├── architecture.md          # Architecture guide
│   ├── architecture/adr/        # Architecture Decision Records
│   ├── api/                     # API documentation
│   └── guides/                  # User guides
├── scripts/                     # Shell and PowerShell scripts
│   ├── devcontainer-opencode.sh # Core orchestrator shell bridge
│   └── gh-auth.ps1              # GitHub App authentication
├── plan_docs/                   # Planning documents (external-generated, do not lint)
└── local_ai_instruction_modules/ # Workflow instruction prompts
```

## Code Style

Configuration lives in `pyproject.toml`. Ruff is the sole linter/formatter; MyPy for type checking.

### Ruff Configuration

- **Target:** Python 3.12
- **Line length:** 120 characters
- **Rule sets:** pycodestyle (E/W), pyflakes (F), isort (I), flake8-bugbear (B), comprehensions (C4), pyupgrade (UP), unused-arguments (ARG), simplify (SIM), type-checking (TCH), use-pathlib (PTH), eradicate (ERA), ruff-specific (RUF)
- **Ignored:** E501 (formatter handles), B008, B904, ARG001

### Type Checking

- MyPy in strict mode with `pydantic.mypy` plugin
- All `src/` code must have full type annotations
- Tests (`tests/*`) are exempt from strict typing

### Naming Conventions

- Files: `snake_case.py`
- Test files: `test_*.py` or `*_test.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Pydantic models: `PascalCase` (e.g., `WorkItem`, `TaskType`)

### Import Ordering

Ruff's isort enforces: stdlib → third-party → first-party (`src`).

## Testing Instructions

### Commands

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_work_item.py -v

# Run a single test by name
uv run pytest tests/test_work_item.py::TestScrubSecrets::test_scrub_github_pat -v

# Skip slow tests
uv run pytest -m "not slow"
```

### Test Configuration

- Framework: pytest with pytest-asyncio (auto mode)
- Location: `tests/` directory
- Patterns: `test_*.py`, `*_test.py`
- Async: `asyncio_mode = "auto"` — all async tests run automatically
- Markers: `@pytest.mark.slow`, `@pytest.mark.integration`

### What to Test

- Every new Pydantic model needs model creation/validation tests
- Every new API endpoint needs tests in `tests/test_api/`
- Every new service function needs tests in `tests/test_services/`
- The `scrub_secrets()` function must cover new secret patterns

### Full Quality Gate

Run this before committing. All must pass:

```bash
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run python -m mypy src/ && uv run pytest tests/ -v
```

## Architecture Notes

### 4-Pillar Pattern

All changes must respect component boundaries. Each pillar has a clear responsibility:

- **The Ear** (`src/notifier_service.py`, `src/api/`) — Receives webhooks, validates HMAC signatures, triages events, applies `agent:queued` label. Does NOT execute tasks.
- **The State** (`src/models/`, `src/queue/`) — Pydantic models for data validation, `ITaskQueue` ABC with `GitHubQueue` implementation. The `ITaskQueue` interface enables future provider swapping (Linear, Jira, etc.).
- **The Brain** (`src/orchestrator_sentinel.py`, `src/services/`) — Polls for `agent:queued` issues, claims via assign-then-verify pattern, dispatches through shell-bridge, manages heartbeats. Polling-first design ensures self-healing on restart.
- **The Hands** (`src/execution/`) — Shell bridge that manages the DevContainer-based opencode worker lifecycle.

### Key Design Decisions

1. **Polling-First Resiliency:** Webhooks are optimization; polling ensures self-healing on restart (ADR 08)
2. **Provider-Agnostic Queue:** All queue interactions via `ITaskQueue` interface (ADR 09)
3. **Shell-Bridge Protocol:** Sentinel dispatches exclusively via `devcontainer-opencode.sh` to prevent environment drift (ADR 07)
4. **Markdown as Database:** GitHub Issues + labels for state persistence and audit trail
5. **Unified Config:** All settings in `src/config.py` via Pydantic Settings with `.env` support

### Label State Machine

```
agent:queued → agent:in-progress → agent:success
                   ↓
              agent:error
                   ↓
           agent:infra-failure
                   ↓
          agent:stalled-budget
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check with config validation |
| POST | `/webhooks/github` | GitHub webhook receiver (HMAC validated) |

## PR and Commit Guidelines

### Branch Naming

- `feature/<short-description>` — New features
- `fix/<short-description>` — Bug fixes
- `docs/<short-description>` — Documentation changes
- `dynamic-workflow-project-setup` — Active project setup branch

### Commit Messages

Use conventional commit format:

```
type(scope): description

feat(webhooks): add issue comment event handler
fix(queue): resolve race condition in claim_task
test(models): add scrub_secrets edge case tests
docs(readme): update configuration section
refactor(config): consolidate settings classes
```

Types: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `ci`

### Required CI Checks

The CI pipeline (`.github/workflows/ci.yml`) runs these jobs:

1. **Lint** — `uv run ruff check src/ tests/` + `uv run ruff format --check src/ tests/`
2. **Type Check** — `uv run python -m mypy src/`
3. **Test** — `uv run pytest tests/ -v --cov=src` (depends on lint passing)
4. **Build** — Docker image build (depends on lint + test passing)
5. **Security Scan** — pip-audit + Trivy (non-blocking)

Do not push until all local checks pass (see Full Quality Gate above).

## Common Pitfalls

- **Missing environment variables:** The app crashes at startup if `GITHUB_TOKEN`, `GITHUB_REPO`, or `WEBHOOK_SECRET` are empty or contain placeholder values. Copy `.env.example` to `.env` and fill in real values before running.
- **Always use `uv run` prefix:** Do not call `pytest`, `ruff`, or `mypy` directly. Use `uv run pytest`, `uv run ruff`, etc.
- **Install before testing:** Run `uv sync --all-extras` before any other command after pulling new changes.
- **`plan_docs/` is external-generated:** Do not lint or reformat files in `plan_docs/`. They are seeded from external sources.
- **`scrub_secrets()` before GitHub posts:** Any output posted to GitHub comments must pass through `scrub_secrets()` to prevent credential leakage.
- **HMAC validation on webhooks:** All webhook handlers must verify the `X-Hub-Signature-256` header. Do not bypass signature validation.
- **Respect pillar boundaries:** Do not put orchestration logic in webhook handlers or queue logic in models. Keep each pillar focused.
- **`asyncio_mode = "auto"`:** Async tests do not need explicit `@pytest.mark.asyncio` decorator, but the event loop scope is function-level by default.
- **Connection pooling:** `GitHubQueue` creates a single `httpx.AsyncClient` in `__init__()`. Always call `await queue.close()` in teardown.
- **Subprocess timeouts:** All subprocess calls in the sentinel use timeouts (5700s for prompts, 300s for infra commands). Do not remove these safety nets.
