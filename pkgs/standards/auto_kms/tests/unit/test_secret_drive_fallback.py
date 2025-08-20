import base64
import importlib
import asyncio
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
def client(tmp_path, monkeypatch):
    from swarmauri_secret_autogpg import AutoGpgSecretDrive as _AutoGpgSecretDrive

    class LocalSecret(_AutoGpgSecretDrive):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("key_dir", tmp_path / "keys")
            super().__init__(*args, **kwargs)

    monkeypatch.setattr("swarmauri_secret_autogpg.AutoGpgSecretDrive", LocalSecret)

    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    with TestClient(app.app) as c:
        yield c, app.AsyncSessionLocal

    if hasattr(app, "SECRETS"):
        delattr(app, "SECRETS")
    if hasattr(app, "CRYPTO"):
        delattr(app, "CRYPTO")


def test_encrypt_decrypt_stores_key_material(client):
    client, AsyncSessionLocal = client
    from auto_kms.tables.key_version import KeyVersion

    key = _create_key(client)

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
