![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_session/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_session" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_session/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_session.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_session/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_session" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_session/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_session" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_session/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_session?label=swarmauri_middleware_session&color=green" alt="PyPI - swarmauri_middleware_session"/>
    </a>
</p>

---

# Swarmauri Middleware Session

Session middleware for FastAPI and Starlette style applications that keeps a
lightweight, in-memory session store synchronized with every request and
response.

## Overview

- Accepts an incoming session identifier from the `X-Session-ID` request header
  (customisable through `session_header`).
- Falls back to generating a new UUID session identifier and persists it on the
  response when none is supplied.
- Stores per-session data in `session_storage`, allowing subsequent requests to
  reuse state keyed by the same identifier.
- Writes the active session id to `request.state.session_id` and mirrors it in
  the `session_id` response cookie (customisable through `session_cookie`).
- Uses a configurable `max_age` to control the lifetime of the emitted cookie.

## Installation

Install from PyPI using the toolchain that fits your workflow.

### pip

```bash
pip install swarmauri_middleware_session
```

### Poetry

```bash
poetry add swarmauri_middleware_session
```

### uv

```bash
uv venv
source .venv/bin/activate
uv pip install swarmauri_middleware_session
```

## Example

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from swarmauri_middleware_session import SessionMiddleware


app = FastAPI()
session_middleware = SessionMiddleware()


@app.middleware("http")
async def attach_session(request: Request, call_next):
    return await session_middleware.dispatch(request, call_next)


@app.get("/greet")
async def greet(request: Request):
    session_id = request.state.session_id
    session_data = session_middleware.session_storage.setdefault(session_id, {})
    session_data["visits"] = session_data.get("visits", 0) + 1
    return JSONResponse({"session_id": session_id, "visits": session_data["visits"]})


client = TestClient(app)

first_response = client.get("/greet")
first_data = first_response.json()

second_response = client.get(
    "/greet", headers={"X-Session-ID": first_response.headers["X-Session-ID"]}
)
second_data = second_response.json()

print(first_data)
print(second_data)
```

Running the example prints the initial visit count followed by an incremented
visit count for the same session, demonstrating how the middleware keeps track
of state across requests.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
