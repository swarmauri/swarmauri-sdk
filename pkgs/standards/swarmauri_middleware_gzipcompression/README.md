![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_middleware_gzipcompression/">
        <img src="https://static.pepy.tech/badge/swarmauri_middleware_gzipcompression/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_gzipcompression/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_gzipcompression.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_gzipcompression/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_gzipcompression/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_gzipcompression" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_gzipcompression/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_gzipcompression?label=swarmauri_middleware_gzipcompression&color=green" alt="PyPI - swarmauri_middleware_gzipcompression"/></a>
</p>
---

# `swarmauri_middleware_gzipcompression`

Middleware for adding gzip compression to FastAPI responses.

## Purpose

This package provides a middleware that automatically compresses outgoing responses using gzip encoding. It ensures that responses are only compressed when supported by the client and when the content type is appropriate for compression.

## Installation

### pip

```bash
pip install swarmauri_middleware_gzipcompression
```

### Poetry

```bash
poetry add swarmauri_middleware_gzipcompression
```

### uv

```bash
uv pip install swarmauri_middleware_gzipcompression
```

## How it works

The middleware mirrors FastAPI's `BaseHTTPMiddleware` contract and can be plugged into an application using the standard `@app.middleware("http")` hook. Compression is only applied when all of the following are true:

- The downstream component returns a `fastapi.Response` (non-`Response` results pass through unchanged).
- The response has a compressible media type such as `application/json` or any `text/*` content type.
- The client opts into compression by sending an `Accept-Encoding` header that includes `gzip`.
- The response is not already marked as gzip encoded.

## Example

The snippet below simulates FastAPI's middleware pipeline and demonstrates how gzip compression is applied when the client opts in to receive gzip-encoded responses.

```python
import asyncio
import gzip
from fastapi import Request, Response

from swarmauri_middleware_gzipcompression import GzipCompressionMiddleware

middleware = GzipCompressionMiddleware()

async def _handle_request() -> None:
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [(b"accept-encoding", b"gzip")],
    }

    async def receive() -> dict:
        return {"type": "http.request", "body": b""}

    request = Request(scope, receive=receive)

    async def call_next(_: Request) -> Response:
        return Response(
            content='{"message":"Hello, gzip!"}',
            media_type="application/json",
        )

    response = await middleware.dispatch(request, call_next)

    assert response.headers.get("Content-Encoding") == "gzip"
    body = gzip.decompress(response.body).decode("utf-8")
    assert body == '{"message":"Hello, gzip!"}'

def run_example() -> None:
    asyncio.run(_handle_request())

if __name__ == "__main__":
    run_example()
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
