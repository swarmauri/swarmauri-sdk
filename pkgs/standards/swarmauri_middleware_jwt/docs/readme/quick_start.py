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
