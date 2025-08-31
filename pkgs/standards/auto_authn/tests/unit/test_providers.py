"""Unit tests for AuthN provider adapters.

Verify adapter delegation and hook registration behavior."""

from unittest.mock import MagicMock

import pytest

import auto_authn.providers.local_adapter as local_adapter_mod
from auto_authn.providers.local_adapter import LocalAuthNAdapter
from auto_authn.providers.remote_adapter import RemoteAuthNAdapter
from autoapi.v3.config import __autoapi_auth_context__


@pytest.mark.unit
@pytest.mark.asyncio
async def test_local_adapter_delegates_get_principal(monkeypatch):
    """LocalAuthNAdapter forwards to fastapi dependency."""
    adapter = LocalAuthNAdapter()
    request = MagicMock()

    async def stub(req):
        return {"ok": True}

    monkeypatch.setattr(local_adapter_mod, "get_principal", stub)

    result = await adapter.get_principal(request)

    assert result == {"ok": True}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_local_adapter_injects_auth_context(monkeypatch):
    adapter = LocalAuthNAdapter()
    request = MagicMock()
    principal = {"sub": "u", "tid": "t"}

    async def mock_get(r):
        r.state.principal = principal
        return principal

    monkeypatch.setattr(local_adapter_mod, "get_principal", mock_get)

    result = await adapter.get_principal(request)

    assert result == principal
    assert getattr(request.state, __autoapi_auth_context__) == {
        "user_id": "u",
        "tenant_id": "t",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remote_adapter_injects_auth_context(monkeypatch):
    adapter = RemoteAuthNAdapter(base_url="https://auth.example")
    request = MagicMock()
    principal = {"sub": "u", "tid": "t"}

    async def mock_introspect(api_key):
        return principal

    monkeypatch.setattr(adapter, "_introspect_key", mock_introspect)

    result = await adapter.get_principal(request, api_key="key")

    assert result == principal
    assert getattr(request.state, __autoapi_auth_context__) == {
        "user_id": "u",
        "tenant_id": "t",
    }
