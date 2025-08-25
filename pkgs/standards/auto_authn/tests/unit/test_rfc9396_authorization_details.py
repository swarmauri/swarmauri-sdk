"""Tests for OAuth 2.0 Rich Authorization Requests (RFC 9396).

RFC excerpt (RFC 9396 §2.1):

   The "authorization_details" parameter is a JSON array of objects.
   Each object MUST contain a "type" member that is a string identifying
   the authorization detail type.
"""

from __future__ import annotations

import json
from importlib import reload

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.rfc9396 import parse_authorization_details
import auto_authn.v2.runtime_cfg as runtime_cfg


@pytest.mark.unit
def test_parse_authorization_details_accepts_valid_input():
    """Valid authorization_details are parsed into a list."""

    details = parse_authorization_details('[{"type": "payment"}]')
    assert details == [{"type": "payment"}]


@pytest.mark.unit
def test_parse_authorization_details_rejects_missing_type():
    """Objects without a "type" member are rejected."""

    with pytest.raises(ValueError):
        parse_authorization_details('[{"foo": "bar"}]')


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_rejects_invalid_authorization_details_when_enabled(monkeypatch):
    """Server returns error for invalid authorization_details when RFC enabled."""

    monkeypatch.setenv("ENABLE_RFC9396", "1")
    reload(runtime_cfg)
    from auto_authn.v2.routers import auth_flows

    app = FastAPI()
    app.include_router(auth_flows.router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = {
            "grant_type": "password",
            "username": "user",
            "password": "pass",
            "authorization_details": json.dumps({"foo": "bar"}),
        }
        resp = await client.post("/token", data=data)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    body = resp.json()
    assert body["error"] == "invalid_authorization_details"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_ignores_authorization_details_when_disabled(monkeypatch):
    """When disabled, invalid authorization_details do not affect outcome."""

    monkeypatch.delenv("ENABLE_RFC9396", raising=False)
    reload(runtime_cfg)
    from auto_authn.v2.routers import auth_flows

    app = FastAPI()
    app.include_router(auth_flows.router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = {
            "grant_type": "password",
            "username": "user",
            "password": "pass",
            "authorization_details": json.dumps({"foo": "bar"}),
        }
        resp = await client.post("/token", data=data)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
