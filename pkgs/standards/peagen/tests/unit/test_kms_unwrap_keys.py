import base64
from types import ModuleType, SimpleNamespace
import sys

import httpx
import pytest

from peagen.gateway.kms import unwrap_key_with_kms
from peagen.gateway.runtime_cfg import settings
from peagen.orm.keys import DeployKey, GPGKey, PublicKey


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


@pytest.mark.asyncio
async def test_public_key_unwrap(monkeypatch):
    called = {}

    async def fake_unwrap(key: str) -> str:
        called["key"] = key
        return "plain"

    gw_pkg = ModuleType("peagen.gateway")
    gw_pkg.__path__ = []
    sys.modules["peagen.gateway"] = gw_pkg
    kms_mod = ModuleType("peagen.gateway.kms")
    kms_mod.unwrap_key_with_kms = fake_unwrap
    sys.modules["peagen.gateway.kms"] = kms_mod

    ctx = {"result": {"public_key": "pub", "private_key": "wrapped"}}
    await PublicKey._post_read(ctx)
    assert called["key"] == "wrapped"
    assert ctx["result"]["private_key"] == "plain"
    assert ctx["result"]["public_key"] == "pub"


@pytest.mark.asyncio
async def test_gpg_key_unwrap(monkeypatch):
    called = {}

    async def fake_unwrap(key: str) -> str:
        called["key"] = key
        return "plain"

    gw_pkg = ModuleType("peagen.gateway")
    gw_pkg.__path__ = []
    sys.modules["peagen.gateway"] = gw_pkg
    kms_mod = ModuleType("peagen.gateway.kms")
    kms_mod.unwrap_key_with_kms = fake_unwrap
    sys.modules["peagen.gateway.kms"] = kms_mod

    ctx = {"result": {"gpg_key": "gpg", "private_key": "wrapped"}}
    await GPGKey._post_read(ctx)
    assert called["key"] == "wrapped"
    assert ctx["result"]["private_key"] == "plain"
    assert ctx["result"]["gpg_key"] == "gpg"


@pytest.mark.asyncio
async def test_deploy_key_unwrap(monkeypatch):
    called = {}

    async def fake_unwrap(key: str) -> str:
        called["key"] = key
        return "plain"

    gw_pkg = ModuleType("peagen.gateway")
    gw_pkg.__path__ = []
    gw_pkg.log = SimpleNamespace(info=lambda *a, **k: None)
    sys.modules["peagen.gateway"] = gw_pkg
    kms_mod = ModuleType("peagen.gateway.kms")
    kms_mod.unwrap_key_with_kms = fake_unwrap
    sys.modules["peagen.gateway.kms"] = kms_mod

    ctx = {"result": {"public_key": "pub", "private_key": "wrapped"}}
    await DeployKey._post_read(ctx)
    assert called["key"] == "wrapped"
    assert ctx["result"]["private_key"] == "plain"
    assert ctx["result"]["public_key"] == "pub"
