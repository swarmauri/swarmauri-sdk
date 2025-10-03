from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed448, ed25519
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from pydantic import Field
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    BasicConstraintsSpec,
    CertExtensionSpec,
    ExtendedKeyUsageSpec,
    KeyUsageSpec,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef

_OID_MAP = {
    "serverAuth": ExtendedKeyUsageOID.SERVER_AUTH,
    "clientAuth": ExtendedKeyUsageOID.CLIENT_AUTH,
    "codeSigning": ExtendedKeyUsageOID.CODE_SIGNING,
    "emailProtection": ExtendedKeyUsageOID.EMAIL_PROTECTION,
    "timeStamping": ExtendedKeyUsageOID.TIME_STAMPING,
    "OCSPSigning": ExtendedKeyUsageOID.OCSP_SIGNING,
}


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


def _name_from_subject(spec: SubjectSpec) -> x509.Name:
    rdns = []
    if "C" in spec and spec["C"]:
        rdns.append(x509.NameAttribute(NameOID.COUNTRY_NAME, spec["C"]))
    if "ST" in spec and spec["ST"]:
        rdns.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, spec["ST"]))
    if "L" in spec and spec["L"]:
        rdns.append(x509.NameAttribute(NameOID.LOCALITY_NAME, spec["L"]))
    if "O" in spec and spec["O"]:
        rdns.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, spec["O"]))
    if "OU" in spec and spec["OU"]:
        rdns.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, spec["OU"]))
    if "emailAddress" in spec and spec["emailAddress"]:
        rdns.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, spec["emailAddress"]))
    if "CN" in spec and spec["CN"]:
        rdns.append(x509.NameAttribute(NameOID.COMMON_NAME, spec["CN"]))

    extra = spec.get("extra_rdns") or {}
    for k, v in extra.items():
        if not v:
            continue
        rdns.append(
            x509.NameAttribute(
                x509.ObjectIdentifier(k) if k.count(".") >= 2 else NameOID.COMMON_NAME,
                v,
            )
        )
    return x509.Name(rdns)


def _san_from_spec(san: Optional[AltNameSpec]) -> Optional[x509.SubjectAlternativeName]:
    if not san:
        return None
    gns = []
    for d in san.get("dns") or []:
        gns.append(x509.DNSName(d))
    for ip in san.get("ip") or []:
        gns.append(x509.IPAddress(x509.ipaddress.ip_address(ip)))  # type: ignore[attr-defined]
    for uri in san.get("uri") or []:
        gns.append(x509.UniformResourceIdentifier(uri))
    for email in san.get("email") or []:
        gns.append(x509.RFC822Name(email))
    return x509.SubjectAlternativeName(gns) if gns else None


def _eku_from_spec(
    eku: Optional[ExtendedKeyUsageSpec],
) -> Optional[x509.ExtendedKeyUsage]:
    if not eku:
        return None
    items = []
    for token in eku.get("oids") or []:
        if token in _OID_MAP:
            items.append(_OID_MAP[token])
        else:
            items.append(x509.ObjectIdentifier(token))
    return x509.ExtendedKeyUsage(items) if items else None


def _ku_from_spec(ku: Optional[KeyUsageSpec]) -> Optional[x509.KeyUsage]:
    if not ku:
        return None
    return x509.KeyUsage(
        digital_signature=bool(ku.get("digital_signature", False)),
        content_commitment=bool(ku.get("content_commitment", False)),
        key_encipherment=bool(ku.get("key_encipherment", False)),
        data_encipherment=bool(ku.get("data_encipherment", False)),
        key_agreement=bool(ku.get("key_agreement", False)),
        key_cert_sign=bool(ku.get("key_cert_sign", False)),
        crl_sign=bool(ku.get("crl_sign", False)),
        encipher_only=bool(ku.get("encipher_only", False)),
        decipher_only=bool(ku.get("decipher_only", False)),
    )


def _bc_from_spec(
    bc: Optional[BasicConstraintsSpec],
) -> Optional[x509.BasicConstraints]:
    if not bc:
        return None
    return x509.BasicConstraints(
        ca=bool(bc.get("ca", False)), path_length=bc.get("path_len", None)
    )


def _choose_sig_hash(private_key) -> Optional[hashes.HashAlgorithm]:
    if isinstance(private_key, (ed25519.Ed25519PrivateKey, ed448.Ed448PrivateKey)):
        return None
    return hashes.SHA256()


@ComponentBase.register_type(CertServiceBase, "SelfSignedCertificate")
class SelfSignedCertificate(CertServiceBase):
    """Minimal self-signed certificate builder exposed as a cert service."""

    subject: SubjectSpec = Field(
        default_factory=lambda: SubjectSpec(CN="localhost")
    )
    san: Optional[AltNameSpec] = None
    extensions: Optional[CertExtensionSpec] = None
    not_before: Optional[int] = None
    not_after: Optional[int] = None
    lifetime_days: int = 365
    serial: Optional[int] = None
    output_der: bool = False
    password: Optional[bytes] = None

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "features": ("self_signed",),
            "key_algs": ("RSA", "ECDSA", "Ed25519", "Ed448"),
            "sig_algs": ("RSA-SHA256", "ECDSA-SHA256", "Ed25519", "Ed448"),
            "formats": ("PEM", "DER"),
        }

    def issue(
        self,
        key: KeyRef,
        *,
        subject: Optional[SubjectSpec] = None,
        san: Optional[AltNameSpec] = None,
        extensions: Optional[CertExtensionSpec] = None,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
        lifetime_days: Optional[int] = None,
        serial: Optional[int] = None,
        output_der: Optional[bool] = None,
        password: Optional[bytes] = None,
    ) -> bytes:
        if key.material is None:
            raise ValueError(
                "Self-signed issuance requires a private key in KeyRef.material (PEM)."
            )

        pwd = password if password is not None else self.password
        if (
            pwd is None
            and key.tags
            and isinstance(key.tags.get("passphrase"), (str, bytes))
        ):
            pwd = (
                key.tags["passphrase"].encode()
                if isinstance(key.tags["passphrase"], str)
                else key.tags["passphrase"]
            )

        private_key = serialization.load_pem_private_key(key.material, password=pwd)
        public_key = private_key.public_key()

        subject_spec = subject or self.subject
        subj = _name_from_subject(subject_spec)
        issuer = subj

        nb_epoch = not_before if not_before is not None else self.not_before
        na_epoch = not_after if not_after is not None else self.not_after

        if nb_epoch is not None:
            nb = datetime.fromtimestamp(int(nb_epoch), tz=timezone.utc)
        else:
            nb = _now_utc() - timedelta(seconds=300)

        if na_epoch is not None:
            na = datetime.fromtimestamp(int(na_epoch), tz=timezone.utc)
        else:
            life = lifetime_days if lifetime_days is not None else self.lifetime_days
            na = nb + timedelta(days=int(life))

        serial_number = (
            serial if serial is not None else self.serial or x509.random_serial_number()
        )

        builder = (
            x509.CertificateBuilder()
            .subject_name(subj)
            .issuer_name(issuer)
            .public_key(public_key)
            .serial_number(serial_number)
            .not_valid_before(nb)
            .not_valid_after(na)
        )

        ext_spec = extensions if extensions is not None else self.extensions

        bc = _bc_from_spec(ext_spec.get("basic_constraints")) if ext_spec else None
        if bc:
            builder = builder.add_extension(bc, critical=True)

        ku = _ku_from_spec(ext_spec.get("key_usage")) if ext_spec else None
        if ku:
            builder = builder.add_extension(ku, critical=True)

        eku = _eku_from_spec(ext_spec.get("extended_key_usage")) if ext_spec else None
        if eku:
            builder = builder.add_extension(eku, critical=False)

        san_spec = (
            ext_spec.get("subject_alt_name")
            if ext_spec and ext_spec.get("subject_alt_name")
            else san or self.san
        )
        san_ext = _san_from_spec(san_spec)
        if san_ext:
            builder = builder.add_extension(san_ext, critical=False)

        skid = x509.SubjectKeyIdentifier.from_public_key(public_key)
        builder = builder.add_extension(skid, critical=False)
        akid = x509.AuthorityKeyIdentifier.from_issuer_public_key(public_key)
        builder = builder.add_extension(akid, critical=False)

        if ext_spec and ext_spec.get("name_constraints"):
            nc = ext_spec["name_constraints"]
            permitted_dns = [x509.DNSName(d) for d in (nc.get("permitted_dns") or [])]
            excluded_dns = [x509.DNSName(d) for d in (nc.get("excluded_dns") or [])]
            permitted_ip = [
                x509.IPAddress(x509.ipaddress.ip_address(ip))
                for ip in (nc.get("permitted_ip") or [])
            ]  # type: ignore[attr-defined]
            excluded_ip = [
                x509.IPAddress(x509.ipaddress.ip_address(ip))
                for ip in (nc.get("excluded_ip") or [])
            ]  # type: ignore[attr-defined]
            permitted_uri = [
                x509.UniformResourceIdentifier(u)
                for u in (nc.get("permitted_uri") or [])
            ]
            excluded_uri = [
                x509.UniformResourceIdentifier(u)
                for u in (nc.get("excluded_uri") or [])
            ]
            permitted_email = [
                x509.RFC822Name(e) for e in (nc.get("permitted_email") or [])
            ]
            excluded_email = [
                x509.RFC822Name(e) for e in (nc.get("excluded_email") or [])
            ]

            builder = builder.add_extension(
                x509.NameConstraints(
                    permitted_subtrees=(
                        permitted_dns + permitted_ip + permitted_uri + permitted_email
                    )
                    or None,
                    excluded_subtrees=(
                        excluded_dns + excluded_ip + excluded_uri + excluded_email
                    )
                    or None,
                ),
                critical=True,
            )

        sig_hash = _choose_sig_hash(private_key)
        cert = builder.sign(private_key=private_key, algorithm=sig_hash)

        encoding = (
            serialization.Encoding.DER
            if (output_der if output_der is not None else self.output_der)
            else serialization.Encoding.PEM
        )
        return cert.public_bytes(encoding)

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
    ) -> bytes:
        san_override = opts.get("san") if opts else None
        lifetime_override = opts.get("lifetime_days") if opts else None
        password_override = opts.get("password") if opts else None
        if isinstance(password_override, str):
            password_override = password_override.encode()
        return self.issue(
            key,
            subject=subject,
            san=san_override,
            extensions=extensions,
            not_before=not_before,
            not_after=not_after,
            lifetime_days=lifetime_override,
            serial=serial,
            output_der=output_der,
            password=password_override,
        )

    @classmethod
    def tls_server(
        cls,
        common_name: str,
        dns_names: Sequence[str] = (),
        ip_addrs: Sequence[str] = (),
        lifetime_days: int = 397,
    ) -> "SelfSignedCertificate":
        subject: SubjectSpec = SubjectSpec(CN=common_name)  # type: ignore[call-arg]
        san = AltNameSpec(dns=list(dns_names), ip=list(ip_addrs))  # type: ignore[call-arg]
        ext: CertExtensionSpec = CertExtensionSpec(  # type: ignore[call-arg]
            basic_constraints=BasicConstraintsSpec(ca=False, path_len=None),  # type: ignore[call-arg]
            key_usage=KeyUsageSpec(  # type: ignore[call-arg]
                digital_signature=True,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            extended_key_usage=ExtendedKeyUsageSpec(oids=["serverAuth"]),  # type: ignore[call-arg]
            subject_alt_name=san,
        )
        return cls(
            subject=subject, san=san, extensions=ext, lifetime_days=lifetime_days
        )

    @classmethod
    def mTLS_client(
        cls,
        common_name: str,
        emails: Sequence[str] = (),
        lifetime_days: int = 365,
    ) -> "SelfSignedCertificate":
        subject: SubjectSpec = SubjectSpec(CN=common_name)  # type: ignore[call-arg]
        san = AltNameSpec(email=list(emails))  # type: ignore[call-arg]
        ext: CertExtensionSpec = CertExtensionSpec(  # type: ignore[call-arg]
            basic_constraints=BasicConstraintsSpec(ca=False, path_len=None),  # type: ignore[call-arg]
            key_usage=KeyUsageSpec(  # type: ignore[call-arg]
                digital_signature=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            extended_key_usage=ExtendedKeyUsageSpec(oids=["clientAuth"]),  # type: ignore[call-arg]
            subject_alt_name=san,
        )
        return cls(
            subject=subject, san=san, extensions=ext, lifetime_days=lifetime_days
        )
