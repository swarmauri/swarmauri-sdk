![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_auth/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_auth" alt="PyPI - Downloads"/>
    </a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri_middleware_auth">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri_middleware_auth&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_auth/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_auth" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_auth/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_auth" alt="PyPI - License"/>
    </a>
    <br />
    <a href="https://pypi.org/project/swarmauri_middleware_auth/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_auth?label=swarmauri_middleware_auth&color=green" alt="PyPI - swarmauri_middleware_auth"/>
    </a>
</p>

---

# `swarmauri_middleware_auth`

JWT authentication middleware for Swarmauri and FastAPI applications.

## Features

- Accepts HTTP `Authorization` headers with `Bearer` tokens and rejects
  missing or malformed credentials with a `401` response.
- Verifies JWT signatures through `swarmauri_signing_jws.JwsSignerVerifier`
  using the configured secret and algorithm (default `HS256`).
- Enforces expiration by default and can optionally require matching
  audience (`aud`) and issuer (`iss`) claims.
- Requires `sub` and `iat` claims and exposes
  `_validate_custom_claims` for additional validation logic.
- Stores the decoded payload on `request.state.user` for downstream
  handlers.
- Provides a `verify_token_manually` utility to inspect tokens outside of
  the middleware lifecycle.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_middleware_auth
```

```bash
poetry add swarmauri_middleware_auth
```

```bash
uv pip install swarmauri_middleware_auth
```

## Configuration

`AuthMiddleware` accepts the following arguments:

- `secret_key` (**required**) – shared secret used to validate
  HMAC-signed JWTs (must be at least 32 bytes for HMAC algorithms).
- `algorithm` (default `"HS256"`) – JWT algorithm identifier supported by
  `swarmauri_signing_jws`.
- `verify_exp` (default `True`) – toggle to enforce the `exp` claim.
- `verify_aud` (default `False`) – toggle to enforce the `aud` claim
  matches the provided `audience`.
- `audience` – expected `aud` claim when `verify_aud` is enabled.
- `issuer` – expected `iss` claim.
- Additional keyword arguments are forwarded to `MiddlewareBase`.

Tokens missing required claims (`sub`, `iat`) or failing any validation
step raise an `HTTPException` with a `401` status code.

## Usage

Instantiate `AuthMiddleware` and delegate to its `dispatch` coroutine from a
FastAPI middleware hook. Use FastAPI's HTTP exception handler to translate
authentication failures into proper responses:

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler

from swarmauri_middleware_auth import AuthMiddleware

SECRET_KEY = "supersecret-key-with-32-bytes-min!"
ISSUER = "my-service"
AUDIENCE = "my-audience"

auth_middleware = AuthMiddleware(
    secret_key=SECRET_KEY,
    issuer=ISSUER,
    audience=AUDIENCE,
    verify_aud=True,
)

app = FastAPI()


@app.middleware("http")
async def auth_guard(request: Request, call_next):
    try:
        return await auth_middleware.dispatch(request, call_next)
    except HTTPException as exc:
        return await http_exception_handler(request, exc)


@app.get("/protected")
async def protected(request: Request):
    return {"subject": request.state.user["sub"]}
```

## Issuing tokens for local testing

The middleware expects tokens to include `sub`, `iat`, and (by default)
`exp`. The snippet below produces a short-lived token compatible with the
configuration above:

```python
import asyncio
import time

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_signing_jws import JwsSignerVerifier

SECRET_KEY = "supersecret-key-with-32-bytes-min!"
ISSUER = "my-service"
AUDIENCE = "my-audience"


async def issue_token() -> str:
    signer = JwsSignerVerifier()
    return await signer.sign_compact(
        payload={
            "sub": "user123",
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,
            "aud": AUDIENCE,
            "iss": ISSUER,
        },
        alg=JWAAlg.HS256,
        key={"kind": "raw", "key": SECRET_KEY, "alg": "HS256"},
        typ="JWT",
    )


token = asyncio.run(issue_token())
```

## Custom claim validation

Override `_validate_custom_claims` to enforce additional rules. Raise
`InvalidTokenError` when a token should be rejected:

```python
from swarmauri_middleware_auth import AuthMiddleware, InvalidTokenError


class RoleCheckingMiddleware(AuthMiddleware):
    def _validate_custom_claims(self, payload: dict) -> None:
        super()._validate_custom_claims(payload)
        if payload.get("role") != "admin":
            raise InvalidTokenError("Admin role is required")
```

## Manual verification helper

Use `verify_token_manually` to synchronously inspect tokens without FastAPI
middleware plumbing. The method returns the decoded payload when valid and
`None` otherwise.

## Want to help?

If you want to contribute to swarmauri-sdk, read our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).

