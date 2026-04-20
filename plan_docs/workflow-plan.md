# Workflow Execution Plan: project-setup

**Workflow:** `project-setup`
**Dynamic Workflow File:** `ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md`
**Repository:** `intel-agency/workflow-orchestration-queue-kilo15-a`
**Branch:** `dynamic-workflow-project-setup`
**Date:** 2026-04-13

---

## 1. Overview

This document is the execution plan for the **project-setup** dynamic workflow, which will initialize the `workflow-orchestration-queue` (OS-APOW) repository and scaffold the complete project foundation.

| Property | Value |
|---|---|
| **Workflow Name** | project-setup |
| **Project Name** | workflow-orchestration-queue (OS-APOW) |
| **Brief Description** | Headless agentic orchestration platform that transforms GitHub Issues into autonomous AI worker execution orders via DevContainers and shell-bridge infrastructure |
| **Total Main Assignments** | 6 |
| **Pre-script Events** | 1 (`create-workflow-plan`) |
| **Post-assignment Events** | 2 per main assignment (`validate-assignment-completion`, `report-progress`) |
| **Post-script Events** | 1 (`orchestration:plan-approved` label application) |

**High-Level Summary:**

The workflow begins by creating this execution plan (current step), then initializes the repository with GitHub Projects, labels, milestones, and branch protection. It proceeds through application planning, project structure scaffolding, AGENTS.md creation, debrief documentation, and finally merges the setup PR. After each main assignment, an independent validation and progress report is executed. Upon full completion, the `orchestration:plan-approved` label is applied to the plan issue to trigger the next orchestration phase.

---

## 2. Project Context Summary

### 2.1 Key Facts

| Fact | Detail |
|---|---|
| **Project Name** | workflow-orchestration-queue (OS-APOW — Opencode-Server Agent Workflow Orchestration) |
| **Repository** | `intel-agency/workflow-orchestration-queue-kilo15-a` |
| **Description** | A headless agentic orchestration platform that replaces interactive AI coding with autonomous background processing. GitHub Issues labeled `agent:queued` trigger AI workers that clone repos, generate code, run tests, and submit PRs without human intervention. |
| **Tech Stack** | Python 3.12+, FastAPI, Pydantic, httpx, uv (package manager), Docker/DevContainers, PowerShell Core (pwsh), Bash |
| **Frameworks** | FastAPI (webhook receiver), Uvicorn (ASGI server), Pydantic (data validation), httpx (async HTTP client) |
| **Package Manager** | uv (Rust-based Python package manager, tracked via `pyproject.toml` + `uv.lock`) |
| **No .NET** | This is a Python/Shell ecosystem. No `global.json` or .NET tooling required. |

### 2.2 Architecture — Four Pillars

1. **The Ear (Work Event Notifier):** FastAPI-based webhook receiver (`notifier_service.py`) that ingests GitHub events, validates HMAC signatures, triages issues, and queues tasks.
2. **The State (Work Queue):** GitHub Issues as the persistence layer ("Markdown as a Database") with label-based state machine (`agent:queued` → `agent:in-progress` → `agent:success`/`agent:error`).
3. **The Brain (Sentinel Orchestrator):** Persistent async Python background service (`orchestrator_sentinel.py`) that polls for queued tasks, claims them via assign-then-verify locking, manages worker lifecycle via shell bridge, and posts heartbeats.
4. **The Hands (Opencode Worker):** Isolated DevContainer environment executing LLM-driven agent instructions via `devcontainer-opencode.sh` shell bridge.

### 2.3 Phased Delivery Plan

| Phase | Name | Scope |
|---|---|---|
| Phase 0 | Seeding & Bootstrapping | Manual repo clone, environment setup, plan doc seeding |
| Phase 1 | The Sentinel (MVP) | Polling engine, shell-bridge dispatch, status feedback, heartbeat, locking |
| Phase 2 | The Ear (Webhook Automation) | FastAPI webhook receiver, HMAC validation, intelligent triage |
| Phase 3 | Deep Orchestration | Architect sub-agent, hierarchical decomposition, self-healing, cost guardrails |

### 2.4 Reference Implementations

Reference code exists in `plan_docs/`:
- `orchestrator_sentinel.py` — Full Sentinel implementation with signal handling, heartbeat coroutine, jittered backoff, and subprocess timeouts
- `notifier_service.py` — FastAPI webhook handler with HMAC validation, environment validation, and queue integration
- `src/models/work_item.py` — Unified `WorkItem`, `TaskType`, `WorkItemStatus` models + `scrub_secrets()` credential scrubber
- `src/queue/github_queue.py` — `ITaskQueue` ABC + `GitHubQueue` concrete implementation with connection pooling, assign-then-verify locking, and heartbeat posting
- `interactive-report.html` — Interactive React-based architecture presentation dashboard

### 2.5 Key Constraints & Design Decisions

- **Shell-First Integration:** Sentinel interacts with workers exclusively via `devcontainer-opencode.sh` — no Docker SDK
- **Polling-First Resiliency:** Webhooks are an optimization; polling is the primary discovery mechanism
- **Provider-Agnostic Interface:** `ITaskQueue` ABC retained for future provider swapping (Linear, Jira)
- **Assign-Then-Verify Locking:** Distributed lock via GitHub Assignees to prevent concurrent Sentinel collisions
- **Credential Scrubbing:** All public-facing output sanitized via `scrub_secrets()` regex
- **Action SHA Pinning:** All GitHub Actions workflows MUST pin actions to specific commit SHAs

### 2.6 Known Issues from Plan Review

The Plan Review document (`OS-APOW Plan Review.md`) identified these issues in the reference implementations:
- **I-1:** Divergent WorkItem models between components — **RESOLVED** (unified in `src/models/work_item.py`)
- **I-2:** Race condition in task claiming — **RESOLVED** (assign-then-verify implemented in `github_queue.py`)
- **I-3:** No jittered exponential backoff — **RESOLVED** (implemented in `orchestrator_sentinel.py`)
- **I-4:** Per-call `httpx.AsyncClient` — **RESOLVED** (connection pooling in `GitHubQueue.__init__()`)
- **I-5:** Hardcoded secrets in notifier — **RESOLVED** (env var validation at import time)
- **I-6:** No heartbeat implementation — **RESOLVED** (async heartbeat coroutine in Sentinel)
- **I-7:** Cost guardrails not implemented — **DEFERRED** (model defined, logic deferred)
- **I-9:** Bare `except: pass` — **RESOLVED** (specific exception handling)
- **I-10:** No environment reset between tasks — **RESOLVED** (`stop` command after each task)

### 2.7 Simplification Decisions (Applied)

Per the Simplification Report (`OS-APOW Simplification Report v1.md`):
- S-3: Reduced to 3 env vars only (GITHUB_TOKEN, GITHUB_ORG, GITHUB_REPO)
- S-4: Environment reset hardcoded to `"stop"` mode only
- S-5: Single-repo polling only (cross-repo noted for future)
- S-6: Queue consolidated to `src/queue/github_queue.py`
- S-7: IPv4 scrubbing pattern removed
- S-8: "Encrypted" log verbiage removed
- S-9: Phase 3 features moved to appendix
- S-10: Single logging to stdout only
- S-11: `raw_payload` field removed from WorkItem

---

## 3. Assignment Execution Plan

### 3.0 Pre-script Event: `create-workflow-plan` (CURRENT)

| Field | Content |
|---|---|
| **Assignment** | `create-workflow-plan`: Create Workflow Plan |
| **Goal** | Create a comprehensive workflow execution plan by reading the dynamic workflow, tracing all assignments, and synthesizing project context from plan_docs/ |
| **Key Acceptance Criteria** | Dynamic workflow fully read; all assignments traced; all plan_docs/ read and summarized; structured plan produced; plan committed as `plan_docs/workflow-plan.md` |
| **Project-Specific Notes** | The project has extensive plan documentation (7 docs + reference code). The reference implementations are production-quality scaffolds that will guide the project structure assignment. |
| **Prerequisites** | Repository cloned; plan_docs/ seeded; remote assignment files accessible |
| **Dependencies** | None (first step) |
| **Risks / Challenges** | Large volume of plan docs to synthesize; ensuring all assignments are correctly traced from remote canonical source |
| **Events** | None (pre-script event itself) |

---

### 3.1 Main Assignment 1: `init-existing-repository`

| Field | Content |
|---|---|
| **Assignment** | `init-existing-repository`: Initiate Existing Repository |
| **Goal** | Set up the repository with branch protection, GitHub Project for issue tracking, labels, renamed workspace/devcontainer files, and an open PR |
| **Key Acceptance Criteria** | (1) New branch `dynamic-workflow-project-setup` created; (2) Branch protection ruleset imported from `.github/protected-branches_ruleset.json`; (3) GitHub Project created with Not Started / In Progress / In Review / Done columns; (4) Labels imported from `.github/.labels.json`; (5) Workspace and devcontainer files renamed; (6) PR opened from branch to main |
| **Project-Specific Notes** | Repository name is `workflow-orchestration-queue-kilo15-a`. Devcontainer should be renamed to `workflow-orchestration-queue-kilo15-a-devcontainer`. Workspace file should be renamed to `workflow-orchestration-queue-kilo15-a.code-workspace`. Branch protection ruleset requires `GH_ORCHESTRATION_AGENT_TOKEN` (PAT with `administration: write` scope). |
| **Prerequisites** | GitHub auth with `repo`, `project`, `read:project`, `read:user`, `user:email` scopes; `administration: write` on repo |
| **Dependencies** | None (first main assignment) |
| **Risks / Challenges** | (1) PAT may lack `administration: write` scope for branch protection import — must fail loudly if so; (2) GitHub Project creation may fail if org-level permissions are insufficient; (3) PR creation requires at least one commit pushed first |
| **Events** | Post-assignment: `validate-assignment-completion` → `report-progress` |

---

### 3.2 Main Assignment 2: `create-app-plan`

| Field | Content |
|---|---|
| **Assignment** | `create-app-plan`: Create Application Plan |
| **Goal** | Create a comprehensive application plan documented as a GitHub Issue using the Appendix A template, based on the plan documents in `plan_docs/` |
| **Key Acceptance Criteria** | (1) Application template analyzed; (2) Plan documented in GitHub Issue using template; (3) `plan_docs/tech-stack.md` created; (4) `plan_docs/architecture.md` created; (5) Milestones created for each phase; (6) Issue linked to GitHub Project and assigned to "Phase 1: Foundation" milestone; (7) Labels applied (planning, documentation); (8) **No implementation code written** |
| **Project-Specific Notes** | The project already has extensive plan docs that serve as the "application template": Development Plan v4.2, Architecture Guide v3.2, Implementation Specification v1.2, plus reference implementations. The agent should synthesize these into a single actionable plan issue. Key tech: Python 3.12+, FastAPI, Pydantic, httpx, uv. No .NET. The plan issue template is at `.github/ISSUE_TEMPLATE/application-plan.md`. |
| **Prerequisites** | Repository initialized (labels, project, milestones available); `plan_docs/` directory with all planning documents |
| **Dependencies** | `init-existing-repository` must be complete (labels and project needed for issue linking) |
| **Risks / Challenges** | (1) Volume of existing plan docs may overwhelm the planning process — agent must synthesize, not copy-paste; (2) The existing plan has 4 phases — milestone creation must align; (3) References to example plans (nam20485/advanced-memory3#12, nam20485/support-assistant#2) should guide formatting; (4) Must resist the urge to write code — this is planning only |
| **Events** | Pre: `gather-context`; Post-assignment: `validate-assignment-completion` → `report-progress`; On-failure: `recover-from-error` |

---

### 3.3 Main Assignment 3: `create-project-structure`

| Field | Content |
|---|---|
| **Assignment** | `create-project-structure`: Create Project Structure |
| **Goal** | Create the actual project structure, scaffolding, Docker configs, CI/CD pipelines, documentation, and repository summary based on the application plan |
| **Key Acceptance Criteria** | (1) Solution/project structure created following Python/uv conventions; (2) `pyproject.toml` with version pinning; (3) Dockerfile + docker-compose.yml created; (4) CI/CD workflow with SHA-pinned actions; (5) README.md + docs/ structure; (6) Test project structure; (7) Repository summary at `.ai-repository-summary.md`; (8) Build verifies successfully |
| **Project-Specific Notes** | Tech stack is Python 3.12+ with uv. Structure should follow the Implementation Spec layout: `src/notifier_service.py`, `src/orchestrator_sentinel.py`, `src/models/work_item.py`, `src/queue/github_queue.py`, `scripts/`, `local_ai_instruction_modules/`, `docs/`. Reference implementations in `plan_docs/` provide the exact code to scaffold. Dockerfile must support Python 3.12+ with uv. Healthcheck must use Python stdlib (no curl). Docker Compose for local dev with Sentinel + Notifier services. |
| **Prerequisites** | Application plan documented in issue (from `create-app-plan`); tech-stack and architecture docs available |
| **Dependencies** | `create-app-plan` must be complete |
| **Risks / Challenges** | (1) Must pin all GitHub Actions to specific commit SHAs; (2) Docker healthcheck cannot use curl — must use Python stdlib; (3) `COPY src/ ./src/` must appear before `uv pip install -e .` in Dockerfile; (4) Reference code in plan_docs/ must be correctly adapted, not blindly copied |
| **Events** | Post-assignment: `validate-assignment-completion` → `report-progress` |

---

### 3.4 Main Assignment 4: `create-agents-md-file`

| Field | Content |
|---|---|
| **Assignment** | `create-agents-md-file`: Create AGENTS.md File |
| **Goal** | Create a comprehensive `AGENTS.md` at the repository root following the open agents.md specification, providing AI coding agents with project context, build commands, and conventions |
| **Key Acceptance Criteria** | (1) `AGENTS.md` exists at repo root; (2) Contains project overview, setup commands, project structure, code style, testing instructions, architecture notes, PR guidelines; (3) All commands validated by running them; (4) Complements (not duplicates) README.md and `.ai-repository-summary.md` |
| **Project-Specific Notes** | Commands will be Python/uv-based: `uv sync`, `uv run python -m src.notifier_service`, `uv run pytest`, `uv run ruff check`. The file must document the Sentinel and Notifier components, the shell-bridge architecture, and the label-based state machine. |
| **Prerequisites** | Repository initialized; project structure created; build/test tooling in place |
| **Dependencies** | `create-project-structure` must be complete |
| **Risks / Challenges** | (1) Commands listed in AGENTS.md must be validated by actually running them — if the project doesn't build yet, this will fail; (2) Must cross-reference with README.md and `.ai-repository-summary.md` to avoid duplication |
| **Events** | Post-assignment: `validate-assignment-completion` → `report-progress` |

---

### 3.5 Main Assignment 5: `debrief-and-document`

| Field | Content |
|---|---|
| **Assignment** | `debrief-and-document`: Debrief and Document Learnings |
| **Goal** | Capture key learnings, insights, deviations, and improvement areas from the completed assignments in a structured debrief report |
| **Key Acceptance Criteria** | (1) Structured report following the 12-section template; (2) All deviations from assignments documented; (3) Execution trace saved at `debrief-and-document/trace.md`; (4) Report committed and pushed; (5) Stakeholder approval obtained |
| **Project-Specific Notes** | This is the first project execution using the workflow-orchestration-queue template, so the debrief is especially valuable for improving the template and assignment definitions. Any issues with branch protection, label import, or project creation should be prominently documented. |
| **Prerequisites** | All main assignments through `create-agents-md-file` complete |
| **Dependencies** | `create-agents-md-file` must be complete |
| **Risks / Challenges** | (1) Agent must accurately recall all deviations — maintaining a trace during execution is critical; (2) The "Plan Adjustment Mandate" requires flagging plan-impacting findings as ACTION ITEMS |
| **Events** | Post-assignment: `validate-assignment-completion` → `report-progress` |

---

### 3.6 Main Assignment 6: `pr-approval-and-merge`

| Field | Content |
|---|---|
| **Assignment** | `pr-approval-and-merge`: Pull Request Approval and Merge |
| **Goal** | Complete the full PR approval and merge process: resolve all review comments, obtain approval, merge the setup PR, delete the setup branch, and close related issues |
| **Key Acceptance Criteria** | (1) All CI checks pass (with remediation loop up to 3 attempts); (2) Code review delegated to `code-reviewer` subagent (not self-review); (3) All review comments resolved via `ai-pr-comment-protocol.md`; (4) PR merged; (5) Source branch deleted; (6) Related issues closed |
| **Project-Specific Notes** | This is a setup PR — **self-approval by the orchestrator is acceptable** (per the dynamic workflow special handling). However, CI remediation loop is still mandatory. The `$pr_num` is extracted from the `init-existing-repository` step. After merge, the `dynamic-workflow-project-setup` branch is deleted. |
| **Prerequisites** | All main assignments complete; PR exists with all commits pushed |
| **Dependencies** | `debrief-and-document` must be complete; PR number from `init-existing-repository` |
| **Risks / Challenges** | (1) CI may fail due to linting issues in plan_docs/ — the AGENTS.md specifies plan_docs/ is excluded from strict linting; (2) Branch protection may require specific reviewers — self-approval must be configured; (3) Must commit and push all local changes BEFORE merge to avoid data loss |
| **Events** | None after this (it's the last main assignment, but post-assignment events still fire) |

---

### 3.7 Post-Assignment Events (After Each Main Assignment)

After every main assignment completes, two events fire in sequence:

#### 3.7.1 `validate-assignment-completion`

| Field | Content |
|---|---|
| **Assignment** | `validate-assignment-completion`: Validate Assignment Completion |
| **Goal** | Independently validate that the just-completed assignment met all acceptance criteria |
| **Key Acceptance Criteria** | (1) All expected files exist; (2) Verification commands pass; (3) Validation report created; (4) Pass/fail status determined; (5) If failed, remediation steps provided |
| **Project-Specific Notes** | Must be delegated to an independent `qa-test-engineer` agent — not the same agent that did the work. For Python projects, verification commands are: `uv sync`, `uv run python -c "import src"`, `uv run ruff check`, `uv run pytest`. For GitHub operations (labels, projects, issues), use `gh` CLI to verify state. |
| **Prerequisites** | A main assignment has just completed |
| **Dependencies** | The assignment being validated |
| **Risks / Challenges** | Validation overhead adds time to each step; must be fast (<5 min) |
| **Events** | None |

#### 3.7.2 `report-progress`

| Field | Content |
|---|---|
| **Assignment** | `report-progress`: Report Progress After Workflow Step Completion |
| **Goal** | Generate structured progress reports, capture outputs, validate acceptance criteria, create checkpoints, and file action items as GitHub issues |
| **Key Acceptance Criteria** | (1) Progress report with step name, duration, status; (2) All outputs captured; (3) Workflow state checkpointed; (4) Action items filed as GitHub issues (mandatory) |
| **Project-Specific Notes** | Each progress report must include Deviations & Findings and Plan-Impacting Discoveries sections. All action items MUST be filed as GitHub issues — not left as text notes. |
| **Prerequisites** | A main assignment (and its validation) has just completed |
| **Dependencies** | `validate-assignment-completion` for the same assignment |
| **Risks / Challenges** | Agent may skip filing issues for "minor" items — this is explicitly forbidden |
| **Events** | None |

---

### 3.8 Post-script Event: Apply `orchestration:plan-approved` Label

| Field | Content |
|---|---|
| **Event** | `post-script-complete` |
| **Goal** | Apply the `orchestration:plan-approved` label to the application plan issue created during `create-app-plan` to signal the plan is ready for epic creation and the next orchestration phase |
| **Key Acceptance Criteria** | Label `orchestration:plan-approved` applied to the plan issue; output recorded as `#events.post-script-complete.plan-approved` |
| **Project-Specific Notes** | This label triggers the next phase of the orchestration pipeline. The plan issue number comes from `#initiate-new-repository.create-app-plan`. |
| **Prerequisites** | All assignments and post-assignment events complete; setup PR merged |
| **Dependencies** | All prior steps |
| **Risks / Challenges** | If the plan issue was not created or its number not recorded, this step will fail |
| **Events** | None (final event) |

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                   PRE-SCRIPT EVENT                                  │
│                                                                     │
│  ┌──────────────────────┐                                           │
│  │ create-workflow-plan  │  ← YOU ARE HERE                          │
│  └──────────┬───────────┘                                           │
└─────────────┼───────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   MAIN ASSIGNMENTS                                   │
│                                                                     │
│  ┌───────────────────────────┐                                       │
│  │ 1. init-existing-repository│                                      │
│  └──────────┬────────────────┘                                       │
│             │  ┌──────────────────────────┐  ┌─────────────────┐    │
│             └─▶│ validate-assignment-      │─▶│ report-progress │    │
│                │ completion               │  └────────┬────────┘    │
│                └──────────────────────────┘           │             │
│                                                       ▼             │
│  ┌───────────────────────────┐                                       │
│  │ 2. create-app-plan        │                                       │
│  └──────────┬────────────────┘                                       │
│             │  ┌──────────────────────────┐  ┌─────────────────┐    │
│             └─▶│ validate-assignment-      │─▶│ report-progress │    │
│                │ completion               │  └────────┬────────┘    │
│                └──────────────────────────┘           │             │
│                                                       ▼             │
│  ┌───────────────────────────┐                                       │
│  │ 3. create-project-structure│                                      │
│  └──────────┬────────────────┘                                       │
│             │  ┌──────────────────────────┐  ┌─────────────────┐    │
│             └─▶│ validate-assignment-      │─▶│ report-progress │    │
│                │ completion               │  └────────┬────────┘    │
│                └──────────────────────────┘           │             │
│                                                       ▼             │
│  ┌───────────────────────────┐                                       │
│  │ 4. create-agents-md-file  │                                       │
│  └──────────┬────────────────┘                                       │
│             │  ┌──────────────────────────┐  ┌─────────────────┐    │
│             └─▶│ validate-assignment-      │─▶│ report-progress │    │
│                │ completion               │  └────────┬────────┘    │
│                └──────────────────────────┘           │             │
│                                                       ▼             │
│  ┌───────────────────────────┐                                       │
│  │ 5. debrief-and-document   │                                       │
│  └──────────┬────────────────┘                                       │
│             │  ┌──────────────────────────┐  ┌─────────────────┐    │
│             └─▶│ validate-assignment-      │─▶│ report-progress │    │
│                │ completion               │  └────────┬────────┘    │
│                └──────────────────────────┘           │             │
│                                                       ▼             │
│  ┌───────────────────────────┐                                       │
│  │ 6. pr-approval-and-merge  │  (self-approval, CI loop, delete     │
│  └──────────┬────────────────┘   setup branch on merge)             │
│             │  ┌──────────────────────────┐  ┌─────────────────┐    │
│             └─▶│ validate-assignment-      │─▶│ report-progress │    │
│                │ completion               │  └────────┬────────┘    │
│                └──────────────────────────┘           │             │
└───────────────────────────────────────────────────────┼─────────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   POST-SCRIPT EVENT                                  │
│                                                                     │
│  ┌──────────────────────────────────────┐                           │
│  │ Apply `orchestration:plan-approved`   │                           │
│  │ label to plan issue                  │                           │
│  └──────────────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Open Questions

### 5.1 PAT Scope for Branch Protection

**Question:** Does the `GH_ORCHESTRATION_AGENT_TOKEN` (or equivalent PAT) have the `administration: write` scope required to import the branch protection ruleset? If not, the `init-existing-repository` assignment will fail at step 2.

**Impact:** Blocks branch protection import; must be resolved before starting `init-existing-repository`.

### 5.2 Application Plan Issue Template Location

**Question:** The `create-app-plan` assignment references an issue template at `.github/ISSUE_TEMPLATE/application-plan.md`. Does this template exist in the repository? The assignment also references an "Appendix A" template. Which should be used?

**Impact:** Affects how the plan issue is formatted.

### 5.3 Existing Content in Repository Root

**Question:** The repository root already contains template files (AGENTS.md, .devcontainer/, .github/, .opencode/, scripts/, test/, local_ai_instruction_modules/). The `create-project-structure` assignment will add new application-specific files. Should the template infrastructure files be preserved as-is, or should they be restructured to accommodate the new project structure?

**Impact:** Affects the scope of `create-project-structure`.

### 5.4 Reference Implementation Usage

**Question:** The reference implementations in `plan_docs/` (orchestrator_sentinel.py, notifier_service.py, etc.) are described as "scaffolds" and "reference code." Should the `create-project-structure` assignment use these as the actual source files (moving them into `src/`), or should they serve only as reference material while new code is written?

**Impact:** Affects code quality and development velocity in `create-project-structure`.

### 5.5 Milestone Naming Convention

**Question:** The plan has 4 phases (0-3). Should milestones be named "Phase 0: Seeding", "Phase 1: Foundation", "Phase 2: Webhook Automation", "Phase 3: Deep Orchestration"? Or should they follow a different convention?

**Impact:** Affects `create-app-plan` milestone creation.

### 5.6 Cost Guardrails (Story 6) Scope

**Question:** Cost guardrails are marked as "deferred" in the plan docs, but `WorkItemStatus.STALLED_BUDGET` and the `agent:stalled-budget` label are defined in the model. Should the project structure include placeholder/stub code for cost guardrails, or omit it entirely?

**Impact:** Minor — affects completeness of `create-project-structure`.

---

## 6. Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| PAT lacks `administration: write` scope | Medium | High — blocks branch protection | Pre-verify with `scripts/test-github-permissions.ps1`; fail loudly if missing |
| CI fails on plan_docs/ linting | Medium | Medium — blocks PR merge | plan_docs/ should be excluded from linting per AGENTS.md |
| Reference code has hidden bugs | Low | Medium — propagates issues | Plan Review already identified and most issues are resolved in the reference code |
| Agent writes code during `create-app-plan` | Low | Medium — violates assignment constraints | Reinforce "planning only" constraint; validation will catch this |
| Branch deletion loses uncommitted work | Low | High — data loss | Ensure all changes are committed and pushed before merge in `pr-approval-and-merge` |
| GitHub API rate limiting during setup | Low | Low — retryable | Assignments use `gh` CLI which handles auth; no polling loop in setup |

---

*This plan was auto-generated by the `create-workflow-plan` pre-script event of the `project-setup` dynamic workflow.*
*All assignment definitions were resolved from the canonical remote repository: `nam20485/agent-instructions`.*
