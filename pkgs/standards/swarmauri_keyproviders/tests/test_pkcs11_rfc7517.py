"""Tests for RFC 7517 (JSON Web Key) compliance."""

import asyncio
import pytest

from swarmauri_core.keys.types import KeyAlg, KeyClass
from swarmauri_keyproviders.Pkcs11KeyProvider import Pkcs11KeyProvider, _IndexEntry


@pytest.mark.unit
def test_symmetric_jwk_placeholder() -> None:
    provider = Pkcs11KeyProvider.__new__(Pkcs11KeyProvider)
    provider._idx = {
        "kid": {
            1: _IndexEntry(
                kid="kid",
                version=1,
                label="lbl",
                klass=KeyClass.symmetric,
                alg=KeyAlg.AES256_GCM,
                handles={},
                tags={},
            )
        }
    }
    jwk = asyncio.run(provider.get_public_jwk("kid", 1))
    assert jwk["kty"] == "oct"
    assert jwk["alg"] == "A256GCM"
    assert jwk["kid"] == "kid.1"
