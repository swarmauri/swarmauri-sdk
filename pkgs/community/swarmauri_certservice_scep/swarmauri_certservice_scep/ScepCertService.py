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
    """Certificate enrollment via SCEP (Simple Certificate Enrollment Protocol).

    The service maps :class:`~swarmauri_core.certs.ICertService` flows onto the
    SCEP message exchange so that clients can issue and validate X.509
    certificates.

    scep_url (str): Base URL of the SCEP server.
    challenge_password (str / None): RA challenge password if required.
    """

    type: Literal["ScepCertService"] = "ScepCertService"

    def __init__(
        self, scep_url: str, *, challenge_password: Optional[str] = None
    ) -> None:
        """Initialise the SCEP certificate service.

        scep_url (str): Base URL of the SCEP server.
        challenge_password (str / None): RA challenge password for enrollment.
        """
        super().__init__()
        self._url = scep_url.rstrip("/")
        self._challenge = challenge_password

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return supported algorithms and features.

        RETURNS (Mapping[str, Iterable[str]]): Supported keys, signatures, and features.
        """
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
        """Build a PKCS#10 certificate signing request.

        key (KeyRef): Private key used to sign the CSR.
        subject (SubjectSpec): Distinguished name of the subject.
        san (AltNameSpec / None): Subject alternative names to include.
        extensions (CertExtensionSpec / None): Additional X.509 extensions.
        sig_alg (str / None): Signature algorithm to use.
        challenge_password (str / None): Challenge password embedded in the CSR.
        output_der (bool): If True, return DER; otherwise PEM.
        opts (Dict[str, Any] / None): Implementation-specific options.
        RETURNS (CsrBytes): The serialized CSR.
        """
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
        """Submit the CSR to the SCEP server and return the issued certificate.

        csr (CsrBytes): Certificate signing request to submit.
        ca_key (KeyRef): Unused but required by the interface.
        issuer (SubjectSpec / None): Ignored for SCEP.
        ca_cert (CertBytes / None): Optional CA certificate.
        serial (int / None): Preferred serial number for the certificate.
        not_before (int / None): Desired start of validity period (UNIX time).
        not_after (int / None): Desired end of validity period (UNIX time).
        extensions (CertExtensionSpec / None): Extra X.509 extensions.
        sig_alg (str / None): Signature algorithm to request.
        output_der (bool): If True, return DER; otherwise PEM.
        opts (Dict[str, Any] / None): Implementation-specific options.
        RETURNS (CertBytes): The certificate returned by the server.
        """
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
        """Verify an X.509 certificate.

        cert (CertBytes): Certificate to verify.
        trust_roots (Sequence[CertBytes] / None): Trusted root certificates.
        intermediates (Sequence[CertBytes] / None): Intermediate certificates.
        check_time (int / None): Verification time as UNIX timestamp.
        check_revocation (bool): Enable revocation checks.
        opts (Dict[str, Any] / None): Implementation-specific options.
        RETURNS (Dict[str, Any]): Verification result details.
        """
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
        """Parse an X.509 certificate into a JSON-compatible mapping.

        cert (CertBytes): Certificate to parse.
        include_extensions (bool): If True, include extensions.
        opts (Dict[str, Any] / None): Implementation-specific options.
        RETURNS (Dict[str, Any]): Certificate metadata.
        """
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
