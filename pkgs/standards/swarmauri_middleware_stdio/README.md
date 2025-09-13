![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_stdio/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_stdio" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_stdio/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_stdio.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_stdio/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_stdio" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_stdio/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_stdio" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_stdio/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_stdio?label=swarmauri_middleware_stdio&color=green" alt="PyPI - swarmauri_middleware_stdio"/>
    </a>
</p>

---

# Swarmauri Middleware Stdio

`swarmauri_middleware_stdio` provides a lightweight FastAPI middleware that
logs incoming requests and outgoing responses to standard output using
Python's logging module. It is handy for development and debugging when a
full logging stack is unnecessary.

## Installation

```bash
pip install swarmauri_middleware_stdio
```

## Usage

```python
from fastapi import FastAPI, Request
from swarmauri_middleware_stdio import StdioMiddleware

app = FastAPI()
stdio = StdioMiddleware()

@app.middleware("http")
async def log_to_stdout(request: Request, call_next):
    return await stdio.dispatch(request, call_next)

@app.get("/")
async def hello() -> dict[str, str]:
    return {"message": "hello"}
```

## How It Works

The middleware reports the HTTP method and path of each request and logs the
resulting response status code. All messages are emitted at the `INFO` level
and written to stdout.
