import importlib
import asyncio

import pytest

from swarmauri_secret_autogpg import AutoGpgSecretDrive as _SecretDrive
from auto_kms.crypto import ParamikoCryptoAdapter


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    class TmpSecretDrive(_SecretDrive):
        def __init__(self):
            super().__init__(path=tmp_path / "keys")

    app = importlib.reload(importlib.import_module("auto_kms.app"))
    monkeypatch.setattr(app, "AutoGpgSecretDrive", TmpSecretDrive)
    try:
        yield app, TmpSecretDrive, ParamikoCryptoAdapter
    finally:
        if hasattr(app, "SECRETS"):
            delattr(app, "SECRETS")
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_ctx_has_secrets_provider(app_module):
    app, TmpSecretDrive, _ = app_module
    ctx: dict = {}
    asyncio.run(app._stash_ctx(ctx))
    assert "secrets" in ctx
    assert isinstance(ctx["secrets"], TmpSecretDrive)


def test_ctx_has_crypto_provider(app_module):
    app, _, CryptoCls = app_module
    ctx: dict = {}
    asyncio.run(app._stash_ctx(ctx))
    assert "crypto" in ctx
    assert isinstance(ctx["crypto"], CryptoCls)
