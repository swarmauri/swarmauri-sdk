![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri JWT Middleware

`swarmauri_middleware_jwt` is the ASGI adapter for authenticating compact JWT
Bearer credentials. It delegates JWS verification to `swarmauri_signing_jws`
and framework-neutral claim policy to `swarmauri_tokens_jwt`.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_middleware_jwt)](https://pepy.tech/projects/swarmauri_middleware_jwt)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jwt.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jwt/)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_middleware_jwt/)
[![License](https://img.shields.io/pypi/l/swarmauri_middleware_jwt)](https://pypi.org/project/swarmauri_middleware_jwt/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_middleware_jwt)](https://pypi.org/project/swarmauri_middleware_jwt/)

## Features

- Extracts RFC 6750-style Bearer credentials without coupling extraction to
  token semantics.
- Verifies compact HMAC JWS signatures with an explicit algorithm allowlist.
- Applies reusable JWT policy for temporal, issuer, audience, required-claim,
  scope, and role validation.
- Stores authenticated claims on a configurable request-state attribute.
- Supports synchronous manual verification and asynchronous middleware flows.
- Uses Starlette request and exception contracts and works with FastAPI.

## Installation

```bash
uv add swarmauri_middleware_jwt
```

```bash
pip install swarmauri_middleware_jwt
```

## Usage

```python
import asyncio
import time

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_middleware_jwt import JWTMiddleware
from swarmauri_signing_jws import JwsSignerVerifier

SECRET = "replace-with-at-least-32-secret-bytes"

async def protected(request: Request) -> JSONResponse:
    return JSONResponse({"subject": request.state.jwt_payload["sub"]})


routes = Starlette(routes=[Route("/protected", protected)])
jwt_middleware = JWTMiddleware(
    secret_key=SECRET,
    app=routes,
    issuer="https://identity.example.com",
    audience="swarmauri-api",
    required_claims={"sub", "iat", "exp"},
)
app = jwt_middleware


async def issue_example_token() -> str:
    now = int(time.time())
    return await JwsSignerVerifier().sign_compact(
        payload={
            "sub": "demo-user",
            "iat": now,
            "exp": now + 300,
            "iss": "https://identity.example.com",
            "aud": "swarmauri-api",
        },
        alg=JWAAlg.HS256,
        key={"kind": "raw", "key": SECRET, "alg": "HS256"},
        typ="JWT",
    )


token = asyncio.run(issue_example_token())
assert jwt_middleware.verify_token(token)["sub"] == "demo-user"
```

For asymmetric keys or managed key providers, use
`swarmauri_tokens_jwt.JWTTokenService` and pass an appropriate verifier into
your application boundary.

## Contributing

See the repository [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).
