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


def _create_key(client, name: str = "k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


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
        with TestClient(app.app) as c:
            yield c, app
    finally:
        if hasattr(app, "SECRETS"):
            delattr(app, "SECRETS")
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_key_creation_seeded_version(client_app):
    client, app = client_app
    key = _create_key(client)
    key_id = key["id"]

    async def fetch_key_and_versions():
        async with app.AsyncSessionLocal() as session:
            key_obj = await session.get(Key, UUID(key_id))
            ver_res = await session.execute(
                select(KeyVersion.version).where(KeyVersion.key_id == UUID(key_id))
            )
            return key_obj, [row[0] for row in ver_res.all()]

    key_obj, versions = asyncio.run(fetch_key_and_versions())
    assert key_obj.primary_version == 1
    assert 1 in versions
    assert max(versions) == key_obj.primary_version
