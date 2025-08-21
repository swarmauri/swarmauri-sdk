"""Tests for RFC 5280 Basic Constraints requirements."""

import pytest
from cryptography import x509


@pytest.mark.asyncio
async def test_basic_constraints_default(service_keyref):
    svc, key = service_keyref
    cert_pem = await svc.create_self_signed(key, {"CN": "example.com"})
    cert = x509.load_pem_x509_certificate(cert_pem)
    bc = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
    assert not bc.ca
