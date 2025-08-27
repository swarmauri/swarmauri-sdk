import importlib
import asyncio

import pytest

from swarmauri_crypto_paramiko import ParamikoCrypto


@pytest.fixture
def app_module():
    app = importlib.reload(importlib.import_module("auto_kms.app"))
    try:
        yield app, ParamikoCrypto
    finally:
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")
        if hasattr(app, "KEY_PROVIDER"):
            delattr(app, "KEY_PROVIDER")


def test_ctx_has_crypto_provider(app_module):
    app, CryptoCls = app_module
    ctx: dict = {}
    asyncio.run(app._stash_ctx(ctx))
    assert "crypto" in ctx
    assert isinstance(ctx["crypto"], CryptoCls)
