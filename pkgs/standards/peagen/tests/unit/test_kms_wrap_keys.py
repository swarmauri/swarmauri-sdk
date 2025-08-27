from types import ModuleType, SimpleNamespace
import sys

import pytest

from peagen.orm.keys import DeployKey, GPGKey, PublicKey


@pytest.mark.asyncio
async def test_public_key_wrap(monkeypatch):
    called = {}

    async def fake_wrap(key: str) -> str:
        called["key"] = key
        return "wrapped"

    gw_pkg = ModuleType("peagen.gateway")
    gw_pkg.__path__ = []  # mark as package
    sys.modules["peagen.gateway"] = gw_pkg
    kms_mod = ModuleType("peagen.gateway.kms")
    kms_mod.wrap_key_with_kms = fake_wrap
    sys.modules["peagen.gateway.kms"] = kms_mod

    params = SimpleNamespace(public_key="pub", private_key="priv")
    ctx = {"env": SimpleNamespace(params=params)}
    await PublicKey._pre_create(ctx)
    assert called["key"] == "priv"
    assert params.private_key == "wrapped"
    assert params.public_key == "pub"


@pytest.mark.asyncio
async def test_gpg_key_wrap(monkeypatch):
    called = {}

    async def fake_wrap(key: str) -> str:
        called["key"] = key
        return "wrapped"

    gw_pkg = ModuleType("peagen.gateway")
    gw_pkg.__path__ = []
    sys.modules["peagen.gateway"] = gw_pkg
    kms_mod = ModuleType("peagen.gateway.kms")
    kms_mod.wrap_key_with_kms = fake_wrap
    sys.modules["peagen.gateway.kms"] = kms_mod

    params = SimpleNamespace(gpg_key="gpg", private_key="priv")
    ctx = {"env": SimpleNamespace(params=params)}
    await GPGKey._pre_create(ctx)
    assert called["key"] == "priv"
    assert params.private_key == "wrapped"
    assert params.gpg_key == "gpg"


@pytest.mark.asyncio
async def test_deploy_key_wrap(monkeypatch):
    called = {}

    async def fake_wrap(key: str) -> str:
        called["key"] = key
        return "wrapped"

    class DummyPGPKey:
        fingerprint = "FP"

        def parse(self, data: str) -> None:
            assert data == "pub"

    gw_pkg = ModuleType("peagen.gateway")
    gw_pkg.__path__ = []
    gw_pkg.log = SimpleNamespace(info=lambda *args, **kwargs: None)
    sys.modules["peagen.gateway"] = gw_pkg
    kms_mod = ModuleType("peagen.gateway.kms")
    kms_mod.wrap_key_with_kms = fake_wrap
    sys.modules["peagen.gateway.kms"] = kms_mod
    monkeypatch.setattr("pgpy.PGPKey", DummyPGPKey)

    params = SimpleNamespace(public_key="pub", private_key="priv")
    ctx = {"env": SimpleNamespace(params=params)}
    await DeployKey._pre_create(ctx)
    assert called["key"] == "priv"
    assert params.private_key == "wrapped"
    assert params.public_key == "pub"
    assert ctx["fingerprint"] == "FP"
