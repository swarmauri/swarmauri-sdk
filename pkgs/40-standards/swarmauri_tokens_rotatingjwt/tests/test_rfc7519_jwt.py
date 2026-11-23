import pytest


from swarmauri_core.crypto.types import JWAAlg


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jwt_claims_roundtrip(service) -> None:
    token = await service.mint(
        {"foo": "bar"},
        alg=JWAAlg.HS256,
        audience="aud",
        subject="subj",
        issuer="issuer",
    )
    decoded = await service.verify(token, audience="aud")
    assert decoded["iss"] == "issuer"
    assert decoded["foo"] == "bar"
    assert decoded["sub"] == "subj"
