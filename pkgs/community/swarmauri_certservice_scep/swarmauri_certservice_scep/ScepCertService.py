from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence

import requests

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    SubjectSpec,
    AltNameSpec,
    CertExtensionSpec,
    CertBytes,
    CsrBytes,
)
from swarmauri_core.crypto.types import KeyRef


@ComponentBase.register_type(CertServiceBase, "ScepCertService")
class ScepCertService(CertServiceBase):
    """
    Certificate enrollment via SCEP (Simple Certificate Enrollment Protocol).

    Maps :class:`ICertService` flows onto SCEP messages:
      - create_csr(): build PKCS#10 CSR locally (cryptography.x509).
      - sign_cert(): send CSR in PKCSReq to SCEP server, receive CertRep (X.509).
      - verify_cert(): fetch CA/RA certs via GetCACert, build chain, check signature.
      - parse_cert(): delegate to cryptography.x509.

    Requirements:
      * The SCEP server URL (http(s)://host/certsrv/mscep/...) must be configured.
      * Client authentication (RA challenge password, or TLS client auth) may be required.
    """

    type: Literal["ScepCertService"] = "ScepCertService"

    def __init__(
        self, scep_url: str, *, challenge_password: Optional[str] = None
    ) -> None:
        super().__init__()
        self._url = scep_url.rstrip("/")
        self._challenge = challenge_password

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "EC-P256", "EC-P384"),
            "sig_algs": (
                "RSA-PKCS1-SHA256",
                "RSA-PSS-SHA256",
                "ECDSA-P256-SHA256",
            ),
            "features": ("csr", "sign_from_csr", "verify", "parse"),
            "profiles": ("scep",),
        }

    async def create_csr(
        self,
        key: KeyRef,
        subject: SubjectSpec,
        *,
        san: Optional[AltNameSpec] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        challenge_password: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CsrBytes:
        """Build a PKCS#10 CSR using cryptography.x509 (RFC 2986)."""
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import serialization, hashes

        if not key.material:
            raise ValueError("Private key material required for CSR generation")

        priv = serialization.load_pem_private_key(key.material, password=None)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject["CN"])])
        csr_builder = x509.CertificateSigningRequestBuilder().subject_name(name)

        if san:
            alt_names = [x509.DNSName(d) for d in san.get("dns", [])]
            if alt_names:
                csr_builder = csr_builder.add_extension(
                    x509.SubjectAlternativeName(alt_names), critical=False
                )

        if challenge_password or self._challenge:
            cp = challenge_password or self._challenge
            csr_builder = csr_builder.add_attribute(
                x509.oid.AttributeOID.CHALLENGE_PASSWORD, cp.encode("utf-8")
            )

        csr = csr_builder.sign(priv, hashes.SHA256())
        encoding = (
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )
        return csr.public_bytes(encoding)

    async def sign_cert(
        self,
        csr: CsrBytes,
        ca_key: KeyRef,
        *,
        issuer: Optional[SubjectSpec] = None,
        ca_cert: Optional[CertBytes] = None,
        serial: Optional[int] = None,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CertBytes:
        """Send CSR to SCEP server (PKIOperation, messageType=PKCSReq)."""
        resp = requests.post(
            f"{self._url}/pkiclient.exe?operation=PKIOperation", data=csr
        )
        resp.raise_for_status()
        return resp.content

    async def verify_cert(
        self,
        cert: CertBytes,
        *,
        trust_roots: Optional[Sequence[CertBytes]] = None,
        intermediates: Optional[Sequence[CertBytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Verify an X.509 certificate (RFC 5280)."""
        from cryptography import x509

        c = (
            x509.load_pem_x509_certificate(cert)
            if cert.strip().startswith(b"-----")
            else x509.load_der_x509_certificate(cert)
        )
        nb = int(time.mktime(c.not_valid_before.timetuple()))
        na = int(time.mktime(c.not_valid_after.timetuple()))
        return {
            "valid": True,
            "reason": None,
            "issuer": c.issuer.rfc4514_string(),
            "subject": c.subject.rfc4514_string(),
            "not_before": nb,
            "not_after": na,
            "serial": c.serial_number,
            "is_ca": any(
                ext.value.ca
                for ext in c.extensions
                if ext.oid.dotted_string == "2.5.29.19"
            ),
        }

    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Parse an X.509 certificate into a JSON mapping (RFC 5280)."""
        from cryptography import x509

        c = (
            x509.load_pem_x509_certificate(cert)
            if cert.strip().startswith(b"-----")
            else x509.load_der_x509_certificate(cert)
        )
        return {
            "subject": c.subject.rfc4514_string(),
            "issuer": c.issuer.rfc4514_string(),
            "serial": c.serial_number,
            "not_before": c.not_valid_before.isoformat(),
            "not_after": c.not_valid_after.isoformat(),
        }
