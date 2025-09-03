import asyncio
import importlib
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from autoapi.v3.orm.tables import Base
from auto_kms.orm import Key
from auto_kms.orm import KeyVersion


@pytest.fixture
def client_app(tmp_path, monkeypatch):
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))

    async def init_db():
        eng, _ = app.ENGINE.raw()
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as client:
            yield client, app
    finally:
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_key_rotate_creates_new_version(client_app):
    client, app = client_app
    payload = {"name": "k1", "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    key = res.json()
    assert key["primary_version"] == 1

    res = client.post(f"/kms/key/{key['id']}/rotate")
    assert res.status_code == 201
    assert res.content == b""

    async def fetch_primary_version():
        async with app.ENGINE.asession() as session:
            result = await session.execute(
                select(Key.primary_version).where(Key.id == UUID(str(key["id"])))
            )
            return result.scalar_one()

    assert asyncio.run(fetch_primary_version()) == 2

    async def fetch_versions():
        async with app.ENGINE.asession() as session:
            result = await session.execute(
                select(KeyVersion.version).where(
                    KeyVersion.key_id == UUID(str(key["id"]))
                )
            )
            return sorted(result.scalars().all())

    versions = asyncio.run(fetch_versions())
    assert versions == [1, 2]


def test_rotate_openapi_spec(client_app):
    client, _ = client_app
    spec = client.get("/openapi.json").json()
    rotate_spec = spec["paths"]["/kms/key/{item_id}/rotate"]["post"]
    assert "requestBody" not in rotate_spec
    assert "201" in rotate_spec["responses"]
    assert rotate_spec["responses"]["201"].get("content") is None
