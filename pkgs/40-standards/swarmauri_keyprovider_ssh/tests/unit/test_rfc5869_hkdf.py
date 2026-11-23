import pytest

from swarmauri_keyprovider_ssh import SshKeyProvider


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc5869_hkdf_vector() -> None:
    kp = SshKeyProvider()
    ikm = bytes.fromhex("0b" * 22)
    salt = bytes.fromhex("000102030405060708090a0b0c")
    info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
    okm = await kp.hkdf(ikm, salt=salt, info=info, length=42)
    expected = bytes.fromhex(
        "3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865"
    )
    assert okm == expected
