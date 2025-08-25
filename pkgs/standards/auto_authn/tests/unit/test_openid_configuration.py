import pytest
from fastapi import status


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openid_configuration_contains_required_fields(async_client) -> None:
    resp = await async_client.get("/.well-known/openid-configuration")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["authorization_endpoint"].endswith("/authorize")
    assert data["userinfo_endpoint"].endswith("/userinfo")
    assert "code" in data["response_types_supported"]
    assert "id_token" in data["response_types_supported"]
    assert data["id_token_signing_alg_values_supported"] == ["RS256"]
