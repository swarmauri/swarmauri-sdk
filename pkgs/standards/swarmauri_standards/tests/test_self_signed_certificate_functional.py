import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography import x509

from swarmauri_standards import SelfSignedCertificate
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.test
@pytest.mark.i9n
def test_tls_server_preset():
    key = ed25519.Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    keyref = KeyRef(
        kid="k2",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )
    cert_bytes = SelfSignedCertificate.tls_server(
        "example.com", dns_names=["example.com"]
    ).issue(keyref)
    cert = x509.load_pem_x509_certificate(cert_bytes)
    san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    assert "example.com" in san.value.get_values_for_type(x509.DNSName)
