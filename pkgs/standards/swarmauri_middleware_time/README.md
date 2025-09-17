![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_time/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_time" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_time/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_time.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_time/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_time" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_time/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_time" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_time/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_time?label=swarmauri_middleware_time&color=green" alt="PyPI - swarmauri_middleware_time"/>
    </a>
</p>

---

# Swarmauri Middleware Time

Middleware for tracking request processing time in Swarmauri applications.

## Features

- Logs when each request starts and when it completes using Python's `logging` module.
- Measures the total time spent handling a request and attaches `X-Request-Duration`
  and `X-Request-Start-Time` headers to the response.
- Raises an `HTTPException` with status code `500` if an unexpected error occurs
  while the downstream handler is executing.

## Installation

### pip

```bash
pip install swarmauri_middleware_time
```

### Poetry

```bash
poetry add swarmauri_middleware_time
```

### uv

```bash
# Install uv if it is not already available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add the middleware to your project
uv add swarmauri_middleware_time
```

## Usage

The middleware exposes a standard `dispatch` method that matches FastAPI's middleware
interface. Instantiate it once and forward requests through `dispatch` inside an
`@app.middleware("http")` hook:

```python
from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from swarmauri_middleware_time import TimerMiddleware

app = FastAPI()
timer_middleware = TimerMiddleware()


@app.middleware("http")
async def add_timer(request: Request, call_next):
    return await timer_middleware.dispatch(request, call_next)


@app.get("/ping")
async def ping():
    return {"message": "pong"}


if __name__ == "__main__":
    client = TestClient(app)
    response = client.get("/ping")

    assert response.json() == {"message": "pong"}
    assert "X-Request-Duration" in response.headers
    assert float(response.headers["X-Request-Duration"]) >= 0.0
    assert "X-Request-Start-Time" in response.headers

    print("Duration header:", response.headers["X-Request-Duration"])
    print("Start time header:", response.headers["X-Request-Start-Time"])
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
