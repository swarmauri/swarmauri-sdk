![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_jwt/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_jwt" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jwt/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jwt.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jwt/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_jwt" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jwt/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_jwt" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jwt/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_jwt?label=swarmauri_middleware_jwt&color=green" alt="PyPI - swarmauri_middleware_jwt"/>
    </a>
</p>

---

# Swarmauri Middleware JWT

`JWTMiddleware` validates JSON Web Tokens (JWT) issued to FastAPI-based
Swarmauri services. The middleware expects a ``Bearer`` token in the
``Authorization`` header, decodes it with the configured secret and algorithm,
and stores the decoded payload on ``request.state.jwt_payload``. Requests with
missing or invalid tokens receive an HTTP 401 response.

## Installation

### pip

```bash
pip install swarmauri_middleware_jwt
```

### Poetry

```bash
poetry add swarmauri_middleware_jwt
```

### uv

```bash
# Install uv (see https://docs.astral.sh/uv/) if it is not already available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Use uv to add the middleware to your environment
uv pip install swarmauri_middleware_jwt
```

## Example

The example below attaches ``JWTMiddleware`` to a FastAPI application, issues a
token using ``PyJWT``, and performs a request that reads the decoded payload
from ``request.state``.

```python
from fastapi import FastAPI, Request
from starlette.testclient import TestClient
import jwt

from swarmauri_middleware_jwt import JWTMiddleware


SECRET_KEY = "change-me"

app = FastAPI()

# Register the middleware with the FastAPI app
jwt_middleware = JWTMiddleware(secret_key=SECRET_KEY)
app.middleware("http")(jwt_middleware.dispatch)


@app.get("/protected")
async def protected_route(request: Request):
    return {"subject": request.state.jwt_payload["sub"]}


def run_example() -> dict:
    token = jwt.encode({"sub": "demo-user"}, SECRET_KEY, algorithm="HS256")
    client = TestClient(app)
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print(run_example())
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.