import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_random_bytes(provider):
    data = await provider.random_bytes(4)
    assert data == b"\x00" * 4


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hkdf_length(provider):
    out = await provider.hkdf(b"input", salt=b"salt", info=b"info", length=16)
    assert len(out) == 16
