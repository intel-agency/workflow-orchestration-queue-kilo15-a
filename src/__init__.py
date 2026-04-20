"""Workflow Orchestration Queue - Headless Agentic Orchestration Platform.

This package provides a headless agentic orchestration platform that transforms
GitHub Issues into autonomous execution orders. It implements a 4-pillar architecture:

- The Ear (notifier_service.py): FastAPI webhook receiver for secure event ingestion
- The State (GitHub Issues): Queue storage using "Markdown as a Database"
- The Brain (orchestrator_sentinel.py): Background polling and dispatch service
- The Hands (opencode worker): DevContainer-based LLM agent execution
"""

__version__ = "0.1.0"
__author__ = "Intel Agency"
