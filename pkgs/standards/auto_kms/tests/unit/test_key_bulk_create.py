import asyncio
import importlib

import pytest
from fastapi.testclient import TestClient
from autoapi.v3.orm.tables import Base


@pytest.fixture()
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


def test_bulk_create_keys(client):
    payload = [
        {"name": "b1", "algorithm": "AES256_GCM"},
        {"name": "b2", "algorithm": "AES256_GCM"},
    ]
    res = client.post("/kms/key", json=payload)
    assert res.status_code in {200, 201}
    listed = client.get("/kms/key").json()
    names = {row["name"] for row in listed}
    assert {"b1", "b2"} <= names
