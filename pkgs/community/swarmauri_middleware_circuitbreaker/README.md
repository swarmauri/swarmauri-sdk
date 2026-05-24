![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://static.pepy.tech/badge/swarmauri_middleware_circuitbreaker/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_middleware_circuitbreaker/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_middleware_circuitbreaker.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_circuitbreaker" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_circuitbreaker?label=swarmauri_middleware_circuitbreaker&color=green" alt="PyPI - swarmauri_middleware_circuitbreaker"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Middleware Circuit Breaker

`swarmauri_middleware_circuitbreaker` is the Swarmauri middleware component for
protecting unstable request paths with a circuit-breaker policy backed by
`pybreaker`. It is designed for FastAPI-style request middleware and prevents
repeated failures from repeatedly hitting unhealthy downstream services.

## Why Use Swarmauri Middleware Circuit Breaker

- Stop sending traffic to failing upstream dependencies after repeated errors.
- Recover gradually by allowing a single half-open probe request before fully
  reopening traffic.
- Add resilience controls to Swarmauri or FastAPI request flows without writing
  custom breaker logic.
- Pair with retry and observability middleware to build layered failure
  protection.

## FAQ

> **What parameters does this middleware expose?**  
> `fail_max`, `reset_timeout`, and `half_open_wait_time`.

> **What happens when the circuit is open?**  
> The middleware raises HTTP 429 for additional requests until a half-open probe
> is allowed.

> **Is this middleware async?**  
> Yes. The main `dispatch(request, call_next)` entry point is asynchronous.

> **What request type does it expect?**  
> It is written for `fastapi.Request` / Starlette-style HTTP request handling.

## Features

- Circuit-breaker protection using `pybreaker`.
- Async `dispatch(request, call_next)` middleware surface.
- Configurable failure threshold and reset timing.
- Logging for open, half-open, and closed transitions.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_middleware_circuitbreaker
```

```bash
pip install swarmauri_middleware_circuitbreaker
```

## Usage

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
```

## Examples

### Protect an unstable endpoint

```python
from fastapi import FastAPI
from swarmauri_middleware_circuitbreaker import CircuitBreakerMiddleware

app = FastAPI()
app.add_middleware(CircuitBreakerMiddleware, fail_max=5, reset_timeout=30)

@app.get("/unstable")
async def unstable():
    raise RuntimeError("Simulated failure")
```

### Observe circuit transitions in logs

```python
import logging

logging.basicConfig(level=logging.INFO)

# Expected messages include:
# "Circuit half-open: Waiting for test request to determine health"
# "Circuit opened: Excessive failures detected"
# "Circuit closed: Service is healthy again"
```

### Understand open and recovery flow

```python
# Repeated failures increment the internal counter.
# Once the threshold is exceeded, the circuit opens.
# A later request is allowed as a half-open probe.
# Success closes the circuit; failure reopens protection.
```

## Related Packages

- [swarmauri_middleware_ratepolicy](https://pypi.org/project/swarmauri_middleware_ratepolicy/)
- [swarmauri_state_clipboard](https://pypi.org/project/swarmauri_state_clipboard/)
- [swarmauri_middleware_circuitbreaker](https://pypi.org/project/swarmauri_middleware_circuitbreaker/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [FastAPI middleware docs](https://fastapi.tiangolo.com/tutorial/middleware/)
- [pybreaker package information](https://pypi.org/project/pybreaker/)

## Best Practices

- Use targeted circuit breakers around unstable upstream dependencies rather
  than globally around every route.
- Tune `fail_max` and `reset_timeout` per dependency instead of reusing one
  threshold everywhere.
- Pair circuit breaking with retries carefully so one layer does not amplify
  the other.
- Verify your monitoring captures circuit state changes before relying on the
  breaker in production.

## License

This project is licensed under the Apache-2.0 License.

