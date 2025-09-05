import pytest
from fastapi import status


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openid_configuration_contains_required_fields(async_client) -> None:
    resp = await async_client.get("/.well-known/openid-configuration")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    from auto_authn.rfc8414_metadata import JWKS_PATH, ISSUER

    assert data["issuer"] == ISSUER
    assert data["authorization_endpoint"].endswith("/authorize")
    assert data["userinfo_endpoint"].endswith("/userinfo")
    assert data["jwks_uri"].endswith(JWKS_PATH)
    assert "code" in data["response_types_supported"]
    assert "token" in data["response_types_supported"]
    assert "id_token" in data["response_types_supported"]
    assert data["id_token_signing_alg_values_supported"] == ["RS256"]
    assert "openid" in data["scopes_supported"]
    assert "address" in data["scopes_supported"]
    assert "phone" in data["scopes_supported"]
    assert "sub" in data["claims_supported"]
    assert "address" in data["claims_supported"]
    assert "phone_number" in data["claims_supported"]
    assert "authorization_code" in data["grant_types_supported"]
    assert "client_secret_basic" in data["token_endpoint_auth_methods_supported"]
    assert "S256" in data["code_challenge_methods_supported"]
    assert "query" in data["response_modes_supported"]
