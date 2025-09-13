import pytest
from fastapi import status


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openid_configuration_values(async_client) -> None:
    """OpenID configuration should expose issuer and JWKS URI."""
    resp = await async_client.get("/.well-known/openid-configuration")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    from tigrbl_auth.rfc8414_metadata import JWKS_PATH, ISSUER

    assert data["issuer"] == ISSUER
    assert data["jwks_uri"].endswith(JWKS_PATH)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jwks_returns_public_keys(async_client) -> None:
    """JWKS endpoint should publish at least one public key."""
    resp = await async_client.get("/.well-known/jwks.json")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    keys = data.get("keys")
    assert isinstance(keys, list) and keys
    first = keys[0]
    assert "kid" in first
    assert "kty" in first
