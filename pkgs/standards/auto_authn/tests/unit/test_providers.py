"""Unit tests for AuthN provider adapters.

Verify adapter delegation and hook registration behavior."""

from unittest.mock import AsyncMock, MagicMock

import pytest

import auto_authn.providers.local_adapter as local_adapter_mod
from auto_authn.providers.local_adapter import LocalAuthNAdapter


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
