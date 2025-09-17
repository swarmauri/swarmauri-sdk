![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_httpsig/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_httpsig" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_httpsig/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_httpsig.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_httpsig/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_httpsig" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_httpsig/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_httpsig" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_httpsig/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_httpsig?label=swarmauri_middleware_httpsig&color=green" alt="PyPI - swarmauri_middleware_httpsig"/>
    </a>
</p>

---

# Swarmauri Middleware HttpSig

`HttpSigMiddleware` verifies a base64-encoded HMAC-SHA256 signature on every
incoming request body. The middleware compares the provided signature (default
header `X-Signature`) with one generated from the request payload using a
shared secret. Missing or incorrect signatures are rejected with `401`.

## Features

- Validates request payloads with an HMAC-SHA256 digest
- Uses constant-time comparisons to mitigate timing attacks
- Configurable signature header via the `header_name` argument
- Logs and rejects requests that do not supply a valid signature

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_middleware_httpsig

# Poetry
poetry add swarmauri_middleware_httpsig

# uv
uv add swarmauri_middleware_httpsig
```

## Example

The snippet below wires the middleware into FastAPI via the `@app.middleware`
decorator, signs a request body, and demonstrates the `401` response that
occurs when a tampered signature is supplied. The middleware raises
`HTTPException`, so the example also converts those errors to JSON responses.

```python
import base64
import hashlib
import hmac
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from swarmauri_middleware_httpsig import HttpSigMiddleware


app = FastAPI()
http_sig = HttpSigMiddleware(secret_key="supersecret")


@app.middleware("http")
async def verify_signature(request: Request, call_next):
    try:
        return await http_sig.dispatch(request, call_next)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.post("/echo")
async def echo(payload: dict) -> dict:
    return payload


def create_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


if __name__ == "__main__":
    client = TestClient(app)

    body = json.dumps({"message": "hello"}).encode()
    signature = create_signature("supersecret", body)

    ok = client.post(
        "/echo",
        data=body,
        headers={
            "X-Signature": signature,
            "Content-Type": "application/json",
        },
    )
    assert ok.status_code == 200
    print("Verified response:", ok.json())

    bad = client.post(
        "/echo",
        data=body,
        headers={
            "X-Signature": "tampered",
            "Content-Type": "application/json",
        },
    )
    assert bad.status_code == 401
    print("Unauthorized status:", bad.status_code)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.
