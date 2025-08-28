"""PEM encoding tests per RFC 7468."""

from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from swarmauri_certs_azure.certs.AzureKeyVaultCertService import _pem_cert


def _make_der_cert() -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(1)
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.DER)


def test_pem_cert_rfc7468() -> None:
    der = _make_der_cert()
    pem = _pem_cert(der)
    assert pem.startswith(b"-----BEGIN CERTIFICATE-----")
    assert pem.strip().endswith(b"END CERTIFICATE-----")
