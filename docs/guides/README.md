# User Guides

This directory contains how-to guides for using the workflow-orchestration-queue system.

## Guides

- [Getting Started](./getting-started.md) - Quick start guide for new users
- [Creating Agent Tasks](./creating-tasks.md) - How to create issues that trigger workflows
- [Local Development](./local-development.md) - Setting up a development environment
- [Docker Deployment](./docker-deployment.md) - Deploying with Docker
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

## Issue Templates

The system recognizes specific issue templates:

| Template Marker | Task Type | Description |
|-----------------|-----------|-------------|
| `[Application Plan]` | `create-app-plan` | Create a new application plan |
| `[Bugfix]` | `analyze-bug` | Analyze and fix a bug |
| `[Task]` | `perform-task` | Perform a specific task |
| `[Feature]` | `perform-task` | Implement a new feature |
| `[Project Structure]` | `create-project-structure` | Create project scaffolding |
