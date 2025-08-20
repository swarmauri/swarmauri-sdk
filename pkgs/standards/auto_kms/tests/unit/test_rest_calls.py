import base64
import importlib
import sys
import types
import asyncio

import pytest
from fastapi.testclient import TestClient
from autoapi.v3.tables import Base


@pytest.fixture
def client(tmp_path, monkeypatch):
    mod1 = types.ModuleType("swarmauri_secret_autogpg")

    class DummySecretDrive: ...

    mod1.AutoGpgSecretDrive = DummySecretDrive
    sys.modules["swarmauri_secret_autogpg"] = mod1

    mod2 = types.ModuleType("swarmauri_crypto_paramiko")

    class DummyCrypto:
        async def encrypt(self, *, kid, plaintext, alg, aad=None, nonce=None):
            from types import SimpleNamespace

            return SimpleNamespace(nonce=b"n", ct=plaintext[::-1], tag=b"t")

        async def decrypt(
            self, *, kid, ciphertext, nonce, tag=None, aad=None, alg=None
        ):
            return ciphertext[::-1]

    mod2.ParamikoCrypto = DummyCrypto
    sys.modules["swarmauri_crypto_paramiko"] = mod2

    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))

    @app.app.middleware("http")
    async def _add_crypto(request, call_next):
        request.state.crypto = DummyCrypto()
        return await call_next(request)

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    with TestClient(app.app) as c:
        yield c


def _create_key(client, name="k1"):
    payload = {"name": name, "algorithm": "AES256_GCM"}
    res = client.post("/kms/Key", json=payload)
    assert res.status_code == 200
    return res.json()


def test_key_create(client):
    data = _create_key(client)
    assert data["name"] == "k1"


def test_key_list(client):
    _create_key(client, "k1")
    _create_key(client, "k2")
    res = client.get("/kms/Key")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_key_read(client):
    key = _create_key(client)
    res = client.get(f"/kms/Key/{key['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == key["id"]


def test_key_update(client):
    key = _create_key(client)
    res = client.patch(
        f"/kms/Key/{key['id']}", json={"name": key["name"], "status": "disabled"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "disabled"


def test_key_replace(client):
    key = _create_key(client)
    payload = {"name": key["name"]}
    res = client.put(f"/kms/Key/{key['id']}", json=payload)
    assert res.status_code == 422


def test_key_delete(client):
    key = _create_key(client)
    res = client.delete(f"/kms/Key/{key['id']}")
    assert res.status_code == 204
    res = client.get(f"/kms/Key/{key['id']}")
    assert res.status_code == 404


def test_key_clear(client):
    _create_key(client)
    res = client.delete("/kms/Key")
    assert res.status_code == 204
    res = client.get("/kms/Key")
    assert res.json() == []


def test_key_encrypt_decrypt(client):
    key = _create_key(client)
    pt = b"hello"
    payload = {"plaintext_b64": base64.b64encode(pt).decode()}
    enc = client.post(f"/kms/Key/{key['id']}/encrypt", json=payload)
    assert enc.status_code == 200
    ct = enc.json()["ciphertext_b64"]
    dec_payload = {
        "ciphertext_b64": ct,
        "nonce_b64": enc.json()["nonce_b64"],
        "tag_b64": enc.json()["tag_b64"],
    }
    dec = client.post(f"/kms/Key/{key['id']}/decrypt", json=dec_payload)
    assert dec.status_code == 200
    assert base64.b64decode(dec.json()["plaintext_b64"]) == pt


def _create_key_version(client, key_id, version=1):
    payload = {"key_id": key_id, "version": version, "status": "active"}
    res = client.post("/kms/key_version", json=payload)
    assert res.status_code == 200
    return res.json()


def test_key_version_create(client):
    key = _create_key(client)
    data = _create_key_version(client, key["id"])
    assert data["version"] == 1


def test_key_version_list(client):
    key = _create_key(client)
    _create_key_version(client, key["id"], 1)
    _create_key_version(client, key["id"], 2)
    res = client.get("/kms/key_version")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_key_version_read(client):
    key = _create_key(client)
    kv = _create_key_version(client, key["id"])
    res = client.get(f"/kms/key_version/{kv['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == kv["id"]


def test_key_version_update(client):
    key = _create_key(client)
    kv = _create_key_version(client, key["id"])
    res = client.patch(
        f"/kms/key_version/{kv['id']}",
        json={"key_id": key["id"], "version": kv["version"], "status": "active"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "active"


def test_key_version_replace(client):
    key = _create_key(client)
    kv = _create_key_version(client, key["id"])
    payload = {"key_id": key["id"], "version": 1, "status": "active"}
    res = client.put(f"/kms/key_version/{kv['id']}", json=payload)
    assert res.status_code == 422


def test_key_version_delete(client):
    key = _create_key(client)
    kv = _create_key_version(client, key["id"])
    res = client.delete(f"/kms/key_version/{kv['id']}")
    assert res.status_code == 204
    res = client.get(f"/kms/key_version/{kv['id']}")
    assert res.status_code == 404


def test_key_version_clear(client):
    key = _create_key(client)
    _create_key_version(client, key["id"])
    res = client.delete("/kms/key_version")
    assert res.status_code == 204
    res = client.get("/kms/key_version")
    assert res.json() == []
