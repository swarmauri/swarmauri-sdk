import pytest
from fastapi import status

from tigrbl_auth.oidc_id_token import rotate_rsa_jwt_key


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jwks_rotation_publishes_new_key(async_client, temp_key_file) -> None:
    resp = await async_client.get("/.well-known/jwks.json")
    assert resp.status_code == status.HTTP_200_OK
    before = resp.json()["keys"]

    await rotate_rsa_jwt_key()

    resp = await async_client.get("/.well-known/jwks.json")
    assert resp.status_code == status.HTTP_200_OK
    after = resp.json()["keys"]
    assert len(after) == len(before) + 1
