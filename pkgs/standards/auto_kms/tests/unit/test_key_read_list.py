import importlib
import asyncio
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from autoapi.v3.orm.tables import Base


@pytest.fixture
def client_app(tmp_path, monkeypatch):
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as client:
            yield client
    finally:
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_key_read_and_list_without_versions(client_app):
    client = client_app
    payload = {"name": "k1", "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    key = res.json()

    res = client.get(f"/kms/key/{key['id']}")
    assert res.status_code == 200
    body = res.json()
    assert "versions" not in body

    res = client.get("/kms/key")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list)
    assert body and "versions" not in body[0]

    res = client.get(f"/kms/key/{uuid4()}")
    assert res.status_code == 404
