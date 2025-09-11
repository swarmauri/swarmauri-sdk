import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import AuthorityInformationAccessOID, NameOID

from swarmauri_cert_ocspverify import OcspVerifyService


def _make_cert(with_ocsp: bool = True) -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example")])
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(
            datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
        )
        .not_valid_after(
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
        )
    )
    if with_ocsp:
        builder = builder.add_extension(
            x509.AuthorityInformationAccess(
                [
                    x509.AccessDescription(
                        AuthorityInformationAccessOID.OCSP,
                        x509.UniformResourceIdentifier("http://ocsp.test/"),
                    )
                ]
            ),
            critical=False,
        )
    cert = builder.sign(private_key=key, algorithm=hashes.SHA256())
    return cert.public_bytes(serialization.Encoding.PEM)


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_parse_cert_extracts_ocsp_url() -> None:
    cert_pem = _make_cert()
    svc = OcspVerifyService()
    parsed = await svc.parse_cert(cert_pem)
    assert parsed["ocsp_urls"] == ["http://ocsp.test/"]


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_verify_cert_without_ocsp_returns_reason() -> None:
    cert_pem = _make_cert(with_ocsp=False)
    svc = OcspVerifyService()
    result = await svc.verify_cert(cert_pem, intermediates=[cert_pem])
    assert result["valid"] is False
    assert result["reason"] == "no_ocsp_url"
