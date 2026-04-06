# Workflow Execution Plan: project-setup

**Workflow Name:** `project-setup`  
**Repository:** `intel-agency/workflow-orchestration-queue-kilo15-a`  
**Working Directory:** `/workspaces/workflow-orchestration-queue-kilo15-a`  
**Created:** 2026-04-06  
**Status:** ✅ **APPROVED**

---

## 1. Overview

This document defines the execution plan for the `project-setup` dynamic workflow, which initializes the **OS-APOW (Orchestration System for Autonomous Project Orchestration Workflow)** repository for autonomous agentic orchestration.

The workflow transforms this template repository into a fully-configured project environment ready for implementing the headless agentic orchestration platform described in the plan documents.

### Workflow Purpose

Transform the `workflow-orchestration-queue-kilo15-a` template repository into a production-ready project by:

1. Initializing repository settings (GitHub Project, labels, milestones)
2. Creating a comprehensive application plan based on the provided specification documents
3. Establishing the Python project structure with proper scaffolding
4. Documenting agent instructions via AGENTS.md
5. Capturing learnings and execution trace for continuous improvement

---

## 2. Project Context Summary

### Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | OS-APOW (workflow-orchestration-queue) |
| **Purpose** | Headless agentic orchestration platform |
| **Paradigm** | Transforms GitHub Issues into automated execution orders for AI agents |
| **Self-Bootstrapping** | System builds its own Phase 2 and 3 using Phase 1 orchestrator |

### Technology Stack

| Category | Technology |
|----------|------------|
| **Language** | Python 3.12+ |
| **Web Framework** | FastAPI + Uvicorn |
| **Validation** | Pydantic |
| **HTTP Client** | httpx (async) |
| **Package Manager** | uv |
| **Containerization** | Docker / DevContainers |
| **Shell Scripts** | PowerShell Core (pwsh) / Bash |

### Architecture: Four Pillars

1. **The Ear (Work Event Notifier)** - FastAPI webhook receiver for GitHub events
2. **The State (Work Queue)** - GitHub Issues as distributed state ("Markdown as a Database")
3. **The Brain (Sentinel Orchestrator)** - Async polling background service
4. **The Hands (Opencode Worker)** - DevContainer-based execution environment

### Key Architectural Decisions (ADRs)

| ADR | Decision | Rationale |
|-----|----------|-----------|
| **ADR 07** | Shell-Bridge Execution via `devcontainer-opencode.sh` | Environment parity with human developers |
| **ADR 08** | Polling-First Resiliency | Self-healing on restart; webhooks are optimization |
| **ADR 09** | Provider-Agnostic Interface (ITaskQueue) | Future swap to Linear, Jira, etc. |

### Development Phases

| Phase | Name | Description | Status |
|-------|------|-------------|--------|
| **0** | Seeding & Bootstrapping | Manual clone, env setup, plan seeding | 📋 Planned |
| **1** | Sentinel (MVP) | Polling, shell-bridge, status feedback | 📋 Planned |
| **2** | The Ear (Webhook) | FastAPI webhook receiver, triage | 📋 Planned |
| **3** | Deep Orchestration | Hierarchical decomposition, self-healing | 📋 Planned |

### Source Documents in `plan_docs/`

| Document | Purpose |
|----------|---------|
| `OS-APOW Development Plan v4.2.md` | Phased roadmap, user stories, risk assessment |
| `OS-APOW Architecture Guide v3.2.md` | System diagrams, ADRs, data flow, security |
| `OS-APOW Implementation Specification v1.2.md` | Requirements, features, test cases |
| `OS-APOW Simplification Report v1.md` | Applied simplifications (S-1 through S-11) |
| `OS-APOW Plan Review.md` | Strengths analysis, issues, recommendations |
| `orchestrator_sentinel.py` | Reference implementation (292 lines) |
| `notifier_service.py` | Reference implementation (110 lines) |
| `src/models/work_item.py` | Unified data model |
| `src/queue/github_queue.py` | GitHub-backed queue implementation |

### Applied Simplifications (from Simplification Report)

| ID | Simplification | Status |
|----|----------------|--------|
| S-3 | Reduced to 3 env vars (GITHUB_TOKEN, GITHUB_ORG, SENTINEL_BOT_LOGIN) | ✅ Implemented |
| S-4 | Hardcoded ENV_RESET_MODE to "stop" | ✅ Implemented |
| S-5 | Single-repo polling only (Search API deferred) | ✅ Implemented |
| S-6 | Consolidated queue to `src/queue/github_queue.py` | ✅ Implemented |
| S-7 | Removed IPv4 scrubbing pattern | ✅ Implemented |
| S-8 | Removed "encrypted" log verbiage | ✅ Implemented |
| S-9 | Phase 3 features moved to Future Work appendix | ✅ Implemented |
| S-10 | Removed FileHandler (stdout only) | ✅ Implemented |
| S-11 | Removed raw_payload field from WorkItem | ✅ Implemented |

---

## 3. Assignment Execution Plan

### Execution Sequence

| # | Assignment | Goal | Key Acceptance Criteria | Dependencies | Complexity |
|---|------------|------|------------------------|--------------|------------|
| **Pre** | `create-workflow-plan` | Create this execution plan | Plan committed to `plan_docs/workflow-plan.md` | None | Low |
| **1** | `init-existing-repository` | Initialize repo settings | Branch created, GitHub Project linked, labels imported, PR created | Pre complete | Medium |
| **2** | `create-app-plan` | Create comprehensive app plan | Plan issue created, milestones linked, `implementation:ready` label applied | #1 complete | High |
| **3** | `create-project-structure` | Create project scaffolding | pyproject.toml, src/, tests/, Dockerfile, CI/CD foundation | #2 approved | High |
| **4** | `create-agents-md-file` | Create AGENTS.md for AI agents | AGENTS.md at root with validated commands | #3 complete | Medium |
| **5** | `debrief-and-document` | Capture learnings | Debrief report with 12 sections, execution trace saved | #1-4 complete | Medium |
| **Post** | `validate-assignment-completion` | Verify all criteria met | All acceptance criteria verified | #1-5 complete | Low |
| **Post** | `report-progress` | Report workflow completion | Progress reported to orchestrator | Validation pass | Low |

### Assignment Details

#### Pre-Script-Begin: `create-workflow-plan` (This Assignment)

**Goal:** Create a comprehensive workflow execution plan before beginning the main script.

**Acceptance Criteria:**
- [x] Dynamic workflow file read and understood
- [x] All workflow assignments traced and read
- [x] All documents in `plan_docs/` read
- [x] Workflow execution plan produced with required sections
- [ ] Plan committed to `plan_docs/workflow-plan.md`

---

#### Assignment 1: `init-existing-repository`

**Goal:** Initialize repository with GitHub Project, labels, milestones, and working branch.

**Key Steps:**
1. Create branch `dynamic-workflow-project-setup`
2. Create GitHub Project with Board template
3. Import labels from `.github/.labels.json`
4. Rename workspace and devcontainer files to match repo name
5. Create PR from branch to `main`

**Acceptance Criteria:**
- [ ] New branch created (must be first)
- [ ] GitHub Project created and linked
- [ ] Project columns: Not Started, In Progress, In Review, Done
- [ ] Labels imported from `.github/.labels.json`
- [ ] Filenames changed to match project name
- [ ] PR created from branch to `main`

**Verification:** Run `./scripts/test-github-permissions.ps1 -Owner intel-agency`

---

#### Assignment 2: `create-app-plan`

**Goal:** Create a comprehensive application plan based on the specification documents.

**Key Inputs:**
- `plan_docs/OS-APOW Development Plan v4.2.md`
- `plan_docs/OS-APOW Architecture Guide v3.2.md`
- `plan_docs/OS-APOW Implementation Specification v1.2.md`

**Key Steps:**
1. Analyze all plan documents
2. Document tech stack in `plan_docs/tech-stack.md`
3. Document architecture in `plan_docs/architecture.md`
4. Create planning issue using application-plan.md template
5. Create milestones based on phases
6. Link issue to GitHub Project
7. Apply labels: `planning`, `documentation`, `implementation:ready`

**Acceptance Criteria:**
- [ ] Application template analyzed
- [ ] Project structure documented
- [ ] Plan issue created from template
- [ ] All phases with steps listed
- [ ] Risks and mitigations identified
- [ ] Milestones created and linked
- [ ] `implementation:ready` label applied

**Important:** This is PLANNING ONLY - no implementation code.

---

#### Assignment 3: `create-project-structure`

**Goal:** Create the actual Python project structure and scaffolding.

**Tech Stack Adaptation:** Python (uv) - adapt from generic instructions:
- Use `pyproject.toml` instead of `.csproj`
- Use `uv` for dependency management
- Use `src/` layout pattern

**Key Steps:**
1. Create `pyproject.toml` with dependencies
2. Set up `src/os_apow/` package structure
3. Create `tests/` directory with test structure
4. Create `Dockerfile` and `docker-compose.yml`
5. Create `.python-version` for version pinning
6. Set up CI/CD workflow templates
7. Create documentation structure (README.md, docs/)
8. Create `.ai-repository-summary.md`

**Project Structure (Python):**
```
/
├── pyproject.toml
├── uv.lock
├── src/
│   └── os_apow/
│       ├── __init__.py
│       ├── sentinel/
│       ├── notifier/
│       ├── models/
│       └── queue/
├── tests/
│   ├── __init__.py
│   └── test_sentinel.py
├── Dockerfile
├── docker-compose.yml
├── README.md
├── AGENTS.md
└── docs/
```

**Acceptance Criteria:**
- [ ] Solution/project structure created
- [ ] All required directories established
- [ ] Initial configuration files created
- [ ] Basic CI/CD pipeline structure
- [ ] Documentation structure created
- [ ] Development environment validated
- [ ] Initial commit with scaffolding
- [ ] Repository summary created

---

#### Assignment 4: `create-agents-md-file`

**Goal:** Create `AGENTS.md` at repository root for AI coding agent context.

**Key Sections:**
1. Project Overview
2. Setup Commands (install, build, run, test, lint)
3. Project Structure
4. Code Style conventions
5. Testing Instructions
6. Architecture Notes
7. PR and Commit Guidelines
8. Common Pitfalls

**Acceptance Criteria:**
- [ ] AGENTS.md exists at repository root
- [ ] All commands validated by running them
- [ ] Project structure documented
- [ ] Code style conventions listed
- [ ] File committed to working branch

---

#### Assignment 5: `debrief-and-document`

**Goal:** Capture learnings, insights, and execution trace.

**Key Deliverables:**
1. Debrief report with 12 required sections
2. Execution trace document (`debrief-and-document/trace.md`)
3. All deviations from assignment documented

**Report Sections:**
1. Executive Summary
2. Workflow Overview
3. Key Deliverables
4. Lessons Learned
5. What Worked Well
6. What Could Be Improved
7. Errors Encountered and Resolutions
8. Complex Steps and Challenges
9. Suggested Changes
10. Metrics and Statistics
11. Future Recommendations
12. Conclusion

**Acceptance Criteria:**
- [ ] Report created with all 12 sections
- [ ] Report in .md format
- [ ] All deviations documented
- [ ] Report reviewed and approved
- [ ] Report committed to repo
- [ ] Execution trace saved

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROJECT-SETUP DYNAMIC WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  PRE-SCRIPT-BEGIN    │
│  ─────────────────── │
│  create-workflow-plan│ ──► Commit plan_docs/workflow-plan.md
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           MAIN SCRIPT                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────┐                                                │
│  │ 1. init-existing-repo   │                                                │
│  │    ─────────────────    │                                                │
│  │ • Create branch         │                                                │
│  │ • Create GH Project     │                                                │
│  │ • Import labels         │                                                │
│  │ • Create PR             │                                                │
│  └───────────┬─────────────┘                                                │
│              │                                                               │
│              ▼                                                               │
│  ┌─────────────────────────┐                                                │
│  │ 2. create-app-plan      │                                                │
│  │    ─────────────────    │                                                │
│  │ • Analyze plan_docs     │                                                │
│  │ • Create tech-stack.md  │                                                │
│  │ • Create architecture.md│                                                │
│  │ • Create planning issue │                                                │
│  │ • Create milestones     │                                                │
│  │ • Apply impl:ready label│                                                │
│  └───────────┬─────────────┘                                                │
│              │                                                               │
│              ▼                                                               │
│  ┌─────────────────────────┐                                                │
│  │ 3. create-project-struct│                                                │
│  │    ─────────────────    │                                                │
│  │ • Create pyproject.toml │                                                │
│  │ • Create src/ structure │                                                │
│  │ • Create tests/         │                                                │
│  │ • Create Dockerfile     │                                                │
│  │ • Create CI/CD templates│                                                │
│  │ • Create README.md      │                                                │
│  │ • Create .ai-summary.md │                                                │
│  └───────────┬─────────────┘                                                │
│              │                                                               │
│              ▼                                                               │
│  ┌─────────────────────────┐                                                │
│  │ 4. create-agents-md     │                                                │
│  │    ─────────────────    │                                                │
│  │ • Gather project context│                                                │
│  │ • Validate commands     │                                                │
│  │ • Create AGENTS.md      │                                                │
│  │ • Cross-reference docs  │                                                │
│  └───────────┬─────────────┘                                                │
│              │                                                               │
│              ▼                                                               │
│  ┌─────────────────────────┐                                                │
│  │ 5. debrief-and-document │                                                │
│  │    ─────────────────    │                                                │
│  │ • Create 12-section rpt │                                                │
│  │ • Document deviations   │                                                │
│  │ • Save execution trace  │                                                │
│  │ • Commit to repo        │                                                │
│  └───────────┬─────────────┘                                                │
│              │                                                               │
└──────────────┼──────────────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  POST-ASSIGNMENT-COMPLETE    │
│  ──────────────────────────  │
│                              │
│  ┌─────────────────────────┐ │
│  │ validate-assignment-    │ │
│  │ completion              │ │
│  └───────────┬─────────────┘ │
│              │               │
│              ▼               │
│  ┌─────────────────────────┐ │
│  │ report-progress         │ │
│  └─────────────────────────┘ │
│                              │
└──────────────────────────────┘
```

---

## 5. Open Questions

### Resolved Questions

| Question | Resolution |
|----------|------------|
| Tech stack for project structure? | Python 3.12+ with uv package manager (per Implementation Spec) |
| Should Phase 3 features be in MVP spec? | Moved to Future Work appendix (S-9) |
| Connection pooling strategy? | Single httpx.AsyncClient in GitHubQueue.__init__() (I-4/R-5) |

### Questions for Stakeholder Review

| # | Question | Context | Recommendation |
|---|----------|---------|----------------|
| 1 | Package name for `src/`? | Need to decide on Python package name | Use `os_apow` or `workflow_orchestration_queue` |
| 2 | Should existing plan_docs code be moved to src/? | Reference implementations exist in plan_docs/ | Move during create-project-structure, preserving plan_docs as docs |
| 3 | CI/CD platform? | GitHub Actions workflows to create | Use existing .github/workflows/ patterns from template |

---

## 6. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| GitHub API rate limiting during label/project setup | Medium | Low | Use GitHub App installation tokens (5,000 req/hr) |
| Missing environment variables | High | Medium | Validate at startup, crash with clear error message |
| Branch already exists | Low | Low | Check first, delete or use existing |
| Planning issue template mismatch | Medium | Low | Use .github/ISSUE_TEMPLATE/application-plan.md |

---

## 7. Success Criteria

The workflow is considered successful when:

1. ✅ Branch `dynamic-workflow-project-setup` exists with all commits
2. ✅ GitHub Project created and linked to repository
3. ✅ Labels imported from `.github/.labels.json`
4. ✅ Application plan issue created with `implementation:ready` label
5. ✅ Project structure created (pyproject.toml, src/, tests/, Dockerfile)
6. ✅ AGENTS.md exists at repository root with validated commands
7. ✅ Debrief report committed with all 12 sections
8. ✅ PR open from `dynamic-workflow-project-setup` to `main`

---

## 8. Approval

**This workflow execution plan has been reviewed and approved.**

### Approval Checklist

- [x] All assignments understood and sequenced correctly
- [x] Project context accurately captured
- [x] Dependencies identified
- [x] Risks acknowledged
- [x] Open questions noted for resolution

### Stakeholder Approval

**Approved by:** Orchestrator Agent  
**Date:** 2026-04-06  
**Comments:** Plan approved - comprehensive coverage of all assignments with proper sequencing, dependencies, and risk identification

---

*Plan Created:* 2026-04-06  
*Workflow:* project-setup  
*Repository:* intel-agency/workflow-orchestration-queue-kilo15-a
