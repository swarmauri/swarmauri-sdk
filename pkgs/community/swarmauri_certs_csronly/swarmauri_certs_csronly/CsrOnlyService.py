from __future__ import annotations

from typing import Any, Dict, Iterable, Literal, Mapping, Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, ed448
from cryptography.x509.oid import NameOID

from swarmauri_base.certs import CertServiceBase
from swarmauri_core.certs.ICertService import (
    SubjectSpec,
    AltNameSpec,
    CertExtensionSpec,
    CsrBytes,
)
from swarmauri_core.crypto.types import KeyRef


class CsrOnlyService(CertServiceBase):
    """Service that only builds PKCS#10 CSRs.

    Implements CSR generation as defined in RFC 2986 and leverages X.509 naming
    and extension rules from RFC 5280. This service does **not** issue or verify
    certificates.
    """

    type: Literal["CsrOnlyService"] = "CsrOnlyService"

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "RSA-4096", "EC-P256", "Ed25519"),
            "sig_algs": ("RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
            "features": ("csr",),
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
        """Build a PKCS#10 CSR from a KeyRef containing a private key PEM."""
        if key.material is None:
            raise ValueError(
                "KeyRef.material with private key PEM is required for CSR creation"
            )

        sk = serialization.load_pem_private_key(key.material, password=None)

        name_attrs = []
        if "CN" in subject:
            name_attrs.append(x509.NameAttribute(NameOID.COMMON_NAME, subject["CN"]))
        if "C" in subject:
            name_attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, subject["C"]))
        if "ST" in subject:
            name_attrs.append(
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject["ST"])
            )
        if "L" in subject:
            name_attrs.append(x509.NameAttribute(NameOID.LOCALITY_NAME, subject["L"]))
        if "O" in subject:
            name_attrs.append(
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject["O"])
            )
        if "OU" in subject:
            name_attrs.append(
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, subject["OU"])
            )
        if "emailAddress" in subject:
            name_attrs.append(
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, subject["emailAddress"])
            )

        csr_builder = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name(name_attrs)
        )

        if san:
            san_entries = []
            for d in san.get("dns", []):
                san_entries.append(x509.DNSName(d))
            for i in san.get("ip", []):
                san_entries.append(x509.IPAddress(i))
            for u in san.get("uri", []):
                san_entries.append(x509.UniformResourceIdentifier(u))
            for e in san.get("email", []):
                san_entries.append(x509.RFC822Name(e))
            if san_entries:
                csr_builder = csr_builder.add_extension(
                    x509.SubjectAlternativeName(san_entries), critical=False
                )

        if challenge_password:
            csr_builder = csr_builder.add_attribute(
                x509.OID_PKCS9_CHALLENGE_PASSWORD, challenge_password.encode()
            )

        if extensions and "basic_constraints" in extensions:
            bc = extensions["basic_constraints"]
            csr_builder = csr_builder.add_extension(
                x509.BasicConstraints(
                    ca=bc.get("ca", False), path_length=bc.get("path_len")
                ),
                critical=True,
            )

        sig = (
            None
            if isinstance(sk, (ed25519.Ed25519PrivateKey, ed448.Ed448PrivateKey))
            else hashes.SHA256()
        )
        csr = csr_builder.sign(private_key=sk, algorithm=sig)

        return csr.public_bytes(
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )

    async def create_self_signed(self, *a, **kw):  # pragma: no cover - not implemented
        raise NotImplementedError("CsrOnlyService does not create certificates")

    async def sign_cert(self, *a, **kw):  # pragma: no cover - not implemented
        raise NotImplementedError("CsrOnlyService does not sign certificates")

    async def verify_cert(self, *a, **kw):  # pragma: no cover - not implemented
        raise NotImplementedError("CsrOnlyService does not verify certificates")

    async def parse_cert(self, *a, **kw):  # pragma: no cover - not implemented
        raise NotImplementedError("CsrOnlyService does not parse certificates")
