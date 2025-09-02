import asyncio
import importlib
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from auto_kms.orm import KeyVersion


@pytest.fixture
def client_app(tmp_path, monkeypatch):
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))
    try:
        with TestClient(app.app) as client:
            yield client, app
    finally:
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")
        if hasattr(app, "KEY_PROVIDER"):
            delattr(app, "KEY_PROVIDER")


def _fetch_versions(app, key_id):
    async def _inner():
        async with app.engine.asession() as session:
            result = await session.execute(
                select(KeyVersion.version).where(KeyVersion.key_id == UUID(str(key_id)))
            )
            return sorted(result.scalars().all())

    return asyncio.run(_inner())


def test_key_full_lifecycle(client_app):
    client, app = client_app
    payload = {"name": "k1", "algorithm": "AES256_GCM"}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    key = res.json()

    assert _fetch_versions(app, key["id"]) == [1]

    kv_payload = {"key_id": key["id"], "version": 2, "status": "active"}
    res = client.post("/kms/key_version", json=kv_payload)
    assert res.status_code == 201
    assert _fetch_versions(app, key["id"]) == [1, 2]

    res = client.delete(f"/kms/key/{key['id']}")
    assert res.status_code == 200
    assert res.json()["deleted"] == 1

    assert _fetch_versions(app, key["id"]) == []
    res = client.get(f"/kms/key/{key['id']}")
    assert res.status_code == 404
