![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_jsonrpc" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jsonrpc/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jsonrpc.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_jsonrpc" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_jsonrpc" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_jsonrpc?label=swarmauri_middleware_jsonrpc&color=green" alt="PyPI - swarmauri_middleware_jsonrpc"/>
    </a>
</p>

---

# Swarmauri Middleware JsonRpc

Middleware that performs simple validation of JSON-RPC requests.

## Features

- Validates JSON request bodies for JSON-RPC payloads when the
  `Content-Type` header starts with `application/json`.
- Returns `400 Bad Request` with a plain-text error when the body contains
  invalid JSON.
- Ensures JSON object payloads define a `jsonrpc` field, responding with
  `400 Bad Request` if it is missing.

## Installation

Install the middleware with your preferred Python packaging workflow:

```bash
pip install swarmauri_middleware_jsonrpc
```

```bash
poetry add swarmauri_middleware_jsonrpc
```

```bash
uv add swarmauri_middleware_jsonrpc
```

```bash
uv pip install swarmauri_middleware_jsonrpc
```

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_jsonrpc import JsonRpcMiddleware

app = FastAPI()
app.middleware("http")(JsonRpcMiddleware().dispatch)
```

The middleware integrates with FastAPI's `app.middleware("http")` hook and is
compatible with the `MiddlewareBase` ecosystem.  Once registered, every incoming
JSON request is validated before reaching subsequent middleware or route
handlers.

## Request Validation

- Requests without an `application/json` content type bypass the middleware.
- Malformed JSON bodies are rejected with a `400` response containing the
  message `Invalid JSON`.
- JSON objects missing the `jsonrpc` key are rejected with a `400` response and
  the message `Missing jsonrpc field`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.