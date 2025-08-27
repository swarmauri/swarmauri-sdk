import base64
from types import SimpleNamespace

import httpx
import pytest

from peagen.gateway.kms import unwrap_key_with_kms
from peagen.gateway.runtime_cfg import settings


@pytest.mark.asyncio
async def test_unwrap_no_url(monkeypatch):
    monkeypatch.setattr(settings, "kms_unwrap_url", None)
    result = await unwrap_key_with_kms("wrapped")
    assert result == "wrapped"


@pytest.mark.asyncio
async def test_unwrap_success(monkeypatch):
    monkeypatch.setattr(settings, "kms_unwrap_url", "http://kms")

    unwrapped = "secret"
    encoded = base64.b64encode(unwrapped.encode()).decode()

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, json):
            assert url == "http://kms"
            assert json == {"wrapped_key_b64": "wrapped"}
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"key_material_b64": encoded},
            )

    monkeypatch.setattr(httpx, "AsyncClient", lambda: DummyClient())
    result = await unwrap_key_with_kms("wrapped")
    assert result == unwrapped


@pytest.mark.asyncio
async def test_unwrap_failure(monkeypatch):
    monkeypatch.setattr(settings, "kms_unwrap_url", "http://kms")

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, json):
            raise RuntimeError("boom")

    monkeypatch.setattr(httpx, "AsyncClient", lambda: DummyClient())
    result = await unwrap_key_with_kms("wrapped")
    assert result == "wrapped"
