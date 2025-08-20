import base64
import importlib
import asyncio

from fastapi.testclient import TestClient
from autoapi.v3.tables import Base
from swarmauri_secret_autogpg import AutoGpgSecretDrive
import pytest


def _create_key(client, name="k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def client(tmp_path, monkeypatch):
    secret_dir = tmp_path / "keys"
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))
    monkeypatch.setattr(
        app,
        "AutoGpgSecretDrive",
        lambda: AutoGpgSecretDrive(path=secret_dir),
    )

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as c:
            yield c
    finally:
        if hasattr(app, "SECRETS"):
            delattr(app, "SECRETS")
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_encrypt_decrypt_roundtrip(client):
    key = _create_key(client)

    plaintext = b"hello world"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc_res = client.post(
        f"/kms/key/{key['id']}/encrypt", json={"plaintext_b64": pt_b64}
    )
    assert enc_res.status_code == 200
    enc = enc_res.json()

    dec_payload = {
        "ciphertext_b64": enc["ciphertext_b64"],
        "nonce_b64": enc["nonce_b64"],
        "tag_b64": enc.get("tag_b64"),
    }
    dec_res = client.post(f"/kms/key/{key['id']}/decrypt", json=dec_payload)
    assert dec_res.status_code == 200
    assert base64.b64decode(dec_res.json()["plaintext_b64"]) == plaintext
