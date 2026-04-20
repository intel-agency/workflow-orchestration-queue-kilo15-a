# OS-APOW Architecture Guide

> **Adapted from:** `plan_docs/architecture.md` and `plan_docs/OS-APOW Architecture Guide v3.2.md`
> **Version:** 1.0 | **Last Updated:** April 2026 | **Status:** Active

---

## Executive Summary

**workflow-orchestration-queue (OS-APOW)** transforms the paradigm from Interactive AI Coding to Headless Agentic Orchestration. Instead of requiring a human-in-the-loop to navigate files, provide context, and trigger executions, this system provides a persistent, event-driven infrastructure that transforms GitHub Issues into autonomous Execution Orders fulfilled by specialized AI agents.

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

**Implementation:** `src/notifier_service.py`, `src/api/webhooks.py`

**Technology:** Python 3.12, FastAPI, Pydantic, uv

**Responsibilities:**
- **Secure Webhook Ingestion:** Hardened endpoint for GitHub webhook events
- **Cryptographic Verification:** HMAC-SHA256 signature validation against `WEBHOOK_SECRET`
- **Intelligent Event Triage:** Parse issue body/labels to determine task type
- **Queue Initialization:** Apply `agent:queued` label for valid triggers
- **WorkItem Manifest Generation:** Create structured JSON for machine-readable state

---

### 2. The State (Work Queue)

**Implementation:** `src/models/`, `src/queue/github_queue.py`

**Philosophy:** "Markdown as a Database" — leverage GitHub Issues for:
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

**Concurrency Control:** Assign-Then-Verify Pattern to prevent race conditions between multiple Sentinel instances.

---

### 3. The Brain (Sentinel Orchestrator)

**Implementation:** `src/services/orchestrator.py`, `src/orchestrator_sentinel.py`

**Technology:** Python (async background service), Shell Bridge, Docker CLI

**Responsibilities:**
- **Polling Discovery:** Query GitHub API every 60 seconds for `agent:queued` issues
- **Rate Limit Handling:** Jittered exponential backoff on 403/429 responses
- **Shell-Bridge Protocol:** Manage worker via shell scripts (ADR 07)
- **Telemetry:** Heartbeat comments every 5 minutes
- **Environment Reset:** Stop worker container between tasks
- **Graceful Shutdown:** Handle SIGTERM/SIGINT, finish current task, exit cleanly

---

### 4. The Hands (Opencode Worker)

**Implementation:** `src/execution/shell_bridge.py`, `scripts/devcontainer-opencode.sh`

**Technology:** opencode CLI, LLM (GLM-5), DevContainer

**Capabilities:**
- Contextual awareness of project structure
- Execution of markdown workflow modules
- Local test suite verification before PR submission
- Environment parity with human developer setup

**Isolation:**
- Dedicated Docker network (no host access)
- Resource constraints: 2 CPUs, 4GB RAM
- Ephemeral credentials (destroyed on exit)

---

## Key Architectural Decisions

See [Architecture Decision Records](./architecture/adr/) for detailed ADRs:

| ADR | Title | Summary |
|-----|-------|---------|
| ADR-001 | Use Python 3.12+ with uv | Modern async Python with fast package management |
| ADR-002 | FastAPI for Webhook Receiver | High-performance async framework with auto docs |
| ADR-003 | GitHub Issues as Task Queue | "Markdown as a Database" for full transparency |
| ADR-004 | 4-Pillar Architecture | Ear/State/Brain/Hands separation of concerns |
| ADR-005 | Shell-Bridge Execution | Script-first worker dispatch (ADR 07) |
| ADR-006 | HMAC-SHA256 Webhook Verification | Cryptographic payload validation |
| ADR-007 | Polling-First Resiliency | Self-healing on restart via continuous polling |
| ADR-008 | Provider-Agnostic Queue Interface | ITaskQueue ABC for future provider swapping |

---

## Data Flow (Happy Path)

```
1. User opens GitHub Issue with [Application Plan] template
2. GitHub Webhook → The Ear (FastAPI)
3. Ear validates signature, confirms pattern, adds agent:queued label
4. Sentinel poller detects new label
5. Sentinel assigns itself, updates to agent:in-progress
6. Sentinel runs git clone/pull to sync workspace
7. Sentinel executes shell-bridge up
8. Sentinel dispatches: shell-bridge prompt "Execute workflow..."
9. Worker (opencode) reads issue, creates child Epic issues
10. Worker posts "Execution Complete" comment
11. Sentinel detects exit, applies agent:success label
```

---

## Security Model

- **Network Isolation:** Worker containers in dedicated Docker network
- **Credential Management:** GitHub App Installation Tokens (scoped, temporary)
- **Credential Scrubbing:** `scrub_secrets()` removes sensitive patterns before GitHub posts
- **Resource Constraints:** 2 CPUs, 4GB RAM per worker container

---

## References

- [Tech Stack](../../plan_docs/tech-stack.md)
- [Development Plan](../../plan_docs/OS-APOW%20Development%20Plan%20v4.2.md)
- [Implementation Specification](../../plan_docs/OS-APOW%20Implementation%20Specification%20v1.2.md)
- [API Documentation](../api/README.md)
