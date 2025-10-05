![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_ratepolicy/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_ratepolicy" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_middleware_ratepolicy/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_middleware_ratepolicy.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratepolicy/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_ratepolicy" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratepolicy/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_ratepolicy" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratepolicy/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_ratepolicy?label=swarmauri_middleware_ratepolicy&color=green" alt="PyPI - swarmauri_middleware_ratepolicy"/></a>
</p>

---

# Swarmauri Middleware Ratepolicy

Retry-policy middleware for Swarmauri services. Provides exponential backoff with configurable retry attempts and wait intervals so unreliable upstream calls can be retried transparently.

## Features

- Implements Swarmauri's `MiddlewareBase` contract; wrap any callable sequence (FastAPI routes, job runners, etc.).
- Configurable `max_retries` and `initial_wait` seconds. Wait time doubles on each retry (`initial_wait * 2**attempt`).
- Emits structured logs on retry attempts and successes for observability.
- Simple synchronous dispatch; wrap async callables by providing a sync shim that executes the coroutine (see example below).

## Prerequisites

- Python 3.10 or newer.
- A Swarmauri application or FastAPI project that supports middleware registration.

## Installation

```bash
# pip
pip install swarmauri_middleware_ratepolicy

# poetry
poetry add swarmauri_middleware_ratepolicy

# uv (pyproject-based projects)
uv add swarmauri_middleware_ratepolicy
```

## Quickstart

```python
import logging
from swarmauri_middleware_ratepolicy import RetryPolicyMiddleware

logging.basicConfig(level=logging.INFO)

retry_middleware = RetryPolicyMiddleware(max_retries=3, initial_wait=0.5)

class RequestEnvelope:
    def __init__(self, payload: str):
        self.payload = payload

request = RequestEnvelope("work-item-123")

def call_next(req: RequestEnvelope):
    raise RuntimeError("Simulated upstream failure")

retry_middleware.dispatch(request, call_next)
```

With Swarmauri's middleware stack (or FastAPI), register it just like other Swarmauri middleware:

```python
from swarmauri_app.middleware import middleware_stack
from swarmauri_middleware_ratepolicy import RetryPolicyMiddleware

middleware_stack.add_middleware(
    RetryPolicyMiddleware,
    max_retries=4,
    initial_wait=0.25,
)
```

## Example: Wrapping an External API Call

```python
import logging
import requests
from swarmauri_middleware_ratepolicy import RetryPolicyMiddleware

logging.basicConfig(level=logging.INFO)

retry = RetryPolicyMiddleware(max_retries=4, initial_wait=0.25)

class RequestWrapper:
    def __init__(self, url: str):
        self.url = url

wrapper = RequestWrapper("https://api.example.com/data")

response = retry.dispatch(
    wrapper,
    lambda req: requests.get(req.url, timeout=5),
)
print(response.status_code)
```

## Tips

- Keep `max_retries` small for user-facing endpoints to avoid long wait chains; rely on background queues for bulk retries.
- Combine with the circuit breaker middleware for layered resilience (circuit breaker opens when repeated retries fail).
- When wrapping async callables, convert them to sync functions using `asyncio.run` or `anyio.from_thread` to fit the middleware signature.
- Capture logs at INFO level to trace retry attempts in production.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
