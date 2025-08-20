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
    res = client.post("/kms/Key", json=payload)
    assert res.status_code == 200
    return res.json()


@pytest.fixture
def client_paramiko(tmp_path, monkeypatch):
    mod1 = types.ModuleType("swarmauri_secret_autogpg")

    class DummySecretDrive: ...

    mod1.AutoGpgSecretDrive = DummySecretDrive
    sys.modules["swarmauri_secret_autogpg"] = mod1

    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    with TestClient(app.app) as c:
        yield c


def test_key_encrypt_decrypt_with_paramiko_crypto(client_paramiko):
    from auto_kms.app import AsyncSessionLocal
    from auto_kms.tables.key_version import KeyVersion

    key = _create_key(client_paramiko)

    async def seed():
        async with AsyncSessionLocal() as s:
            kv = KeyVersion(
                key_id=UUID(key["id"]),
                version=1,
                status="active",
                public_material=b"\x11" * 32,
            )
            s.add(kv)
            await s.commit()

    asyncio.run(seed())

    pt = b"hello"
    payload = {"plaintext_b64": base64.b64encode(pt).decode()}
    enc = client_paramiko.post(f"/kms/Key/{key['id']}/encrypt", json=payload)
    assert enc.status_code == 200
    dec_payload = {
        "ciphertext_b64": enc.json()["ciphertext_b64"],
        "nonce_b64": enc.json()["nonce_b64"],
        "tag_b64": enc.json()["tag_b64"],
    }
    dec = client_paramiko.post(f"/kms/Key/{key['id']}/decrypt", json=dec_payload)
    assert dec.status_code == 200
    assert base64.b64decode(dec.json()["plaintext_b64"]) == pt
