import asyncio
import importlib
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from autoapi.v3.tables import Base
from swarmauri_secret_autogpg import AutoGpgSecretDrive
from auto_kms.tables.key_version import KeyVersion
from auto_kms.tables.key import Key


@pytest.fixture
def client_app(tmp_path, monkeypatch):
    secret_dir = tmp_path / "keys"
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))
    monkeypatch.setattr(
        app, "AutoGpgSecretDrive", lambda: AutoGpgSecretDrive(path=secret_dir)
    )

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as client:
            yield client, app
    finally:
        if hasattr(app, "SECRETS"):
            delattr(app, "SECRETS")
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_key_rotate_creates_new_version(client_app):
    client, app = client_app
    payload = {"name": "k1", "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    key = res.json()
    assert key["primary_version"] == 1

    res = client.post(f"/kms/key/{key['id']}/rotate", json={})
    assert res.status_code == 201

    async def fetch_key_and_versions():
        async with app.AsyncSessionLocal() as session:
            key_obj = await session.get(Key, UUID(str(key["id"])))
            result = await session.execute(
                select(KeyVersion.version).where(
                    KeyVersion.key_id == UUID(str(key["id"]))
                )
            )
            versions = sorted(row[0] for row in result.all())
            return key_obj, versions

    key_obj, versions = asyncio.run(fetch_key_and_versions())
    assert key_obj.primary_version == 2
    assert versions == [1, 2]
