![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_cachecontrol/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_cachecontrol" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_cachecontrol/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_cachecontrol.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_cachecontrol/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_cachecontrol" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_cachecontrol/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_cachecontrol" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_cachecontrol/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_cachecontrol?label=swarmauri_middleware_cachecontrol&color=green" alt="PyPI - swarmauri_middleware_cachecontrol"/>
    </a>
</p>

---

# Swarmauri Middleware Cachecontrol

Middleware for managing HTTP cache headers and client-side caching behavior.

## Features

- Configurable `max_age` that controls how long clients may cache responses.
- Toggle caching on or off at runtime with the `enabled` flag.
- Adds `Cache-Control`, timestamp-based `ETag`, and `Vary: Accept-Encoding` headers to successful responses.
- Inspects `If-Modified-Since` and `If-None-Match` request headers to short-circuit unchanged responses with `304 Not Modified`.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_middleware_cachecontrol
```

```bash
poetry add swarmauri_middleware_cachecontrol
```

```bash
uv pip install swarmauri_middleware_cachecontrol
```

## Usage

`CacheControlMiddleware` accepts two primary configuration options:

- `max_age`: Maximum cache lifetime (in seconds) communicated to clients. Defaults to `3600`.
- `enabled`: When `False`, the middleware skips all cache headers and lets responses pass through untouched. Defaults to `True`.

When enabled, the middleware injects cache headers into outgoing responses and mirrors conditional request headers to return `304 Not Modified` when the client already has fresh content. Integrate it with FastAPI or Starlette by instantiating the middleware once and delegating to its `dispatch` method from an `@app.middleware("http")` handler.

### Example

The snippet below shows how to register the middleware with FastAPI and inspect the generated headers using `TestClient`:

```python
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from swarmauri_middleware_cachecontrol import CacheControlMiddleware

app = FastAPI()
cache_control = CacheControlMiddleware(max_age=60)


@app.middleware("http")
async def apply_cache_control(request: Request, call_next):
    return await cache_control.dispatch(request, call_next)


@app.get("/status")
def status() -> dict[str, str]:
    return {"state": "fresh"}


def main() -> None:
    client = TestClient(app)
    response = client.get("/status")
    response.raise_for_status()

    print("Cache-Control:", response.headers["Cache-Control"])
    print("ETag:", response.headers["ETag"])
    print("Vary:", response.headers["Vary"])
    print("Payload:", response.json())


if __name__ == "__main__":
    main()
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.
