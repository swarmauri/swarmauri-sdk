![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_logging/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_logging" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_logging/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_logging.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_logging/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_logging" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_logging/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_logging" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_logging/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_logging?label=swarmauri_middleware_logging&color=green" alt="PyPI - swarmauri_middleware_logging"/>
    </a>
</p>

---

# Swarmauri Middleware Logging

HTTP middleware for logging requests and responses in Swarmauri and FastAPI applications.

## Features

- Logs the HTTP method and path for each incoming request.
- Captures request headers and attempts to parse JSON bodies for inspection.
- Emits a warning when the request body cannot be decoded as JSON.
- Measures total processing time and records the response status code.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_middleware_logging
```

```bash
poetry add swarmauri_middleware_logging
```

```bash
uv pip install swarmauri_middleware_logging
```

```bash
uv add swarmauri_middleware_logging
```

## Example

```python
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from swarmauri_middleware_logging import LoggingMiddleware

app = FastAPI()
logging_middleware = LoggingMiddleware()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    return await logging_middleware.dispatch(request, call_next)


@app.post("/echo")
async def echo(payload: dict):
    return payload


client = TestClient(app)
print(client.post("/echo", json={"message": "hello"}).json())
```

Running the example prints the echoed payload and produces INFO-level log entries for the request and response lifecycle.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.
