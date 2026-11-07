from unittest.mock import AsyncMock, Mock

import pytest
from starlette.exceptions import HTTPException
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_middleware_jwt import BearerTokenExtractor, JWTMiddleware
from swarmauri_signing_jws import JwsSignerVerifier

SECRET = "correct-secret-with-at-least-32-bytes"
OTHER_SECRET = "different-secret-with-at-least-32-bytes"


async def _token(secret: str, **claims: object) -> str:
    return await JwsSignerVerifier().sign_compact(
        payload=claims,
        alg=JWAAlg.HS256,
        key={"kind": "raw", "key": secret, "alg": "HS256"},
        typ="JWT",
    )


@pytest.mark.unit
def test_bearer_extractor_is_case_insensitive() -> None:
    extractor = BearerTokenExtractor()
    assert extractor.extract({"Authorization": "bearer token"}) == "token"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_valid_token() -> None:
    token = await _token(
        SECRET, sub="user", iat=100, exp=4_000_000_000, aud="api"
    )
    middleware = JWTMiddleware(
        secret_key=SECRET,
        audience="api",
        required_claims={"sub", "iat", "exp"},
    )
    request = Mock(spec=Request)
    request.headers = {"Authorization": f"Bearer {token}"}
    request.state = Mock()
    call_next = AsyncMock(return_value="ok")

    result = await middleware.dispatch(request, call_next)

    assert result == "ok"
    assert request.state.jwt_payload["sub"] == "user"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_rejects_missing_header() -> None:
    middleware = JWTMiddleware(secret_key=SECRET)
    request = Mock(spec=Request)
    request.headers = {}
    request.state = Mock()
    call_next = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await middleware.dispatch(request, call_next)

    assert exc_info.value.status_code == 401
    call_next.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_rejects_invalid_signature_and_claims() -> None:
    bad_signature = await _token(OTHER_SECRET, sub="user")
    middleware = JWTMiddleware(secret_key=SECRET, required_claims={"sub"})
    request = Mock(spec=Request)
    request.headers = {"Authorization": f"Bearer {bad_signature}"}
    request.state = Mock()

    with pytest.raises(HTTPException):
        await middleware.dispatch(request, AsyncMock())

    missing_claim = await _token(SECRET, iat=100)
    request.headers = {"Authorization": f"Bearer {missing_claim}"}
    with pytest.raises(HTTPException):
        await middleware.dispatch(request, AsyncMock())


@pytest.mark.unit
def test_verify_token_sync_and_state_attribute_configuration() -> None:
    import asyncio

    token = asyncio.run(_token(SECRET, sub="user"))
    middleware = JWTMiddleware(secret_key=SECRET, state_attribute="user")

    assert middleware.verify_token(token)["sub"] == "user"


@pytest.mark.unit
def test_asgi_adapter_does_not_require_fastapi() -> None:
    import asyncio

    async def protected(request: Request) -> JSONResponse:
        return JSONResponse({"sub": request.state.jwt_payload["sub"]})

    routes = Starlette(routes=[Route("/protected", protected)])
    app = JWTMiddleware(secret_key=SECRET, app=routes)
    token = asyncio.run(_token(SECRET, sub="user"))

    with TestClient(app) as client:
        unauthorized = client.get("/protected")
        authorized = client.get(
            "/protected", headers={"Authorization": f"Bearer {token}"}
        )

    assert unauthorized.status_code == 401
    assert authorized.json() == {"sub": "user"}
