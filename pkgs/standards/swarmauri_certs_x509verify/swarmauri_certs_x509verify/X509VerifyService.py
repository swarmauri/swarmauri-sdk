"""x509_verify_service.py

Service for parsing and verifying X.509 certificates.

The implementation focuses on basic RFC 5280 compliance for time
validation and a simple one-hop chain check. It is intended for test
and development environments rather than production PKI validation.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.x509.base import Certificate

from swarmauri_base.certs.CertServiceBase import CertServiceBase


class X509VerifyService(CertServiceBase):
    """Verify and parse X.509 certificates.

    Attributes:
        type: Component type identifier.
    """

    type: Literal["X509VerifyService"] = "X509VerifyService"

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return supported algorithms and features."""
        return {
            "key_algs": ("RSA", "EC", "Ed25519"),
            "sig_algs": ("RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
            "features": ("verify", "parse"),
        }

    async def verify_cert(
        self,
        cert: bytes,
        *,
        trust_roots: Optional[Sequence[bytes]] = None,
        intermediates: Optional[Sequence[bytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate a certificate against trust material.

        Args:
            cert (bytes): DER or PEM encoded certificate to verify.
            trust_roots (Optional[Sequence[bytes]]): Root certificates.
            intermediates (Optional[Sequence[bytes]]): Intermediate certs.
            check_time (Optional[int]): Override of verification time in UTC
                seconds since the epoch. Defaults to current time.
            check_revocation (bool): Placeholder for revocation checking. Not
                implemented.
            opts (Optional[Dict[str, Any]]): Additional options (unused).

        Returns:
            Dict[str, Any]: Structured validation result.
        """
        now = (
            datetime.datetime.utcfromtimestamp(check_time)
            if check_time
            else datetime.datetime.utcnow()
        )

        cert_obj = (
            x509.load_pem_x509_certificate(cert, default_backend())
            if b"-----BEGIN" in cert
            else x509.load_der_x509_certificate(cert, default_backend())
        )

        roots = [
            x509.load_pem_x509_certificate(root, default_backend())
            if b"-----BEGIN" in root
            else x509.load_der_x509_certificate(root, default_backend())
            for root in trust_roots or []
        ]

        inters = [
            x509.load_pem_x509_certificate(icert, default_backend())
            if b"-----BEGIN" in icert
            else x509.load_der_x509_certificate(icert, default_backend())
            for icert in intermediates or []
        ]

        valid_time = cert_obj.not_valid_before <= now <= cert_obj.not_valid_after

        chain_ok = False
        for candidate in roots + inters:
            if cert_obj.issuer == candidate.subject:
                try:
                    pub = candidate.public_key()
                    if isinstance(pub, rsa.RSAPublicKey):
                        pub.verify(
                            cert_obj.signature,
                            cert_obj.tbs_certificate_bytes,
                            padding.PKCS1v15(),
                            cert_obj.signature_hash_algorithm,
                        )
                    elif isinstance(pub, ec.EllipticCurvePublicKey):
                        pub.verify(
                            cert_obj.signature,
                            cert_obj.tbs_certificate_bytes,
                            ec.ECDSA(cert_obj.signature_hash_algorithm),
                        )
                    else:
                        pub.verify(
                            cert_obj.signature,
                            cert_obj.tbs_certificate_bytes,
                        )
                    chain_ok = True
                    break
                except Exception:  # pragma: no cover - best effort
                    pass

        return {
            "valid": valid_time and chain_ok,
            "reason": None if (valid_time and chain_ok) else "invalid_chain_or_time",
            "subject": cert_obj.subject.rfc4514_string(),
            "issuer": cert_obj.issuer.rfc4514_string(),
            "not_before": int(cert_obj.not_valid_before.timestamp()),
            "not_after": int(cert_obj.not_valid_after.timestamp()),
            "is_ca": any(
                ext.value.ca
                for ext in cert_obj.extensions
                if isinstance(ext.value, x509.BasicConstraints)
            ),
            "chain_len": 1 + len(inters),
            "revocation_checked": False,
        }

    async def parse_cert(
        self,
        cert: bytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Parse an X.509 certificate into metadata.

        Args:
            cert (bytes): DER or PEM encoded certificate.
            include_extensions (bool): Whether to parse SAN and EKU.
            opts (Optional[Dict[str, Any]]): Additional options (unused).

        Returns:
            Dict[str, Any]: Parsed certificate information.
        """
        cert_obj: Certificate = (
            x509.load_pem_x509_certificate(cert, default_backend())
            if b"-----BEGIN" in cert
            else x509.load_der_x509_certificate(cert, default_backend())
        )

        info: Dict[str, Any] = {
            "serial": cert_obj.serial_number,
            "issuer": cert_obj.issuer.rfc4514_string(),
            "subject": cert_obj.subject.rfc4514_string(),
            "not_before": int(cert_obj.not_valid_before.timestamp()),
            "not_after": int(cert_obj.not_valid_after.timestamp()),
            "sig_alg": cert_obj.signature_algorithm_oid._name,
        }

        if include_extensions:
            for ext in cert_obj.extensions:
                if isinstance(ext.value, x509.SubjectAlternativeName):
                    info["san"] = {"dns": ext.value.get_values_for_type(x509.DNSName)}
                if isinstance(ext.value, x509.ExtendedKeyUsage):
                    info["eku"] = [oid._name or oid.dotted_string for oid in ext.value]

        return info


__all__ = ["X509VerifyService"]
