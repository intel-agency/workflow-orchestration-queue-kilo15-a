# Architecture: workflow-orchestration-queue (OS-APOW)

> **Document Version:** 1.0  
> **Last Updated:** April 2026  
> **Status:** Planning Phase

---

## Executive Summary

workflow-orchestration-queue transforms the paradigm from **Interactive AI Coding** to **Headless Agentic Orchestration**. Traditional AI developer tools require a human-in-the-loop to navigate files, provide context, and trigger executions. This system replaces that manual overhead with a persistent, event-driven infrastructure that transforms GitHub Issues into "Execution Orders" autonomously fulfilled by specialized AI agents.

The system is designed to be **Self-Bootstrapping** — the initial deployment is seeded manually, then the orchestrator builds its own remaining features using its own agentic workflows.

---

## System Architecture: The 4 Pillars

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
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  FastAPI + HMAC Validation + Event Triage + Manifest Gen    │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         THE STATE                                    │
│                      (Work Queue)                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  GitHub Issues + Labels + Milestones                        │    │
│  │  "Markdown as a Database"                                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  States: agent:queued → agent:in-progress → agent:success/error     │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         THE BRAIN                                    │
│                 (Sentinel Orchestrator)                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Polling Loop + Claim Lock + Shell-Bridge Dispatch          │    │
│  │  Heartbeat + Graceful Shutdown + Cost Guardrails            │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         THE HANDS                                    │
│                    (Opencode Worker)                                 │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  DevContainer + opencode CLI + LLM Agent                    │    │
│  │  Instruction Modules + Vector Indexing + Verification       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. The Ear (Work Event Notifier)

**Technology:** Python 3.12, FastAPI, Pydantic, uv

**Responsibilities:**
- **Secure Webhook Ingestion:** Hardened endpoint for GitHub webhook events
- **Cryptographic Verification:** HMAC-SHA256 signature validation against `WEBHOOK_SECRET`
- **Intelligent Event Triage:** Parse issue body/labels to determine task type
- **Queue Initialization:** Apply `agent:queued` label for valid triggers
- **WorkItem Manifest Generation:** Create structured JSON for machine-readable state

**Security:** Every request validated against X-Hub-Signature-256 header before processing

---

### 2. The State (Work Queue)

**Implementation:** GitHub Issues, Labels, and Milestones

**Philosophy:** "Markdown as a Database" — leverage GitHub for:
- World-class audit trail
- Transparent versioning
- Out-of-the-box UI for human supervision
- Real-time intervention via commenting

**State Machine (Label Logic):**

| State | Label | Meaning |
|-------|-------|---------|
| Queued | `agent:queued` | Task validated, awaiting Sentinel |
| In Progress | `agent:in-progress` | Sentinel has claimed the issue |
| Reconciling | `agent:reconciling` | Stale task being recovered |
| Success | `agent:success` | Workflow completed successfully |
| Error | `agent:error` | Technical failure occurred |
| Infra Failure | `agent:infra-failure` | Container/environment failure |
| Stalled Budget | `agent:stalled-budget` | Budget threshold exceeded |

**Concurrency Control:**
- **Assign-Then-Verify Pattern:** Prevents race conditions
  1. Attempt to assign Sentinel bot to issue
  2. Re-fetch the issue
  3. Verify assignment before proceeding
  4. If verification fails, skip gracefully

---

### 3. The Brain (Sentinel Orchestrator)

**Technology:** Python (async background service), PowerShell, Docker CLI

**Responsibilities:**
- **Polling Discovery:** Query GitHub API every 60 seconds for `agent:queued` issues
- **Rate Limit Handling:** Jittered exponential backoff on 403/429 responses
- **Auth Synchronization:** Run `scripts/gh-auth.ps1` before execution
- **Shell-Bridge Protocol:** Manage worker via `devcontainer-opencode.sh`
- **Telemetry:** Capture stdout, post heartbeat comments every 5 minutes
- **Environment Reset:** Stop worker container between tasks
- **Graceful Shutdown:** Handle SIGTERM/SIGINT, finish current task, exit cleanly

**Shell-Bridge Commands:**
```bash
./scripts/devcontainer-opencode.sh up      # Provision environment
./scripts/devcontainer-opencode.sh start   # Launch opencode server
./scripts/devcontainer-opencode.sh prompt  # Execute workflow
```

**Exit Code Mapping:**
- Exit 0 = Success
- Exit 1-10 = Infrastructure Error
- Exit 11+ = Logic/Agent Error

---

### 4. The Hands (Opencode Worker)

**Technology:** opencode CLI, LLM (GLM-5/Claude), DevContainer

**Capabilities:**
- **Contextual Awareness:** Access project structure, vector-indexed codebase
- **Instructional Logic:** Execute markdown workflow modules from `/local_ai_instruction_modules/`
- **Verification:** Run local test suites before PR submission
- **Environment Parity:** Bit-for-bit identical to human developer environment

**Isolation:**
- Dedicated Docker network (no host access)
- Resource constraints: 2 CPUs, 4GB RAM
- Ephemeral credentials (destroyed on exit)

---

## Key Architectural Decisions (ADRs)

### ADR 07: Standardized Shell-Bridge Execution

**Decision:** Orchestrator interacts with agentic environment exclusively via `./scripts/devcontainer-opencode.sh`

**Rationale:** Reusing shell infrastructure prevents "Configuration Drift" — agent runs in identical environment to local developer. Python code remains focused on logic/state.

**Consequence:** Clear separation between Logic Layer (Python) and Infra Layer (Shell)

---

### ADR 08: Polling-First Resiliency Model

**Decision:** Sentinel uses polling as primary discovery; webhooks are optimization

**Rationale:** Webhooks are "fire and forget" — if server is down during event, it's lost forever. Polling ensures state reconciliation on every restart.

**Consequence:** System is inherently self-healing and resilient against downtime

---

### ADR 09: Provider-Agnostic Interface Layer

**Decision:** All queue interactions abstracted behind `ITaskQueue` interface

**Rationale:** While Phase 1 targets GitHub, architecture supports swapping to Linear, Notion, or SQL queues without rewriting orchestrator logic.

**Interface Methods:**
- `fetch_queued()`
- `claim_task(id, sentinel_id)`
- `update_progress(id, log_line)`
- `finish_task(id, artifacts)`

---

## Data Flow (Happy Path)

```
1. User opens GitHub Issue with [Application Plan] template
2. GitHub Webhook → The Ear (FastAPI)
3. Ear validates signature, confirms pattern, adds agent:queued label
4. Sentinel poller detects new label
5. Sentinel assigns itself, updates to agent:in-progress
6. Sentinel runs git clone/pull to sync workspace
7. Sentinel executes devcontainer-opencode.sh up
8. Sentinel dispatches: prompt "Run workflow: create-app-plan.md..."
9. Worker (Opencode) reads issue, creates child Epic issues
10. Worker posts "Execution Complete" comment
11. Sentinel detects exit, applies agent:success label
```

---

## Security Model

### Network Isolation
- Worker containers in dedicated Docker network
- No access to host subnet or peer containers

### Credential Management
- GitHub App Installation Tokens (scoped, temporary)
- Ephemeral environment variables (destroyed on exit)
- Least-privilege access model

### Credential Scrubbing
All worker output passed through `scrub_secrets()` before posting to GitHub:
- GitHub PATs: `ghp_*`, `ghs_*`, `gho_*`, `github_pat_*`
- Bearer tokens, API keys (`sk-*`), ZhipuAI keys

### Resource Constraints
- 2 CPUs, 4GB RAM per worker container
- Prevents DoS from rogue agents

---

## Self-Bootstrapping Lifecycle

```
Stage 0 (Seeding)     → Manual clone of template repository
Stage 1 (Manual)      → Run devcontainer-opencode.sh up
Stage 2 (Project Setup) → Agent configures env vars, indexes codebase
Stage 3 (Handover)    → Start sentinel.py, AI builds remaining features
Stage 4 (Autonomous)  → Developer interacts only via GitHub Issues
```

---

## Cross-Cutting Implementation Directions

### Unified Data Model
All Pydantic models (`WorkItem`, `TaskType`, `WorkItemStatus`) in single shared module: `src/models/work_item.py`

### Graceful Shutdown
- Handle `SIGTERM` and `SIGINT` via signal handlers
- Set shutdown flag, finish current task, close connection pool, exit cleanly

### Subprocess Timeout
- All subprocess calls use `asyncio.wait_for()` with timeout
- Prompt command: 5700s (95 min) — higher than inner watchdog (5400s)
- Infrastructure commands: 60-300s

### Environment Variable Validation
- Validate required env vars at startup
- Crash immediately with clear error if missing or placeholder

### Connection Pooling
- Single `httpx.AsyncClient` created in `GitHubQueue.__init__()`
- Reused across all API calls
- `async close()` method for graceful shutdown

---

## Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # Core dependencies and metadata
├── uv.lock                      # Deterministic lockfile
├── src/
│   ├── notifier_service.py      # FastAPI webhook ingestion
│   ├── orchestrator_sentinel.py # Background polling and dispatch
│   ├── models/
│   │   ├── work_item.py         # Unified WorkItem, TaskType, scrub_secrets()
│   │   └── github_events.py     # GitHub webhook payload schemas
│   └── queue/
│       └── github_queue.py      # ITaskQueue ABC + GitHubQueue
├── scripts/
│   ├── devcontainer-opencode.sh # Core orchestrator shell bridge
│   ├── gh-auth.ps1              # GitHub App authentication
│   └── update-remote-indices.ps1# Vector index sync
├── local_ai_instruction_modules/
│   ├── create-app-plan.md       # Planning workflow prompts
│   ├── perform-task.md          # Implementation workflow
│   └── analyze-bug.md           # Bugfix workflow
└── docs/                        # Architecture and user documentation
```

---

## References

- [Development Plan v4.2](./OS-APOW%20Development%20Plan%20v4.2.md)
- [Implementation Specification v1.2](./OS-APOW%20Implementation%20Specification%20v1.2.md)
- [Plan Review](./OS-APOW%20Plan%20Review.md)
- [Simplification Report v1](./OS-APOW%20Simplification%20Report%20v1.md)
