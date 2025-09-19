![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_exceptionhandling/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_exceptionhandling" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_exceptionhandling/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_exceptionhandling.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_exceptionhandling/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_exceptionhandling" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_exceptionhandling/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_exceptionhandling" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_exceptionhandling/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_exceptionhandling?label=swarmauri_middleware_exceptionhandling&color=green" alt="PyPI - swarmauri_middleware_exceptionhandling"/>
    </a>
</p>

---

# Swarmauri Middleware Exception Handling

Centralized exception and error handling for Swarmauri applications built on FastAPI.

## Features

- Wraps unhandled exceptions in a consistent JSON payload with the error type,
  message, and a UTC timestamp.
- Logs request metadata (method, path, and headers) alongside the stack trace to
  simplify troubleshooting.
- Registers through the Swarmauri component system and can be attached to any
  FastAPI application via `app.middleware("http")`.

## Installation

Pick the workflow that matches your project:

```bash
pip install swarmauri_middleware_exceptionhandling
```

```bash
poetry add swarmauri_middleware_exceptionhandling
```

```bash
uv pip install swarmauri_middleware_exceptionhandling
# or, inside a uv project
uv add swarmauri_middleware_exceptionhandling
```

## Usage

Attach the middleware to convert uncaught exceptions into the structured error
response returned by Swarmauri services.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

from swarmauri_middleware_exceptionhandling import ExceptionHandlingMiddleware

app = FastAPI()
app.middleware("http")(ExceptionHandlingMiddleware())


@app.get("/boom")
async def boom():
    raise RuntimeError("Boom!")


client = TestClient(app)
response = client.get("/boom")
assert response.status_code == 500
print(response.json())
```

The JSON payload produced by the middleware includes the error type, message,
and a timestamp similar to the following:

```json
{
  "error": {
    "type": "Unhandled Exception",
    "message": "Boom!",
    "timestamp": "2024-05-01T12:34:56.789012"
  }
}
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.
