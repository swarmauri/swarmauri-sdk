import pytest

from swarmauri_keyprovider_pkcs11 import Pkcs11KeyProvider


@pytest.mark.unit
def test_supported_algorithms() -> None:
    """Supported algorithms should align with RFC7518 identifiers."""
    provider = object.__new__(Pkcs11KeyProvider)
    provider._allow_aes = True
    provider._allow_ec = True
    provider._allow_rsa = True
    algs = set(Pkcs11KeyProvider.supports(provider)["algs"])
    assert algs == {
        "AES256_GCM",
        "ECDSA_P256_SHA256",
        "RSA_OAEP_SHA256",
        "RSA_PSS_SHA256",
    }
