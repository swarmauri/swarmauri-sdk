"""Comprehensive CMS and S/MIME signing demonstrations using CMSSigner."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_core.signing.types import Signature
from swarmauri_signing_cms import CMSSigner


def build_ephemeral_identity(common_name: str) -> tuple[dict[str, object], str]:
    """Return a ``KeyRef`` dictionary and PEM trust anchor for demos."""

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = x509.Name(
        [
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Swarmauri Demo"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name),
        ]
    )
    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=7))
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()), False
        )
        .sign(private_key, hashes.SHA256())
    )

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)

    key_ref = {
        "kind": "pem",
        "private_key": private_key_pem,
        "certificate": certificate_pem,
    }
    trust_anchor = certificate.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    return key_ref, trust_anchor


async def cms_detached_signature(
    signer: CMSSigner,
    key_ref: dict[str, object],
    trust: Iterable[str],
) -> Signature:
    """Produce and verify a detached CMS signature for raw bytes."""

    payload = b"Important release payload"
    signatures = await signer.sign_bytes(
        key_ref,
        payload,
        alg="SHA256",
        opts={"attached": False, "encoding": "der"},
    )

    ok = await signer.verify_bytes(
        payload,
        signatures,
        opts={"trusted_certs": list(trust)},
    )
    assert ok, "Detached CMS verification failed"
    return signatures[0]


async def smime_attached_message(
    signer: CMSSigner,
    key_ref: dict[str, object],
    trust: Iterable[str],
) -> MIMEMultipart:
    """Build an RFC-compliant S/MIME signed message with CMS payload."""

    plaintext = """Dear Friend,

This message demonstrates how to build an S/MIME payload with CMSSigner.

Regards,
Swarmauri SDK
"""
    payload = plaintext.encode("utf-8")
    signatures = await signer.sign_bytes(
        key_ref,
        payload,
        opts={"attached": True, "encoding": "pem"},
    )

    ok = await signer.verify_bytes(
        payload,
        signatures,
        opts={"trusted_certs": list(trust)},
    )
    assert ok, "S/MIME verification failed"

    signature = signatures[0]
    envelope = MIMEMultipart(
        "signed", protocol="application/pkcs7-signature", micalg="sha-256"
    )
    envelope["Subject"] = "S/MIME Demonstration"
    envelope["From"] = "demo@swarmauri.test"
    envelope["To"] = "recipient@example.com"

    envelope.attach(MIMEText(plaintext, _charset="utf-8"))
    signature_part = MIMEApplication(
        signature.artifact,
        _subtype="pkcs7-signature",
        Name="smime.p7s",
    )
    encoders.encode_base64(signature_part)
    signature_part.add_header("Content-Disposition", "attachment", filename="smime.p7s")
    envelope.attach(signature_part)
    return envelope


def describe_certificate_chain(signature: Signature) -> list[str]:
    """Return human readable subject strings extracted from ``cert_chain_der``."""

    subjects: list[str] = []
    for entry in signature.cert_chain_der or ():
        cert = x509.load_der_x509_certificate(entry)
        subjects.append(cert.subject.rfc4514_string())
    return subjects


async def main() -> None:
    key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
    signer = CMSSigner()

    signature = await cms_detached_signature(signer, key_ref, [trust_anchor])
    print("Detached CMS signature produced using:", signature.alg)

    smime_message = await smime_attached_message(signer, key_ref, [trust_anchor])
    print(
        "S/MIME message assembled with parts:",
        [part.get_content_type() for part in smime_message.get_payload()],
    )

    subjects = describe_certificate_chain(signature)
    print("Certificates embedded in signature:", subjects)


if __name__ == "__main__":
    asyncio.run(main())
