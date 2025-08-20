import base64
import importlib
import asyncio
import types
import sys

import pytest
from fastapi.testclient import TestClient
from autoapi.v3.tables import Base


def _create_key(client, name="k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def client_kid(tmp_path, monkeypatch):
    mod1 = types.ModuleType("swarmauri_secret_autogpg")
    from swarmauri_core.crypto.types import (
        ExportPolicy,
        KeyRef,
        KeyType,
        KeyUse,
    )

    class DummySecretDrive:
        async def load_key(self, *, kid, require_private=False, **_):
            return KeyRef(
                kid=str(kid),
                version=1,
                type=KeyType.SYMMETRIC,
                uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=b"k" * 32,
            )

    mod1.AutoGpgSecretDrive = DummySecretDrive
    sys.modules["swarmauri_secret_autogpg"] = mod1

    mod2 = types.ModuleType("swarmauri_crypto_paramiko")

    class DummyParamikoCrypto: ...

    mod2.ParamikoCrypto = DummyParamikoCrypto
    sys.modules["swarmauri_crypto_paramiko"] = mod2

    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")

    app = importlib.reload(importlib.import_module("auto_kms.app"))

    class DummyCrypto:
        async def encrypt(self, *, kid, plaintext, alg, aad=None, nonce=None):
            assert alg == "AES-256-GCM"
            from types import SimpleNamespace

            return SimpleNamespace(
                version=1, alg=alg, nonce=b"n" * 12, ct=plaintext, tag=b"t"
            )

        async def decrypt(self, *, kid, ciphertext, nonce, tag, aad=None, alg=None):
            assert alg == "AES-256-GCM"
            return ciphertext

    app.SECRETS = DummySecretDrive()
    app.CRYPTO = DummyCrypto()

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    with TestClient(app.app) as c:
        yield c
    if hasattr(app, "SECRETS"):
        delattr(app, "SECRETS")
    if hasattr(app, "CRYPTO"):
        delattr(app, "CRYPTO")
    sys.modules.pop("swarmauri_secret_autogpg", None)
    sys.modules.pop("swarmauri_crypto_paramiko", None)


def test_encrypt_passes_provider_algorithm_string(client_kid):
    key = _create_key(client_kid)
    payload = {"plaintext_b64": base64.b64encode(b"hello").decode()}
    res = client_kid.post(f"/kms/key/{key['id']}/encrypt", json=payload)
    assert res.status_code == 200
    assert res.json()["alg"] == "AES256_GCM"
