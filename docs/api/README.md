# API Documentation

This directory contains API documentation for the workflow-orchestration-queue system.

## Endpoints

### Notifier Service (The Ear)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check endpoint |
| GET | `/ready` | Readiness check endpoint |
| POST | `/webhooks/github` | GitHub webhook receiver |

## OpenAPI Documentation

When running the notifier service, access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Webhook Events

### Supported Events

| Event | Action | Description |
|-------|--------|-------------|
| `issues` | `opened`, `edited`, `labeled` | Issue events |
| `issue_comment` | `created` | Comment events |
| `pull_request` | `opened`, `synchronize` | Pull request events |

### Webhook Verification

All webhook requests must include a valid `X-Hub-Signature-256` header.

```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```
