import pytest

from tigrbl_spiffe.identity.svid_validator import SvidValidator


@pytest.mark.asyncio
async def test_validate_rejects_unknown_kind():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(kind="otp", material=b"token", bundle_id=None, ctx={})


@pytest.mark.asyncio
async def test_validate_requires_bytes_material():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(kind="jwt", material="token", bundle_id=None, ctx={})


@pytest.mark.asyncio
async def test_validate_enforces_minimum_x509_size():
    validator = SvidValidator()
    with pytest.raises(ValueError):
        await validator.validate(
            kind="x509", material=b"0" * 32, bundle_id=None, ctx={}
        )

    await validator.validate(kind="x509", material=b"1" * 64, bundle_id=None, ctx={})


@pytest.mark.asyncio
async def test_validate_accepts_jwt_token_bytes():
    validator = SvidValidator()
    await validator.validate(
        kind="jwt",
        material=b"header.payload.signature",
        bundle_id=None,
        ctx={},
    )
