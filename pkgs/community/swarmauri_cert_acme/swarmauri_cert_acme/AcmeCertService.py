from __future__ import annotations

import datetime
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence

from acme import client, messages
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    CertBytes,
    CertExtensionSpec,
    CsrBytes,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef

ACME_DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"


class AcmeCertService(CertServiceBase):
    """ACME v2 certificate service implementing RFC 8555.

    This service handles PKCS#10 CSRs (RFC 2986) and returns X.509
    certificates (RFC 5280).
    """

    type: Literal["AcmeCertService"] = "AcmeCertService"

    def __init__(
        self,
        account_key: KeyRef,
        *,
        directory_url: str = ACME_DIRECTORY_URL,
        contact_emails: Optional[Sequence[str]] = None,
    ) -> None:
        super().__init__()
        self._account_key = account_key
        self._dir_url = directory_url
        self._contact = contact_emails or []

        self._client: Optional[client.ClientV2] = None

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "EC-P256", "EC-P384"),
            "sig_algs": ("RS256", "ES256", "ES384"),
            "features": ("acme", "sign_from_csr", "verify"),
            "profiles": ("server", "client"),
        }

    def _ensure_client(self) -> client.ClientV2:
        if self._client:
            return self._client

        if self._account_key.material is None:
            raise RuntimeError("Account key material is required for ACME")
        acc_key = serialization.load_pem_private_key(
            self._account_key.material, password=None
        )
        net = client.ClientNetwork(acc_key, user_agent="swarmauri-acme/1.0")
        directory = messages.Directory.from_json(net.get(self._dir_url).json())
        self._client = client.ClientV2(directory, net=net)
        return self._client

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
        if key.material is None:
            raise RuntimeError("Private key material required to build CSR")
        priv = serialization.load_pem_private_key(key.material, password=None)
        builder = x509.CertificateSigningRequestBuilder()

        name_attrs = []
        if "CN" in subject:
            name_attrs.append(
                x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, subject["CN"])
            )
        builder = builder.subject_name(x509.Name(name_attrs))

        if san and "dns" in san:
            san_ext = x509.SubjectAlternativeName([x509.DNSName(d) for d in san["dns"]])
            builder = builder.add_extension(san_ext, critical=False)

        algorithm = (
            hashes.SHA256()
            if isinstance(priv, (rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey))
            else None
        )
        csr = builder.sign(priv, algorithm)
        data = csr.public_bytes(
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )
        return data

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
        cl = self._ensure_client()
        order = cl.new_order(csr)
        finalized = cl.poll_and_finalize(order)
        pem = finalized.fullchain_pem.encode("utf-8")
        return pem if not output_der else finalized.fullchain_der

    async def create_self_signed(self, *a, **kw) -> CertBytes:  # pragma: no cover
        raise NotImplementedError("Self-signed not supported in AcmeCertService")

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
        c = x509.load_pem_x509_certificate(cert)
        now = datetime.datetime.utcnow()
        return {
            "valid": c.not_valid_before <= now <= c.not_valid_after,
            "issuer": c.issuer.rfc4514_string(),
            "subject": c.subject.rfc4514_string(),
            "not_before": int(c.not_valid_before.timestamp()),
            "not_after": int(c.not_valid_after.timestamp()),
        }

    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        c = x509.load_pem_x509_certificate(cert)
        return {
            "subject": c.subject.rfc4514_string(),
            "issuer": c.issuer.rfc4514_string(),
            "serial": c.serial_number,
            "not_before": int(c.not_valid_before.timestamp()),
            "not_after": int(c.not_valid_after.timestamp()),
        }
