import importlib
import sys
import types
import asyncio

import pytest


@pytest.fixture
def app_module():
    mod1 = types.ModuleType("swarmauri_secret_autogpg")

    class DummySecretDrive: ...

    mod1.AutoGpgSecretDrive = DummySecretDrive
    sys.modules["swarmauri_secret_autogpg"] = mod1

    mod2 = types.ModuleType("swarmauri_crypto_paramiko")

    class DummyCrypto: ...

    mod2.ParamikoCrypto = DummyCrypto
    sys.modules["swarmauri_crypto_paramiko"] = mod2

    app = importlib.reload(importlib.import_module("auto_kms.app"))
    try:
        yield app, DummySecretDrive, DummyCrypto
    finally:
        if hasattr(app, "SECRETS"):
            delattr(app, "SECRETS")
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")
        sys.modules.pop("swarmauri_secret_autogpg", None)
        sys.modules.pop("swarmauri_crypto_paramiko", None)


def test_ctx_has_secrets_provider(app_module):
    app, DummySecretDrive, _ = app_module
    ctx: dict = {}
    asyncio.run(app._stash_ctx(ctx))
    assert "secrets" in ctx
    assert isinstance(ctx["secrets"], DummySecretDrive)


def test_ctx_has_crypto_provider(app_module):
    app, _, DummyCrypto = app_module
    ctx: dict = {}
    asyncio.run(app._stash_ctx(ctx))
    assert "crypto" in ctx
    assert isinstance(ctx["crypto"], DummyCrypto)
