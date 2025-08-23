from __future__ import annotations

import datetime
import secrets
from typing import Any, Dict, Iterable, Literal, Optional, Sequence

from cryptography import x509
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    CertBytes,
    CertExtensionSpec,
    CsrBytes,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef


def _name_from_spec(spec: SubjectSpec) -> x509.Name:
    rdns = []
    if "C" in spec:
        rdns.append(x509.NameAttribute(NameOID.COUNTRY_NAME, spec["C"]))
    if "ST" in spec:
        rdns.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, spec["ST"]))
    if "L" in spec:
        rdns.append(x509.NameAttribute(NameOID.LOCALITY_NAME, spec["L"]))
    if "O" in spec:
        rdns.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, spec["O"]))
    if "OU" in spec:
        rdns.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, spec["OU"]))
    if "CN" in spec:
        rdns.append(x509.NameAttribute(NameOID.COMMON_NAME, spec["CN"]))
    if "emailAddress" in spec:
        rdns.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, spec["emailAddress"]))
    return x509.Name(rdns)


def _apply_extensions(
    builder: x509.CertificateBuilder | x509.CertificateSigningRequestBuilder,
    exts: Optional[CertExtensionSpec],
    *,
    ca: bool = False,
) -> x509.CertificateBuilder | x509.CertificateSigningRequestBuilder:
    if not exts:
        exts = {}
    if "basic_constraints" in exts:
        bc = exts["basic_constraints"]
        builder = builder.add_extension(
            x509.BasicConstraints(
                ca=bc.get("ca", False), path_length=bc.get("path_len")
            ),
            critical=True,
        )
    else:
        builder = builder.add_extension(
            x509.BasicConstraints(ca=ca, path_length=None),
            critical=True,
        )

    if "subject_alt_name" in exts:
        san = exts["subject_alt_name"]
        names = []
        for dns in san.get("dns", []):
            names.append(x509.DNSName(dns))
        for ip in san.get("ip", []):
            names.append(x509.IPAddress(ip))
        for uri in san.get("uri", []):
            names.append(x509.UniformResourceIdentifier(uri))
        for email in san.get("email", []):
            names.append(x509.RFC822Name(email))
        builder = builder.add_extension(
            x509.SubjectAlternativeName(names),
            critical=False,
        )

    if "extended_key_usage" in exts:
        ekus = []
        for oid in exts["extended_key_usage"].get("oids", []):
            if oid == "serverAuth":
                ekus.append(ExtendedKeyUsageOID.SERVER_AUTH)
            elif oid == "clientAuth":
                ekus.append(ExtendedKeyUsageOID.CLIENT_AUTH)
            else:
                ekus.append(x509.ObjectIdentifier(oid))
        builder = builder.add_extension(
            x509.ExtendedKeyUsage(ekus),
            critical=False,
        )

    return builder


class LocalCaCertService(CertServiceBase):
    """Local CA that can create a CA cert, sign CSRs, and verify certificates."""

    type: Literal["LocalCaCertService"] = "LocalCaCertService"

    def supports(self) -> Dict[str, Iterable[str]]:
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "EC-P256", "Ed25519"),
            "sig_algs": ("RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
            "features": ("csr", "self_signed", "sign_from_csr", "verify", "parse"),
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
        sk = serialization.load_pem_private_key(key.material, password=None)
        csr_builder = x509.CertificateSigningRequestBuilder().subject_name(
            _name_from_spec(subject)
        )
        if san:
            csr_builder = _apply_extensions(
                csr_builder,
                {"subject_alt_name": san},
            )
        algorithm = (
            None if isinstance(sk, ed25519.Ed25519PrivateKey) else hashes.SHA256()
        )
        csr = csr_builder.sign(sk, algorithm)
        return csr.public_bytes(
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )

    async def create_self_signed(
        self,
        key: KeyRef,
        subject: SubjectSpec,
        *,
        serial: Optional[int] = None,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> CertBytes:
        sk = serialization.load_pem_private_key(key.material, password=None)
        pub = sk.public_key()
        builder = (
            x509.CertificateBuilder()
            .subject_name(_name_from_spec(subject))
            .issuer_name(_name_from_spec(subject))
            .public_key(pub)
            .serial_number(serial or secrets.randbits(64))
            .not_valid_before(
                datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
            )
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        )
        builder = _apply_extensions(builder, extensions, ca=True)
        algorithm = (
            None if isinstance(sk, ed25519.Ed25519PrivateKey) else hashes.SHA256()
        )
        cert = builder.sign(private_key=sk, algorithm=algorithm)
        return cert.public_bytes(
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )

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
        csr_obj = (
            x509.load_pem_x509_csr(csr)
            if b"BEGIN" in csr
            else x509.load_der_x509_csr(csr)
        )
        ca_sk = serialization.load_pem_private_key(ca_key.material, password=None)
        ca_name = csr_obj.subject if issuer is None else _name_from_spec(issuer)

        builder = (
            x509.CertificateBuilder()
            .subject_name(csr_obj.subject)
            .issuer_name(ca_name)
            .public_key(csr_obj.public_key())
            .serial_number(serial or secrets.randbits(64))
            .not_valid_before(
                datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
            )
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        )
        builder = _apply_extensions(builder, extensions, ca=False)
        algorithm = (
            None if isinstance(ca_sk, ed25519.Ed25519PrivateKey) else hashes.SHA256()
        )
        cert = builder.sign(private_key=ca_sk, algorithm=algorithm)
        return cert.public_bytes(
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )

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
        c = (
            x509.load_pem_x509_certificate(cert)
            if b"BEGIN" in cert
            else x509.load_der_x509_certificate(cert)
        )
        now = datetime.datetime.utcnow()
        if not (c.not_valid_before <= now <= c.not_valid_after):
            return {"valid": False, "reason": "expired_or_not_yet_valid"}
        return {
            "valid": True,
            "reason": None,
            "subject": c.subject.rfc4514_string(),
            "issuer": c.issuer.rfc4514_string(),
        }

    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        c = (
            x509.load_pem_x509_certificate(cert)
            if b"BEGIN" in cert
            else x509.load_der_x509_certificate(cert)
        )
        out: Dict[str, Any] = {
            "serial": c.serial_number,
            "issuer": c.issuer.rfc4514_string(),
            "subject": c.subject.rfc4514_string(),
            "not_before": int(c.not_valid_before.timestamp()),
            "not_after": int(c.not_valid_after.timestamp()),
        }
        if include_extensions:
            out["extensions"] = [ext.oid.dotted_string for ext in c.extensions]
        return out
