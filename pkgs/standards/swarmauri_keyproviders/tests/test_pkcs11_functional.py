"""Functional tests for HKDF per RFC 5869."""

import asyncio
import pytest

from swarmauri_keyproviders.Pkcs11KeyProvider import Pkcs11KeyProvider


@pytest.mark.functional
def test_hkdf_deterministic() -> None:
    provider = Pkcs11KeyProvider.__new__(Pkcs11KeyProvider)
    result1 = asyncio.run(provider.hkdf(b"ikm", salt=b"salt", info=b"info", length=32))
    result2 = asyncio.run(provider.hkdf(b"ikm", salt=b"salt", info=b"info", length=32))
    assert result1 == result2
    assert len(result1) == 32
