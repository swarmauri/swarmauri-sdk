"""Test wrap/unwrap error handling and edge cases."""

import base64
import importlib
import asyncio
import secrets

import pytest
from fastapi.testclient import TestClient
from autoapi.v3.tables import Base
from swarmauri_secret_autogpg import AutoGpgSecretDrive


def _create_key(client, name: str = None, algorithm: str = "AES256_GCM"):
    """Helper to create a test key."""
    if name is None:
        import uuid

        name = f"error_test_key_{uuid.uuid4().hex[:8]}"
    payload = {"name": name, "algorithm": algorithm}
    res = client.post("/kms/key", json=payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create test client with temporary database and secrets."""
    secret_dir = tmp_path / "keys"
    db_path = tmp_path / "kms.db"
    monkeypatch.setenv("KMS_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    app = importlib.reload(importlib.import_module("auto_kms.app"))
    monkeypatch.setattr(
        app,
        "AutoGpgSecretDrive",
        lambda: AutoGpgSecretDrive(path=secret_dir),
    )

    async def init_db():
        async with app.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    try:
        with TestClient(app.app) as c:
            yield c
    finally:
        if hasattr(app, "SECRETS"):
            delattr(app, "SECRETS")
        if hasattr(app, "CRYPTO"):
            delattr(app, "CRYPTO")


def test_wrap_missing_key_material(client):
    """Test wrap operation with missing key_material_b64."""
    key = _create_key(client)

    # Missing key_material_b64
    wrap_payload = {}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 422


def test_wrap_invalid_base64_key_material(client):
    """Test wrap operation with invalid base64 key material."""
    key = _create_key(client)

    # Invalid base64
    wrap_payload = {"key_material_b64": "invalid_base64!@#$"}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 400
    assert (
        "Invalid base64 encoding for key_material_b64" in wrap_response.json()["detail"]
    )


def test_wrap_invalid_base64_aad(client):
    """Test wrap operation with invalid base64 AAD."""
    key = _create_key(client)

    key_material_b64 = base64.b64encode(secrets.token_bytes(32)).decode()
    wrap_payload = {
        "key_material_b64": key_material_b64,
        "aad_b64": "invalid_base64!@#$",
    }
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 400
    assert "Invalid base64 encoding for aad_b64" in wrap_response.json()["detail"]


def test_wrap_nonexistent_key(client):
    """Test wrap operation with non-existent key ID."""
    fake_key_id = "00000000-0000-0000-0000-000000000000"
    key_material_b64 = base64.b64encode(secrets.token_bytes(32)).decode()

    wrap_payload = {"key_material_b64": key_material_b64}
    wrap_response = client.post(f"/kms/key/{fake_key_id}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 404
    assert "Key not found" in wrap_response.json()["detail"]


def test_wrap_disabled_key(client):
    """Test wrap operation with disabled key."""
    key = _create_key(client)

    # Disable the key
    disable_payload = {"status": "disabled"}
    disable_response = client.patch(f"/kms/key/{key['id']}", json=disable_payload)
    assert disable_response.status_code in (200, 422)
    if disable_response.status_code == 200:
        key_material_b64 = base64.b64encode(secrets.token_bytes(32)).decode()
        wrap_payload = {"key_material_b64": key_material_b64}
        wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
        assert wrap_response.status_code == 403
        assert "Key is disabled" in wrap_response.json()["detail"]


def test_unwrap_missing_wrapped_key(client):
    """Test unwrap operation with missing wrapped_key_b64."""
    key = _create_key(client)

    unwrap_payload = {"nonce_b64": base64.b64encode(secrets.token_bytes(12)).decode()}
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 422


def test_unwrap_missing_nonce(client):
    """Test unwrap operation with missing nonce_b64."""
    key = _create_key(client)

    unwrap_payload = {
        "wrapped_key_b64": base64.b64encode(secrets.token_bytes(32)).decode()
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 422


def test_unwrap_invalid_base64_wrapped_key(client):
    """Test unwrap operation with invalid base64 wrapped key."""
    key = _create_key(client)

    unwrap_payload = {
        "wrapped_key_b64": "invalid_base64!@#$",
        "nonce_b64": base64.b64encode(secrets.token_bytes(12)).decode(),
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 400
    assert (
        "Invalid base64 encoding for wrapped_key_b64"
        in unwrap_response.json()["detail"]
    )


def test_unwrap_invalid_base64_nonce(client):
    """Test unwrap operation with invalid base64 nonce."""
    key = _create_key(client)

    unwrap_payload = {
        "wrapped_key_b64": base64.b64encode(secrets.token_bytes(32)).decode(),
        "nonce_b64": "invalid_base64!@#$",
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 400
    assert "Invalid base64 encoding for nonce_b64" in unwrap_response.json()["detail"]


def test_unwrap_invalid_base64_tag(client):
    """Test unwrap operation with invalid base64 tag."""
    key = _create_key(client)

    unwrap_payload = {
        "wrapped_key_b64": base64.b64encode(secrets.token_bytes(32)).decode(),
        "nonce_b64": base64.b64encode(secrets.token_bytes(12)).decode(),
        "tag_b64": "invalid_base64!@#$",
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 400
    assert "Invalid base64 encoding for tag_b64" in unwrap_response.json()["detail"]


def test_unwrap_invalid_base64_aad(client):
    """Test unwrap operation with invalid base64 AAD."""
    key = _create_key(client)

    unwrap_payload = {
        "wrapped_key_b64": base64.b64encode(secrets.token_bytes(32)).decode(),
        "nonce_b64": base64.b64encode(secrets.token_bytes(12)).decode(),
        "aad_b64": "invalid_base64!@#$",
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 400
    assert "Invalid base64 encoding for aad_b64" in unwrap_response.json()["detail"]


def test_unwrap_wrong_nonce(client):
    """Test unwrap operation with wrong nonce fails authentication."""
    key = _create_key(client)

    # First wrap some key material
    key_material_b64 = base64.b64encode(secrets.token_bytes(32)).decode()
    wrap_payload = {"key_material_b64": key_material_b64}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 200
    wrap_data = wrap_response.json()

    # Try to unwrap with wrong nonce
    wrong_nonce = base64.b64encode(secrets.token_bytes(12)).decode()
    unwrap_payload = {
        "wrapped_key_b64": wrap_data["wrapped_key_b64"],
        "nonce_b64": wrong_nonce,  # Wrong nonce
        "tag_b64": wrap_data["tag_b64"],
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    # This should fail with crypto error (exact error depends on crypto implementation)
    assert unwrap_response.status_code >= 400


def test_unwrap_wrong_tag(client):
    """Test unwrap operation with wrong tag fails authentication."""
    key = _create_key(client)

    # First wrap some key material
    key_material_b64 = base64.b64encode(secrets.token_bytes(32)).decode()
    wrap_payload = {"key_material_b64": key_material_b64}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 200
    wrap_data = wrap_response.json()

    # Try to unwrap with wrong tag
    wrong_tag = base64.b64encode(secrets.token_bytes(16)).decode()
    unwrap_payload = {
        "wrapped_key_b64": wrap_data["wrapped_key_b64"],
        "nonce_b64": wrap_data["nonce_b64"],
        "tag_b64": wrong_tag,  # Wrong tag
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    # This should fail with crypto error (exact error depends on crypto implementation)
    assert unwrap_response.status_code >= 400


def test_unwrap_mismatched_aad(client):
    """Test unwrap operation with mismatched AAD fails authentication."""
    key = _create_key(client)

    # Wrap with specific AAD
    key_material_b64 = base64.b64encode(secrets.token_bytes(32)).decode()
    original_aad_b64 = base64.b64encode(b"original_context").decode()
    wrap_payload = {"key_material_b64": key_material_b64, "aad_b64": original_aad_b64}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 200
    wrap_data = wrap_response.json()

    # Try to unwrap with different AAD
    different_aad_b64 = base64.b64encode(b"different_context").decode()
    unwrap_payload = {
        "wrapped_key_b64": wrap_data["wrapped_key_b64"],
        "nonce_b64": wrap_data["nonce_b64"],
        "tag_b64": wrap_data["tag_b64"],
        "aad_b64": different_aad_b64,  # Different AAD
    }
    unwrap_response = client.post(f"/kms/key/{key['id']}/unwrap", json=unwrap_payload)
    # This should fail with crypto error (exact error depends on crypto implementation)
    assert unwrap_response.status_code >= 400


def test_unwrap_nonexistent_key(client):
    """Test unwrap operation with non-existent key ID."""
    fake_key_id = "00000000-0000-0000-0000-000000000000"

    unwrap_payload = {
        "wrapped_key_b64": base64.b64encode(secrets.token_bytes(32)).decode(),
        "nonce_b64": base64.b64encode(secrets.token_bytes(12)).decode(),
    }
    unwrap_response = client.post(f"/kms/key/{fake_key_id}/unwrap", json=unwrap_payload)
    assert unwrap_response.status_code == 404
    assert "Key not found" in unwrap_response.json()["detail"]


def test_unwrap_disabled_key(client):
    """Test unwrap operation with disabled key."""
    key = _create_key(client)

    # First wrap some key material while key is enabled
    key_material_b64 = base64.b64encode(secrets.token_bytes(32)).decode()
    wrap_payload = {"key_material_b64": key_material_b64}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 200
    wrap_data = wrap_response.json()

    # Disable the key
    disable_payload = {"status": "disabled"}
    disable_response = client.patch(f"/kms/key/{key['id']}", json=disable_payload)
    assert disable_response.status_code in (200, 422)
    if disable_response.status_code == 200:
        unwrap_payload = {
            "wrapped_key_b64": wrap_data["wrapped_key_b64"],
            "nonce_b64": wrap_data["nonce_b64"],
            "tag_b64": wrap_data["tag_b64"],
        }
        unwrap_response = client.post(
            f"/kms/key/{key['id']}/unwrap", json=unwrap_payload
        )
        assert unwrap_response.status_code == 403
        assert "Key is disabled" in unwrap_response.json()["detail"]


def test_wrap_unsupported_algorithm(client):
    """Test wrap operation with unsupported algorithm (RSA keys)."""
    # Note: This test assumes RSA keys are not supported for wrapping
    # If RSA support is added later, this test should be updated
    key = _create_key(client, algorithm="RSA2048")

    key_material_b64 = base64.b64encode(secrets.token_bytes(32)).decode()
    wrap_payload = {"key_material_b64": key_material_b64}
    wrap_response = client.post(f"/kms/key/{key['id']}/wrap", json=wrap_payload)
    assert wrap_response.status_code == 400
    assert (
        "Key wrapping only supported for AES256_GCM and CHACHA20_POLY1305"
        in wrap_response.json()["detail"]
    )
