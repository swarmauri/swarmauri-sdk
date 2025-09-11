import pytest

from swarmauri_keyprovider_local import LocalKeyProvider


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_random_and_hkdf() -> None:
    kp = LocalKeyProvider()
    rnd = await kp.random_bytes(16)
    assert len(rnd) == 16
    out = await kp.hkdf(b"ikm", salt=b"s", info=b"i", length=32)
    assert len(out) == 32
