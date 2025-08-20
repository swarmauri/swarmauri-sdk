import base64
import importlib
import asyncio
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from autoapi.v3.tables import Base
from swarmauri_secret_autogpg import AutoGpgSecretDrive


def _create_key(client, name="k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def client_keyref(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "auto_kms.app.AutoGpgSecretDrive",
        lambda: AutoGpgSecretDrive(path=tmp_path / "keys"),
    )
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as c:
            yield c, app.AsyncSessionLocal
    finally:
        if hasattr(app, "SECRETS"):
            delattr(app, "SECRETS")
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


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


def test_encrypt_invalid_base64_returns_400(client_keyref):
    client, AsyncSessionLocal = client_keyref
    from auto_kms.tables.key_version import KeyVersion

    key = _create_key(client, name="k2")

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

    payload = {"plaintext_b64": "not-base64"}
    res = client.post(f"/kms/key/{key['id']}/encrypt", json=payload)
    assert res.status_code == 400
    assert "Invalid base64" in res.json()["detail"]
