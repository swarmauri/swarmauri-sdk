"""Tests for RFC 5280 compliance."""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509

from swarmauri_standards import SelfSignedCertificate
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.test
@pytest.mark.unit
def test_basic_constraints_and_key_usage():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    keyref = KeyRef(
        kid="k4",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )
    cert_bytes = SelfSignedCertificate.tls_server(
        "example.com", dns_names=["example.com"]
    ).issue(keyref)
    cert = x509.load_pem_x509_certificate(cert_bytes)
    bc = cert.extensions.get_extension_for_class(x509.BasicConstraints)
    assert bc.value.ca is False
    ku = cert.extensions.get_extension_for_class(x509.KeyUsage)
    assert ku.value.digital_signature
    assert not ku.value.crl_sign
