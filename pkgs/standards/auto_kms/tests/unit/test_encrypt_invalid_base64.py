import asyncio
import base64
import importlib

import pytest
from autoapi.v3.tables import Base
from fastapi.testclient import TestClient


def _create_key(client, name="k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def client(tmp_path, monkeypatch):
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


def test_encrypt_invalid_base64(client):
    key = _create_key(client)
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
