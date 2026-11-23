import binascii
import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hkdf_rfc5869(provider):
    ikm = binascii.unhexlify("0b" * 22)
    salt = binascii.unhexlify("000102030405060708090a0b0c")
    info = binascii.unhexlify("f0f1f2f3f4f5f6f7f8f9")
    okm = await provider.hkdf(ikm, salt=salt, info=info, length=42)
    assert okm.hex() == (
        "3cb25f25faacd57a90434f64d0362f2a"
        "2d2d0a90cf1a5a4c5db02d56ecc4c5bf"
        "34007208d5b887185865"
    )
