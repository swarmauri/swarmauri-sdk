"""Tests for OAuth 2.0 token endpoint compliance with RFC 6749 §5.2."""

import pytest
import pytest_asyncio
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient, BasicAuth

from tigrbl_auth.fastapi_deps import get_db
from tigrbl_auth.routers.auth_flows import router
from tigrbl_auth.runtime_cfg import settings


AUTH = BasicAuth("abc", "secret")


class DummyClient:
    id = "abc"

    def verify_secret(self, secret: str) -> bool:  # pragma: no cover - trivial
        return secret == "secret"


class DummyDB:
    async def scalar(self, stmt):  # pragma: no cover - trivial
        return DummyClient()


async def _override_db():
    yield DummyDB()


@pytest_asyncio.fixture()
async def client():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture()
def enable_rfc6749():
    original = settings.enable_rfc6749
    settings.enable_rfc6749 = True
    try:
        yield
    finally:
        settings.enable_rfc6749 = original


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_grant_type_returns_invalid_request(client, enable_rfc6749):
    """RFC 6749 §5.2: grant_type is required."""
    data = {"username": "user", "password": "pass"}
    resp = await client.post("/token", data=data, auth=AUTH)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "invalid_request"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unsupported_grant_type_returns_error(client, enable_rfc6749):
    """RFC 6749 §5.2: unsupported_grant_type is returned for unknown grants."""
    data = {
        "username": "user",
        "password": "pass",
        "grant_type": "client_credentials",
    }
    resp = await client.post("/token", data=data, auth=AUTH)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "unsupported_grant_type"


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data",
    [
        {"grant_type": "password", "username": "user"},
        {"grant_type": "password", "password": "pass"},
    ],
)
async def test_password_grant_requires_username_and_password(
    client, data, enable_rfc6749
):
    """RFC 6749 §4.3: username and password parameters are required."""
    resp = await client.post("/token", data=data, auth=AUTH)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "invalid_request"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authorization_code_grant_requires_code(client, enable_rfc6749):
    """RFC 6749 §4.1.3: code and redirect_uri are required."""
    data = {
        "grant_type": "authorization_code",
        "redirect_uri": "https://c",
        "client_id": "abc",
    }
    resp = await client.post("/token", data=data, auth=AUTH)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"] == "invalid_request"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unsupported_grant_type_when_disabled(client):
    """Without RFC 6749 enforcement FastAPI validation is returned."""
    original = settings.enable_rfc6749
    settings.enable_rfc6749 = False
    try:
        data = {
            "username": "user",
            "password": "pass",
            "grant_type": "client_credentials",
        }
        resp = await client.post("/token", data=data, auth=AUTH)
    finally:
        settings.enable_rfc6749 = original
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = resp.json()["detail"]
    assert detail[0]["loc"][-1] == "grant_type"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_endpoint_requires_client_auth(client):
    """The token endpoint must reject requests without client authentication."""
    resp = await client.post("/token", data={"grant_type": "authorization_code"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["error"] == "invalid_client"
