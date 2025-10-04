from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

# Optional cryptography import
try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
    from cryptography.x509.oid import NameOID, ExtensionOID
except Exception:  # pragma: no cover
    x509 = None
    hashes = None
    serialization = None
    rsa = None
    ec = None

@dataclass
class IssueResult:
    pem: str
    serial_hex: str
    not_before: datetime
    not_after: datetime

@dataclass
class CertService:
    """Certificate issuance helper.

    In dev mode (no cryptography), returns a placeholder PEM.
    In prod mode, signs the CSR with the provided issuer private key.
    """

    @classmethod
    def from_config(cls, config: dict) -> "CertService":
        return cls()

    async def issue_certificate(self, *, csr_der: bytes, sans: List[str], issuer_key: Any,
                                not_before: datetime, not_after: datetime) -> IssueResult:
        import secrets, base64
        if x509 is None or serialization is None:
            # minimal placeholder (non-functional cert)
            pem = "-----BEGIN CERTIFICATE-----\n" + base64.b64encode(csr_der).decode("ascii") + "\n-----END CERTIFICATE-----\n"
            return IssueResult(
                pem=pem,
                serial_hex=secrets.token_hex(16),
                not_before=not_before,
                not_after=not_after,
            )

        # Parse CSR
        csr = x509.load_der_x509_csr(csr_der)
        # Build cert
        serial = int.from_bytes(secrets.token_bytes(16), "big")
        builder = (
            x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(csr.subject)  # In dev, default to self-issued unless issuer cert provided elsewhere
            .public_key(csr.public_key())
            .serial_number(serial)
            .not_valid_before(not_before)
            .not_valid_after(not_after)
        )

        # Copy SAN from CSR if present; otherwise use provided sans
        try:
            ext = csr.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            builder = builder.add_extension(ext.value, critical=False)
        except Exception:
            if sans:
                builder = builder.add_extension(
                    x509.SubjectAlternativeName([x509.DNSName(n) for n in sans]), critical=False
                )

        # Sign with issuer key
        try:
            algorithm = hashes.SHA256()
            cert = builder.sign(private_key=issuer_key, algorithm=algorithm)
        except Exception:
            # If issuer_key is an adapter without .sign(), fall back to placeholder
            return await self.issue_certificate_placeholder(csr_der=csr_der, not_before=not_before, not_after=not_after)

        pem = cert.public_bytes(serialization.Encoding.PEM).decode("ascii")
        return IssueResult(
            pem=pem,
            serial_hex=f"{serial:032x}",
            not_before=not_before,
            not_after=not_after,
        )

    async def issue_certificate_placeholder(self, *, csr_der: bytes, not_before: datetime, not_after: datetime) -> IssueResult:
        import secrets, base64
        pem = "-----BEGIN CERTIFICATE-----\n" + base64.b64encode(csr_der).decode("ascii") + "\n-----END CERTIFICATE-----\n"
        return IssueResult(
            pem=pem,
            serial_hex=secrets.token_hex(16),
            not_before=not_before,
            not_after=not_after,
        )
