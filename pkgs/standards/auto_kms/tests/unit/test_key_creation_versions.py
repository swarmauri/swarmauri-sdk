import asyncio
import importlib
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from auto_kms.orm import KeyVersion


def _create_key(client, name: str = "k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def client_app(tmp_path, monkeypatch):
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))
    try:
        with TestClient(app.app) as c:
            yield c, app
    finally:
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")
        if hasattr(app, "KEY_PROVIDER"):
            delattr(app, "KEY_PROVIDER")


def test_key_creation_seeded_version(client_app):
    client, app = client_app
    key = _create_key(client)
    key_id = key["id"]

    read = client.get(f"/kms/key/{key_id}")
    assert read.status_code == 200
    data = read.json()
    assert data["id"] == key_id
    assert data["primary_version"] == 1

    async def fetch_versions():
        async with app.engine.asession() as session:
            res = await session.execute(
                select(KeyVersion.version).where(KeyVersion.key_id == UUID(key_id))
            )
            return list(res.scalars().all())

    versions = asyncio.run(fetch_versions())
    assert 1 in versions
    assert max(versions) == data["primary_version"]
