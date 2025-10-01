![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_circuitbreaker" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_middleware_circuitbreaker/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_middleware_circuitbreaker.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_circuitbreaker" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_circuitbreaker" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_circuitbreaker?label=swarmauri_middleware_circuitbreaker&color=green" alt="PyPI - swarmauri_middleware_circuitbreaker"/></a>
</p>

---

# Swarmauri Middleware Circuitbreaker

FastAPI middleware that adds a configurable circuit breaker (powered by `pybreaker`) to Swarmauri services. Automatically blocks requests after repeated failures and re-opens based on a half-open probation window.

## Features

- Integrates with Swarmauri's `MiddlewareBase` interface—drop in via `app.add_middleware`.
- Configurable thresholds: `fail_max`, `reset_timeout`, and `half_open_wait_time`.
- Supports async FastAPI request handling and conveys 429 responses when the circuit is open.
- Logs state transitions (closed ➜ open ➜ half-open) for observability.

## Prerequisites

- Python 3.10 or newer.
- FastAPI application (ASGI) using Swarmauri's middleware system.
- `pybreaker` installed (included as a dependency of this package).

## Installation

```bash
# pip
pip install swarmauri_middleware_circuitbreaker

# poetry
poetry add swarmauri_middleware_circuitbreaker

# uv (pyproject-based projects)
uv add swarmauri_middleware_circuitbreaker
```

## Quickstart

```python
from fastapi import FastAPI
from swarmauri_middleware_circuitbreaker import CircuitBreakerMiddleware

app = FastAPI()

app.add_middleware(
    CircuitBreakerMiddleware,
    fail_max=5,
    reset_timeout=30,
    half_open_wait_time=10,
)

@app.get("/unstable")
async def unstable_endpoint():
    raise RuntimeError("Simulated failure")
```

- After 5 failures (`fail_max=5`), the circuit opens and subsequent calls receive HTTP 429.
- After `reset_timeout` seconds, a single test request is allowed in the half-open state; success closes the circuit, failure keeps it open.

## Observing the Circuit

```python
import logging

logging.basicConfig(level=logging.INFO)

# Logs include:
# "Circuit half-open: Waiting for test request to determine health"
# "Circuit opened: Excessive failures detected"
# "Circuit closed: Service is healthy again"
```

Integrate with your logging/monitoring stack to alert on circuit state changes.

## Tips

- Use targeted middleware stacks; wrap only the routes that call upstream services prone to failure.
- Tune `fail_max` and `reset_timeout` for each dependency—critical paths may require conservative thresholds.
- Pair with retry logic or queueing to degrade gracefully while the circuit is open.
- When testing locally, trigger failures intentionally to ensure your observability tracks circuit transitions correctly.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
