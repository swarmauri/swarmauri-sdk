![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

Pick the tool that matches your workflow:

```bash
# pip
pip install swarmauri_middleware_stdio

# Poetry
poetry add swarmauri_middleware_stdio

# uv
pip install uv  # install uv if it's not already available
uv add swarmauri_middleware_stdio
```

## Usage

```python
import logging
import sys

from fastapi import FastAPI, Request
from swarmauri_middleware_stdio import StdioMiddleware

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

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

`StdioMiddleware` uses Python's logging facilities under the logger name
`swarmauri_middleware_stdio.StdioMiddleware`. Each request produces an `INFO`
record before the downstream handler runs, and the matching response status is
logged afterwards. Configure logging (as in the example above) to route those
messages to stdout or another destination appropriate for your deployment.

When the middleware is active you should see output similar to:

```
INFO swarmauri_middleware_stdio.StdioMiddleware STDIO Request: GET /
INFO swarmauri_middleware_stdio.StdioMiddleware STDIO Response: 200
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.