"""Shared fixtures for CfsslCertService tests."""

from __future__ import annotations

import datetime as dt
from typing import Tuple

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


@pytest.fixture(scope="session")
def cert_and_csr() -> Tuple[bytes, bytes]:
    """Generate a self-signed certificate and a matching CSR."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "test.example")]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(dt.datetime.utcnow() - dt.timedelta(days=1))
        .not_valid_after(dt.datetime.utcnow() + dt.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("test.example")]), critical=False
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False
        )
        .sign(key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
        .sign(key, hashes.SHA256())
    )
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)
    return cert_pem, csr_pem


@pytest.fixture(scope="session")
def cert_pem(cert_and_csr: Tuple[bytes, bytes]) -> bytes:
    """Return certificate PEM."""
    return cert_and_csr[0]


@pytest.fixture(scope="session")
def csr_pem(cert_and_csr: Tuple[bytes, bytes]) -> bytes:
    """Return CSR PEM."""
    return cert_and_csr[1]
