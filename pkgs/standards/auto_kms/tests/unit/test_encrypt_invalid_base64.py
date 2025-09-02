import asyncio
import base64
import importlib

import pytest
from autoapi.v3.orm.tables import Base
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
    mod = importlib.reload(importlib.import_module("auto_kms.app"))

    async def init_db():
        async for session in mod.app.get_async_db():
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break

    asyncio.run(init_db())
    try:
        with TestClient(mod.app) as c:
            yield c
    finally:
        if hasattr(mod, "CRYPTO"):
            delattr(mod, "CRYPTO")


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
    from auto_kms.orm import Key
    from auto_kms.orm import KeyVersion

    assert Key.__resource__ == "key"
    assert KeyVersion.__resource__ == "key_version"
