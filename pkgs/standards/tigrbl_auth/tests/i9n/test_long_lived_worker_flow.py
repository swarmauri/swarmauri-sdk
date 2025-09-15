import time
import pytest
from fastapi import status
from httpx import AsyncClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from tigrbl_auth import encode_jwt, decode_jwt
from tigrbl_auth.crypto import hash_pw
from tigrbl_auth.orm import Tenant, User
from tigrbl_auth.rfc.rfc9449_dpop import (
    create_proof,
    jwk_from_public_key,
    jwk_thumbprint,
)
from tigrbl_auth.rfc.rfc8693 import TOKEN_EXCHANGE_GRANT_TYPE, TokenType


@pytest.mark.integration
@pytest.mark.asyncio
async def test_worker_enrollment_flow_dpop(
    async_client: AsyncClient, db_session, enable_rfc8693
) -> None:
    tenant = Tenant(slug="worker-tenant", name="Worker Tenant", email="wt@example.com")
    db_session.add(tenant)
    await db_session.commit()
    worker = User(
        tenant_id=tenant.id,
        username="worker1",
        email="worker1@example.com",
        password_hash=hash_pw("SecretPwd123!"),
    )
    db_session.add(worker)
    await db_session.commit()

    enrollment = encode_jwt(
        sub=str(worker.id), tid=str(tenant.id), exp=int(time.time()) + 3600
    )

    sk = Ed25519PrivateKey.generate()
    private_pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    jwk = jwk_from_public_key(sk.public_key())
    jkt = jwk_thumbprint(jwk)
    proof = create_proof(private_pem, "POST", "http://test/token/exchange")

    resp = await async_client.post(
        "/token/exchange",
        data={
            "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
            "subject_token": enrollment,
            "subject_token_type": TokenType.ACCESS_TOKEN.value,
            "audience": "peagen-gateway",
        },
        headers={"DPoP": proof},
    )
    assert resp.status_code == status.HTTP_200_OK
    token = resp.json()["access_token"]
    claims = decode_jwt(token)
    assert claims.get("cnf", {}).get("jkt") == jkt

    proof2 = create_proof(private_pem, "GET", "http://test/userinfo")
    headers = {"Authorization": f"Bearer {token}", "DPoP": proof2}
    ok = await async_client.get("/userinfo", headers=headers)
    assert ok.status_code == status.HTTP_200_OK
    assert ok.json()["sub"] == str(worker.id)

    fail = await async_client.get(
        "/userinfo", headers={"Authorization": f"Bearer {token}"}
    )
    assert fail.status_code == status.HTTP_401_UNAUTHORIZED
