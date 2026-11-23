"""Tests for RFC 5869 HKDF compliance."""

import pytest

from swarmauri_keyprovider_file import FileKeyProvider


@pytest.mark.asyncio
@pytest.mark.test
@pytest.mark.unit
async def test_hkdf_length(tmp_path):
    provider = FileKeyProvider(tmp_path)
    out = await provider.hkdf(b"ikm", salt=b"salt", info=b"info", length=42)
    assert len(out) == 42
