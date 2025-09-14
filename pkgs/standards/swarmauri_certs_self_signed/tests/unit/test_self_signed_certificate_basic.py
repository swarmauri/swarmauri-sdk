import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509

from swarmauri_certs_self_signed import SelfSignedCertificate
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.test
@pytest.mark.unit
def test_issue_basic():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    keyref = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )
    cert_bytes = SelfSignedCertificate().issue(keyref)
    cert = x509.load_pem_x509_certificate(cert_bytes)
    assert cert.subject == cert.issuer
    assert (
        cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
        == "localhost"
    )
