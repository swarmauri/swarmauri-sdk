"""Verify adapter auth context injection."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import auto_authn.adapters.local_adapter as local_adapter_mod
from auto_authn.adapters.local_adapter import LocalAuthNAdapter
from auto_authn.adapters.remote_adapter import RemoteAuthNAdapter
from autoapi.v3.config import __autoapi_auth_context__


@pytest.mark.unit
@pytest.mark.asyncio
async def test_local_adapter_sets_auth_context(monkeypatch):
    """Local adapter populates request.state with auth context."""
    adapter = LocalAuthNAdapter()
    request = MagicMock(state=SimpleNamespace())
    mock_get = AsyncMock(return_value={"tid": "t1", "sub": "u1"})
    monkeypatch.setattr(local_adapter_mod, "get_principal", mock_get)

    result = await adapter.get_principal(request)

    assert result == {"tid": "t1", "sub": "u1"}
    ctx = getattr(request.state, __autoapi_auth_context__)
    assert ctx["tenant_id"] == "t1"
    assert ctx["user_id"] == "u1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remote_adapter_sets_auth_context(monkeypatch):
    """Remote adapter stores auth context from introspection."""
    adapter = RemoteAuthNAdapter(base_url="https://auth.example")
    request = MagicMock(state=SimpleNamespace())
    monkeypatch.setattr(
        adapter, "_introspect_key", AsyncMock(return_value={"tid": "t1", "sub": "u1"})
    )

    result = await adapter.get_principal(request, api_key="abc")

    assert result == {"tid": "t1", "sub": "u1"}
    ctx = getattr(request.state, __autoapi_auth_context__)
    assert ctx["tenant_id"] == "t1"
    assert ctx["user_id"] == "u1"
