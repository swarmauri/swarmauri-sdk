import asyncio
import importlib

from swarmauri_base.crypto.CryptoBase import CryptoBase
from auto_kms.crypto import ParamikoCryptoAdapter


class DummyCrypto(CryptoBase):
    def supports(self):  # pragma: no cover - not used
        return {}


class DummyPluginManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.get_called = False

    def get(self, group, name=None):
        self.get_called = True
        assert group == "cryptos"
        return DummyCrypto()


def test_crypto_provider_loaded_via_plugins(monkeypatch):
    app = importlib.reload(importlib.import_module("auto_kms.app"))
    pm = DummyPluginManager({})
    monkeypatch.setattr(app, "PluginManager", lambda cfg: pm)
    monkeypatch.setattr(app, "AutoGpgSecretDrive", lambda: object())

    ctx: dict = {}
    asyncio.run(app._stash_ctx(ctx))

    assert pm.get_called
    assert isinstance(ctx["crypto"], ParamikoCryptoAdapter)
    assert isinstance(ctx["crypto"]._crypto, DummyCrypto)

    if hasattr(app, "SECRETS"):
        delattr(app, "SECRETS")
    if hasattr(app, "CRYPTO"):
        delattr(app, "CRYPTO")
