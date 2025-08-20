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


def test_encrypt_invalid_base64(client):
    key = _create_key(client)
    # The primary version (1) is seeded automatically during key creation.
    # Create a new secondary version to exercise the key version endpoint.
    kv_payload = {"key_id": key["id"], "version": 2, "status": "active"}
    res = client.post("/kms/key_version", json=kv_payload)
    assert res.status_code == 201
    payload = {
        "plaintext_b64": base64.b64encode(b"hi").decode(),
        "aad_b64": "not-base64",
    }
    res = client.post(f"/kms/key/{key['id']}/encrypt", json=payload)
    assert res.status_code == 400
    assert "aad_b64" in res.json()["detail"]


def test_resource_names():
    from auto_kms.tables.key import Key
    from auto_kms.tables.key_version import KeyVersion

    assert Key.__resource__ == "key"
    assert KeyVersion.__resource__ == "key_version"
