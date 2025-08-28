import datetime
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


@pytest.fixture
def cert_and_crl():
    def _make(*, revoked: bool = False, expired: bool = False):
        ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CA")])
        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=1))
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=1))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True
            )
            .sign(private_key=ca_key, algorithm=hashes.SHA256())
        )

        ee_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        nb = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        na = (
            datetime.datetime.utcnow() - datetime.timedelta(days=1)
            if expired
            else datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )
        cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "EE")]))
            .issuer_name(ca_cert.subject)
            .public_key(ee_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(nb)
            .not_valid_after(na)
            .sign(private_key=ca_key, algorithm=hashes.SHA256())
        )

        crl_builder = (
            x509.CertificateRevocationListBuilder()
            .issuer_name(ca_cert.subject)
            .last_update(datetime.datetime.utcnow() - datetime.timedelta(days=1))
            .next_update(datetime.datetime.utcnow() + datetime.timedelta(days=1))
        )
        if revoked:
            revoked_cert = (
                x509.RevokedCertificateBuilder()
                .serial_number(cert.serial_number)
                .revocation_date(datetime.datetime.utcnow())
                .build()
            )
            crl_builder = crl_builder.add_revoked_certificate(revoked_cert)
        crl = crl_builder.sign(private_key=ca_key, algorithm=hashes.SHA256())
        return (
            cert.public_bytes(serialization.Encoding.PEM),
            [crl.public_bytes(serialization.Encoding.PEM)],
        )

    return _make
