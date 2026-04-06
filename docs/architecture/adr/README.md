# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the workflow-orchestration-queue system.

## What is an ADR?

An ADR is a document that captures an important architectural decision made along with its context and consequences.

## Index

| Number | Title | Status |
|--------|-------|--------|
| ADR-001 | Use Python 3.12+ with uv | Accepted |
| ADR-002 | FastAPI for Webhook Receiver | Accepted |
| ADR-003 | GitHub Issues as Task Queue | Accepted |
| ADR-004 | 4-Pillar Architecture | Accepted |
| ADR-005 | Shell-Bridge Execution Pattern | Accepted |
| ADR-006 | HMAC-SHA256 Webhook Verification | Accepted |
| ADR-007 | Polling-First Resiliency Model | Accepted |
| ADR-008 | Provider-Agnostic Queue Interface | Accepted |

## Template

```markdown
# ADR-NNN: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that motivates this decision?

## Decision
What is the change that we're proposing?

## Consequences
What becomes easier or more difficult because of this change?
```
