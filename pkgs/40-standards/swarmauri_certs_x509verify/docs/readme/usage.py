# README example: verify and parse a development certificate
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from swarmauri_certs_x509verify import X509VerifyService


def issue_dev_certificate() -> bytes:
    private_key = ec.generate_private_key(ec.SECP256R1())
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "example.test")]
    )
    now = datetime.now(timezone.utc)

    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("example.test")]),
            critical=False,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .sign(private_key=private_key, algorithm=hashes.SHA256())
    )

    return certificate.public_bytes(serialization.Encoding.PEM)


async def main() -> dict[str, dict[str, Any]]:
    certificate_pem = issue_dev_certificate()
    service = X509VerifyService()

    parsed = await service.parse_cert(certificate_pem)
    verification = await service.verify_cert(
        certificate_pem, trust_roots=[certificate_pem]
    )

    return {"parsed": parsed, "verification": verification}


example_result = asyncio.run(main())
print(example_result["parsed"]["subject"])
print(example_result["verification"]["valid"])
