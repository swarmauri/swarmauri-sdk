![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_ratelimit/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_ratelimit" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_ratelimit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_ratelimit.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratelimit/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_ratelimit" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratelimit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_ratelimit" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratelimit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_ratelimit?label=swarmauri_middleware_ratelimit&color=green" alt="PyPI - swarmauri_middleware_ratelimit"/>
    </a>
</p>

---

# Swarmauri Middleware Ratelimit

Flexible rate limiting middleware for Swarmauri applications.

This package provides a drop-in FastAPI middleware that throttles requests
based on the client IP address or an authentication token. It is useful for
preventing abuse of public APIs or protecting upstream services from bursts of
traffic.

## Features

- Configurable request limit and time window that defaults to ``100`` requests
  per ``60`` seconds.
- Tracks callers by IP address or a custom authentication token header.
- Maintains in-memory counters that reset automatically after the configured
  time window.
- Returns FastAPI ``Response`` objects with HTTP ``429`` status codes when the
  limit is exceeded.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_middleware_ratelimit

# Poetry
poetry add swarmauri_middleware_ratelimit

# uv
uv add swarmauri_middleware_ratelimit
```

## Usage

### Basic IP-based limiting

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from swarmauri_middleware_ratelimit import RateLimitMiddleware

app = FastAPI()
rate_limiter = RateLimitMiddleware(rate_limit=2, time_window=60)


@app.middleware("http")
async def limit_requests(request, call_next):
    return await rate_limiter.dispatch(request, call_next)


@app.get("/ping")
async def ping():
    return {"status": "ok"}


client = TestClient(app)

assert client.get("/ping").status_code == 200
assert client.get("/ping").status_code == 200
assert client.get("/ping").status_code == 429
```

In this example the first two requests succeed because they fall inside the
allowed limit. A third request within the same 60-second window exceeds the
threshold and the middleware immediately returns a ``429`` response with the
body ``"Rate limit exceeded"``. The middleware instance keeps request counters
in memory, so you should create one instance per application process.

### Token-based rate limiting

```python
# Use the value of the `X-Api-Key` header to track clients instead of IP
rate_limiter = RateLimitMiddleware(
    rate_limit=100,
    time_window=60,
    use_token=True,
    token_header="X-Api-Key",
)


@app.middleware("http")
async def limit_requests(request, call_next):
    return await rate_limiter.dispatch(request, call_next)
```

When ``use_token`` is ``True`` the middleware looks for the configured header on
every request and raises a ``ValueError`` if it is missing. This makes it safe
to enforce API key or bearer token quotas even when requests are routed through
shared proxies. Reuse the same middleware instance across requests to ensure
counters continue to accumulate across calls.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
