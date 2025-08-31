"""Unit tests for AuthN adapters.

Verify adapter delegation and hook registration behavior."""

from unittest.mock import AsyncMock, MagicMock

import pytest

import auto_authn.adapters.local_adapter as local_adapter_mod
import auto_authn.adapters.remote_adapter as remote_adapter_mod
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
def test_local_adapter_register_inject_hook(monkeypatch):
    """Hook registration delegates to module helper."""
    adapter = LocalAuthNAdapter()
    api = MagicMock()
    hook = MagicMock()
    monkeypatch.setattr(local_adapter_mod, "register_inject_hook", hook)

    adapter.register_inject_hook(api)

    hook.assert_called_once_with(api)


@pytest.mark.unit
def test_remote_adapter_register_hook_noop(monkeypatch):
    """RemoteAuthNAdapter does not register hooks but warns."""
    adapter = RemoteAuthNAdapter(base_url="https://auth.example")
    api = MagicMock()
    warn = MagicMock()
    monkeypatch.setattr(remote_adapter_mod.warnings, "warn", warn)

    adapter.register_inject_hook(api)

    api.register_hook.assert_not_called()
    warn.assert_called_once()
