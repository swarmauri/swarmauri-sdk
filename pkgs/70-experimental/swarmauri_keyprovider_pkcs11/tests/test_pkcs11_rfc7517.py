import pytest

from swarmauri_keyprovider_pkcs11 import Pkcs11KeyProvider
from swarmauri_keyprovider_pkcs11.Pkcs11KeyProvider import _IndexEntry
from swarmauri_core.key_providers.types import KeyAlg, KeyClass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_symmetric_jwk_placeholder() -> None:
    """Symmetric keys expose placeholder JWK per RFC7517."""
    provider = object.__new__(Pkcs11KeyProvider)
    provider._idx = {
        "sym": {
            1: _IndexEntry(
                kid="sym",
                version=1,
                label="lbl",
                klass=KeyClass.symmetric,
                alg=KeyAlg.AES256_GCM,
                handles={},
                tags={},
            )
        }
    }
    jwk = await Pkcs11KeyProvider.get_public_jwk(provider, "sym", 1)
    assert jwk == {"kty": "oct", "alg": "A256GCM", "kid": "sym.1"}
