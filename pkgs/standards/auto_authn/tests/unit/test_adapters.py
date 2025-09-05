"""Unit tests for AuthN adapters.

Verify adapter delegation and hook registration behavior."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import auto_authn.adapters.local_adapter as local_adapter_mod
from autoapi.v3.config.constants import AUTOAPI_AUTH_CONTEXT_ATTR
from auto_authn.adapters.local_adapter import LocalAuthNAdapter
from auto_authn.adapters.remote_adapter import RemoteAuthNAdapter


@pytest.mark.unit
@pytest.mark.asyncio
async def test_local_adapter_delegates_get_principal(monkeypatch):
    """LocalAuthNAdapter forwards to fastapi dependency."""
    adapter = LocalAuthNAdapter()
    request = MagicMock()
    mock_get = AsyncMock(return_value={"ok": True})
    monkeypatch.setattr(local_adapter_mod, "get_principal", mock_get)

    result = await adapter.get_principal(request)

    mock_get.assert_awaited_once_with(request)
    assert result == {"ok": True}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_local_adapter_injects_auth_context(monkeypatch):
    adapter = LocalAuthNAdapter()
    request = MagicMock()
    request.state = SimpleNamespace()
    principal = {"sub": "u1", "tid": "t1"}
    mock_get = AsyncMock(return_value=principal)
    monkeypatch.setattr(local_adapter_mod, "get_principal", mock_get)

    result = await adapter.get_principal(request)

    assert result == principal
    assert getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR) == {
        "user_id": "u1",
        "tenant_id": "t1",
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remote_adapter_injects_auth_context(monkeypatch):
    adapter = RemoteAuthNAdapter(base_url="https://auth.example")
    request = MagicMock()
    request.state = SimpleNamespace()
    principal = {"sub": "u2", "tid": "t2"}
    adapter._cache_put("key", principal)

    result = await adapter.get_principal(request, api_key="key")

    assert result == principal
    assert getattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR) == {
        "user_id": "u2",
        "tenant_id": "t2",
    }
