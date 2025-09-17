![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_cors/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_cors" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_cors/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_cors.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_cors/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_cors" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_cors/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_cors" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_cors/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_cors?label=swarmauri_middleware_cors&color=green" alt="PyPI - swarmauri_middleware_cors"/>
    </a>
</p>

---

# Swarmauri Middleware CORS

Custom CORS middleware for the Swarmauri framework that integrates with FastAPI applications.

## Features

- Handles CORS preflight (`OPTIONS`) requests directly and returns a `200` response with your configured headers.
- Adds CORS headers to downstream responses produced by your FastAPI routes.
- Rejects requests with a missing `Origin` header or an origin that is not explicitly allowed, returning a `403` response.
- Allows fine-grained control of the exposed headers, allowed methods, credentials support, and cache duration of the CORS policy.

## Installation

### pip

```bash
pip install swarmauri_middleware_cors
```

### Poetry

```bash
poetry add swarmauri_middleware_cors
```

### uv

```bash
uv venv
source .venv/bin/activate  # Use .\.venv\Scripts\activate on Windows
uv add swarmauri_middleware_cors
```

## Usage

Configure the middleware with the exact origins, methods, and headers you want to allow. Origins are matched literally—if you use the default `['*']` setting, every request must send an `Origin: *` header. In practice you should list the concrete origins your frontend sends.

### Python example

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

from swarmauri_middleware_cors import CustomCORSMiddleware

app = FastAPI()

cors = CustomCORSMiddleware(
    allow_origins=["https://frontend.example"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["Authorization"],
    expose_headers=["X-App-Version"],
    max_age=300,
)


@app.middleware("http")
async def apply_custom_cors(request, call_next):
    return await cors.dispatch(request, call_next)


@app.get("/ping")
async def ping():
    return {"status": "ok"}


client = TestClient(app)

if __name__ == "__main__":
    options_response = client.options(
        "/ping", headers={"Origin": "https://frontend.example"}
    )
    print(
        "Allowed origin header:",
        options_response.headers["Access-Control-Allow-Origin"],
    )

    response = client.get(
        "/ping", headers={"Origin": "https://frontend.example"}
    )
    print("Response JSON:", response.json())
```

Running the example prints the allowed origin configured on the middleware and the JSON payload returned by the `GET /ping` route.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.
