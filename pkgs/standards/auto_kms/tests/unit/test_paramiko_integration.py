import base64
import importlib
import asyncio


import pytest
from fastapi.testclient import TestClient
from autoapi.v3.orm.tables import Base


def _create_key(client, name="k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def client_paramiko(tmp_path, monkeypatch):
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as c:
            yield c
    finally:
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")
        if hasattr(app, "KEY_PROVIDER"):
            delattr(app, "KEY_PROVIDER")


def test_key_encrypt_decrypt_with_paramiko_crypto(client_paramiko):
    client = client_paramiko

    key = _create_key(client)
    kv_payload = {"key_id": key["id"], "version": 2, "status": "active"}
    res = client.post("/kms/key_version", json=kv_payload)
    assert res.status_code == 201

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


def test_encrypt_accepts_unpadded_base64(client_paramiko):
    client = client_paramiko

    key = _create_key(client, name="k2")
    kv_payload = {"key_id": key["id"], "version": 2, "status": "active"}
    res = client.post("/kms/key_version", json=kv_payload)
    assert res.status_code == 201

    pt = b"world"
    pt_b64 = base64.b64encode(pt).decode().rstrip("=")
    payload = {"plaintext_b64": pt_b64}
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
