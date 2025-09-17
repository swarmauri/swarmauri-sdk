![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_bulkhead" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_bulkhead/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_bulkhead.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_bulkhead" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_bulkhead" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_bulkhead?label=swarmauri_middleware_bulkhead&color=green" alt="PyPI - swarmauri_middleware_bulkhead"/>
    </a>
</p>

---

# Swarmauri Middleware Bulkhead

Concurrency isolation middleware for FastAPI applications. Limit the number of simultaneous requests to protect resources from overload and ensure reliable service operation.

## Features

- **Concurrency control** restricts the number of in-flight requests using an `asyncio.Semaphore`.
- **Configurable limits** let you tune `max_concurrency` (default: 10) to match service capacity.
- **Fail-fast validation** guards against non-positive concurrency limits at initialization.
- **Structured logging** surfaces request flow and failure details for easier diagnostics.
- **FastAPI compatibility** enables seamless integration into ASGI middleware stacks.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_middleware_bulkhead

# Poetry
poetry add swarmauri_middleware_bulkhead

# uv
uv add swarmauri_middleware_bulkhead
```

## Quickstart

The middleware wraps a `call_next` handler and ensures that no more than `max_concurrency` requests execute at once. Run the example below with `python quickstart.py` to see the concurrency ceiling in action.

```python
import asyncio

from fastapi import Request

from swarmauri_middleware_bulkhead import BulkheadMiddleware


async def main() -> None:
    bulkhead = BulkheadMiddleware(max_concurrency=2)
    active_requests = 0
    peak_active_requests = 0
    lock = asyncio.Lock()

    async def call_next(request: Request):
        nonlocal active_requests, peak_active_requests
        async with lock:
            active_requests += 1
            peak_active_requests = max(peak_active_requests, active_requests)

        try:
            await asyncio.sleep(0.05)
            return {"path": request.scope.get("path"), "handled": True}
        finally:
            async with lock:
                active_requests -= 1

    async def simulate_request(idx: int):
        request = Request(scope={"type": "http", "path": f"/task/{idx}"})
        return await bulkhead.dispatch(request, call_next)

    responses = await asyncio.gather(*(simulate_request(i) for i in range(5)))

    assert peak_active_requests <= bulkhead.max_concurrency
    print("Peak concurrent requests:", peak_active_requests)
    print("Responses:", responses)


if __name__ == "__main__":
    asyncio.run(main())
```

## For Contributors

If you want to contribute to `swarmauri_middleware_bulkhead`, please read our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and [style guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/STYLE_GUIDE.md).

