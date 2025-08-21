"""Tests for RFC 7468 PEM encoding and decoding."""

import pytest

from swarmauri_cert_cfssl.CfsslCertService import _der_to_pem, _pem_to_der


@pytest.mark.unit
def test_pem_der_roundtrip(cert_pem: bytes) -> None:
    """Ensure PEM <-> DER round-trip as defined in RFC 7468."""
    der = _pem_to_der(cert_pem)
    pem = _der_to_pem(der)
    assert pem.strip() == cert_pem.strip()
