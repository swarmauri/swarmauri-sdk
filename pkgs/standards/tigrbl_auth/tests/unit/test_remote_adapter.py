"""Unit tests for RemoteAuthNAdapter."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import HTTPException, Request, status

import tigrbl_auth.adapters.remote_adapter as remote_adapter
from tigrbl_auth.adapters.remote_adapter import RemoteAuthNAdapter


@pytest.mark.unit
class TestCacheTTL:
    """Tests for cache TTL expiration behavior."""

    def test_cache_ttl_expiration(self, monkeypatch):
        adapter = RemoteAuthNAdapter(base_url="https://auth", cache_ttl=1)

        # Control time.monotonic used by the adapter
        current = {"t": 0.0}
        monkeypatch.setattr(remote_adapter.time, "monotonic", lambda: current["t"])

        # Put value in cache and verify immediate hit
        principal = {"sub": "user"}
        adapter._cache_put("k", principal)
        assert adapter._cache_get("k") == principal

        # Advance time beyond TTL and ensure cache miss/eviction
        current["t"] = 2.0
        assert adapter._cache_get("k") is None
        assert "k" not in adapter._cache


@pytest.mark.unit
class TestNetworkFailure:
    """Tests network failure handling during introspection."""

    @pytest.mark.asyncio
    async def test_introspection_unavailable(self, monkeypatch):
        adapter = RemoteAuthNAdapter(base_url="https://auth")

        async def raise_connect(*args, **kwargs):
            raise httpx.ConnectError("boom")

        monkeypatch.setattr(adapter._client, "post", raise_connect)

        request = MagicMock(spec=Request)
        request.state = SimpleNamespace()

        with pytest.raises(HTTPException) as excinfo:
            await adapter.get_principal(request=request, api_key="abc")
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

        # Optional flow should swallow the failure and return None
        request_opt = MagicMock(spec=Request)
        request_opt.state = SimpleNamespace()
        result = await adapter.get_principal_optional(
            request=request_opt, api_key="abc"
        )
        assert result is None
        assert request_opt.state.principal is None


@pytest.mark.unit
class TestOptionalFlows:
    """Tests optional authentication with missing or invalid credentials."""

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        adapter = RemoteAuthNAdapter(base_url="https://auth")
        request = MagicMock(spec=Request)
        request.state = SimpleNamespace()

        result = await adapter.get_principal_optional(request=request, api_key=None)
        assert result is None
        assert request.state.principal is None

    @pytest.mark.asyncio
    async def test_invalid_api_key(self, monkeypatch):
        adapter = RemoteAuthNAdapter(base_url="https://auth")

        async def fake_post(*args, **kwargs):
            return httpx.Response(status_code=401)

        monkeypatch.setattr(adapter._client, "post", fake_post)

        request = MagicMock(spec=Request)
        request.state = SimpleNamespace()

        result = await adapter.get_principal_optional(request=request, api_key="bad")
        assert result is None
        assert request.state.principal is None
