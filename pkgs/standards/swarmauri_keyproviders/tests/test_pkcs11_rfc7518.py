"""Tests for RFC 7518 (JSON Web Algorithms) compliance."""

import pytest

from swarmauri_keyproviders.Pkcs11KeyProvider import Pkcs11KeyProvider


@pytest.mark.unit
def test_supported_algorithms() -> None:
    provider = Pkcs11KeyProvider.__new__(Pkcs11KeyProvider)
    provider._allow_aes = True
    provider._allow_ec = True
    provider._allow_rsa = True
    algs = provider.supports()["algs"]
    assert "AES256_GCM" in algs
    assert "ECDSA_P256_SHA256" in algs
    assert "RSA_OAEP_SHA256" in algs
    assert "RSA_PSS_SHA256" in algs
