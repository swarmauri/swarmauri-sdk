"""Test wrap/unwrap roundtrip functionality."""

import base64
import importlib
import asyncio
import secrets

import pytest
from fastapi.testclient import TestClient
from tigrbl.orm.tables import Base


def _create_key(client, name: str = None, algorithm: str = "AES256_GCM"):
    """Helper to create a test key."""
    if name is None:
        import uuid

        name = f"wrap_test_key_{uuid.uuid4().hex[:8]}"
    payload = [{"name": name, "algorithm": algorithm}]
    res = client.post("/kms/key", json=payload)
    if res.status_code not in {200, 201}:
        print(f"Key creation failed: {res.status_code} - {res.json()}")
    assert res.status_code in {200, 201}
    key = res.json()[0]
    rotate = client.post(f"/kms/key/{key['id']}/rotate")
    assert rotate.status_code in {200, 201}
    return key


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create test client with temporary database."""
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("tigrbl_kms.app"))

    async def init_db():
        eng, _ = app.ENGINE.raw()
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as c:
            yield c
    finally:
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_wrap_unwrap_basic_roundtrip(client):
    """Test basic wrap/unwrap roundtrip with AES key material."""
    # Create a key for wrapping
    key = _create_key(client)

    # Generate some key material to wrap (32-byte AES key)
    key_material = secrets.token_bytes(32)
    key_material_b64 = base64.b64encode(key_material).decode()

    # Wrap the key material
    wrap_payload = {"key_material_b64": key_material_b64}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 200

    wrap_data = wrap_response.json()

    # Verify wrap response structure
    assert "kid" in wrap_data
    assert "version" in wrap_data
    assert "alg" in wrap_data
    assert "nonce_b64" in wrap_data
    assert "wrapped_key_b64" in wrap_data
    assert "tag_b64" in wrap_data
    assert wrap_data["kid"] == key["id"]
    assert wrap_data["alg"] == "AES256_GCM"

    # Unwrap the key material
    unwrap_payload = {
        "wrapped_key_b64": wrap_data["wrapped_key_b64"],
        "nonce_b64": wrap_data["nonce_b64"],
        "tag_b64": wrap_data["tag_b64"],
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 200

    unwrap_data = unwrap_response.json()

    # Verify unwrapped key material matches original
    assert "key_material_b64" in unwrap_data
    unwrapped_material = base64.b64decode(unwrap_data["key_material_b64"])
    assert unwrapped_material == key_material


def test_wrap_unwrap_with_aad(client):
    """Test wrap/unwrap roundtrip with Additional Authenticated Data."""
    # Create a key for wrapping
    key = _create_key(client)

    # Generate key material and AAD
    key_material = secrets.token_bytes(32)
    key_material_b64 = base64.b64encode(key_material).decode()
    aad = b"key_context_info"
    aad_b64 = base64.b64encode(aad).decode()

    # Wrap with AAD
    wrap_payload = {"key_material_b64": key_material_b64, "aad_b64": aad_b64}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 200

    wrap_data = wrap_response.json()
    assert wrap_data["aad_b64"] == aad_b64  # AAD should be echoed

    # Unwrap with AAD
    unwrap_payload = {
        "wrapped_key_b64": wrap_data["wrapped_key_b64"],
        "nonce_b64": wrap_data["nonce_b64"],
        "tag_b64": wrap_data["tag_b64"],
        "aad_b64": aad_b64,
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 200

    unwrap_data = unwrap_response.json()
    unwrapped_material = base64.b64decode(unwrap_data["key_material_b64"])
    assert unwrapped_material == key_material


def test_wrap_unwrap_different_key_sizes(client):
    """Test wrapping different sizes of key material."""
    key = _create_key(client)

    # Test different key sizes
    test_sizes = [16, 24, 32, 48, 64]  # Various key sizes in bytes

    for size in test_sizes:
        key_material = secrets.token_bytes(size)
        key_material_b64 = base64.b64encode(key_material).decode()

        # Wrap
        wrap_payload = {"key_material_b64": key_material_b64}
        wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
        assert wrap_response.status_code == 200

        wrap_data = wrap_response.json()

        # Unwrap
        unwrap_payload = {
            "wrapped_key_b64": wrap_data["wrapped_key_b64"],
            "nonce_b64": wrap_data["nonce_b64"],
            "tag_b64": wrap_data["tag_b64"],
        }
        unwrap_response = client.post(
            f"/kms/key/{key['id']}/unwrap", json=unwrap_payload
        )
        assert unwrap_response.status_code == 200

        unwrap_data = unwrap_response.json()
        unwrapped_material = base64.b64decode(unwrap_data["key_material_b64"])
        assert unwrapped_material == key_material


def test_multiple_wrap_operations_same_key(client):
    """Test that multiple wrap operations with same key produce different results."""
    key = _create_key(client)

    key_material = secrets.token_bytes(32)
    key_material_b64 = base64.b64encode(key_material).decode()

    # Perform multiple wrap operations
    wrap_results = []
    for _ in range(3):
        wrap_payload = {"key_material_b64": key_material_b64}
        wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
        assert wrap_response.status_code == 200
        wrap_results.append(wrap_response.json())

    # Each wrap should produce different nonce and ciphertext
    nonces = [result["nonce_b64"] for result in wrap_results]
    ciphertexts = [result["wrapped_key_b64"] for result in wrap_results]

    assert len(set(nonces)) == 3  # All nonces should be unique
    assert len(set(ciphertexts)) == 3  # All ciphertexts should be unique

    # But all should unwrap to the same key material
    for wrap_data in wrap_results:
        unwrap_payload = {
            "wrapped_key_b64": wrap_data["wrapped_key_b64"],
            "nonce_b64": wrap_data["nonce_b64"],
            "tag_b64": wrap_data["tag_b64"],
        }
        unwrap_response = client.post(
            f"/kms/key/{key['id']}/unwrap", json=unwrap_payload
        )
        assert unwrap_response.status_code == 200

        unwrap_data = unwrap_response.json()
        unwrapped_material = base64.b64decode(unwrap_data["key_material_b64"])
        assert unwrapped_material == key_material


def test_wrap_unwrap_empty_key_material(client):
    """Test wrapping empty key material."""
    key = _create_key(client)

    # Empty key material
    key_material = b""
    key_material_b64 = base64.b64encode(key_material).decode()

    # Wrap
    wrap_payload = {"key_material_b64": key_material_b64}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 200

    wrap_data = wrap_response.json()

    # Unwrap
    unwrap_payload = {
        "wrapped_key_b64": wrap_data["wrapped_key_b64"],
        "nonce_b64": wrap_data["nonce_b64"],
        "tag_b64": wrap_data["tag_b64"],
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 200

    unwrap_data = unwrap_response.json()
    unwrapped_material = base64.b64decode(unwrap_data["key_material_b64"])
    assert unwrapped_material == key_material == b""
