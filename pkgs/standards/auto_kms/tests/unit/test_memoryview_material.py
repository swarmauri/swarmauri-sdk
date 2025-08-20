import base64
import importlib
import asyncio
import types
import sys
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from autoapi.v3.tables import Base


def _create_key(client, name="k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def client_keyref(tmp_path, monkeypatch):
    mod1 = types.ModuleType("swarmauri_secret_autogpg")

    class DummySecretDrive:
        pass

    mod1.AutoGpgSecretDrive = DummySecretDrive
    sys.modules["swarmauri_secret_autogpg"] = mod1

    mod2 = types.ModuleType("swarmauri_crypto_paramiko")

    class DummyParamiko:
        pass

    mod2.ParamikoCrypto = DummyParamiko
    sys.modules["swarmauri_crypto_paramiko"] = mod2

    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))

    class DummyCrypto:
        async def encrypt(self, key, pt, alg, aad=None, nonce=None):
            assert isinstance(key.material, bytes)
            return types.SimpleNamespace(nonce=b"0" * 12, ct=pt, tag=b"1" * 16)

        async def decrypt(self, key, ct, *, aad=None):
            assert isinstance(key.material, bytes)
            return ct.ct

    app.CRYPTO = DummyCrypto()
    app.SECRETS = DummySecretDrive()

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    with TestClient(app.app) as c:
        yield c, app.AsyncSessionLocal

    # cleanup globals and modules
    if hasattr(app, "SECRETS"):
        delattr(app, "SECRETS")
    if hasattr(app, "CRYPTO"):
        delattr(app, "CRYPTO")
    sys.modules.pop("swarmauri_secret_autogpg", None)
    sys.modules.pop("swarmauri_crypto_paramiko", None)


def test_encrypt_decrypt_with_memoryview_material(client_keyref):
    client, AsyncSessionLocal = client_keyref
    from auto_kms.tables.key_version import KeyVersion

    key = _create_key(client)

    async def seed():
        async with AsyncSessionLocal() as s:
            kv = KeyVersion(
                key_id=UUID(key["id"]),
                version=1,
                status="active",
                public_material=memoryview(b"\x11" * 32),
            )
            s.add(kv)
            await s.commit()

    asyncio.run(seed())

    pt = b"hello"
    payload = {"plaintext_b64": base64.b64encode(pt).decode()}
    enc = client.post(f"/kms/key/{key['id']}/encrypt", json=payload)
    assert enc.status_code == 200
    dec_payload = {
        "ciphertext_b64": enc.json()["ciphertext_b64"],
        "nonce_b64": enc.json()["nonce_b64"],
        "tag_b64": enc.json()["tag_b64"],
    }
    dec = client.post(f"/kms/key/{key['id']}/decrypt", json=dec_payload)
    assert dec.status_code == 200
    assert base64.b64decode(dec.json()["plaintext_b64"]) == pt
