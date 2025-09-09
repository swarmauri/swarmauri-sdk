import base64
import importlib
import asyncio

import pytest
from fastapi.testclient import TestClient
from tigrbl.v3.orm.tables import Base


def _create_key(client, name: str = "k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=[payload])
    assert res.status_code in {200, 201}
    return res.json()[0]


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("tigrbl_kms.app"))

    async def init_db():
        eng, _ = app.ENGINE.raw()
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as c:
            yield c
    finally:
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_key_creation_encrypt_decrypt(client):
    """Document key creation followed by encrypt/decrypt roundtrip."""
    key = _create_key(client)
    plaintext = b"hello"
    payload = {"plaintext_b64": base64.b64encode(plaintext).decode()}
    enc = client.post(f"/kms/key/{key['id']}/encrypt", json=payload)
    assert enc.status_code == 200
    dec_payload = {
        "ciphertext_b64": enc.json()["ciphertext_b64"],
        "nonce_b64": enc.json()["nonce_b64"],
        "tag_b64": enc.json()["tag_b64"],
    }
    dec = client.post(f"/kms/key/{key['id']}/decrypt", json=dec_payload)
    assert dec.status_code == 200
    assert base64.b64decode(dec.json()["plaintext_b64"]) == plaintext
