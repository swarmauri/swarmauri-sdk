from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, ed448
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

from swarmauri_core.crypto.types import KeyRef
from swarmauri_core.certs.ICertService import (
    SubjectSpec,
    AltNameSpec,
    CertExtensionSpec,
    KeyUsageSpec,
    ExtendedKeyUsageSpec,
    BasicConstraintsSpec,
)


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


@dataclass
class SelfSignedCertificate:
    """Minimal builder for self-signed X.509 certificates."""

    subject: SubjectSpec = field(default_factory=lambda: SubjectSpec(CN="localhost"))  # type: ignore[call-arg]
    san: Optional[AltNameSpec] = None
    extensions: Optional[CertExtensionSpec] = None
    not_before: Optional[int] = None
    not_after: Optional[int] = None
    lifetime_days: int = 365
    serial: Optional[int] = None
    output_der: bool = False
    password: Optional[bytes] = None

    def issue(self, key: KeyRef) -> bytes:
        if key.material is None:
            raise ValueError(
                "Self-signed issuance requires a private key in KeyRef.material (PEM)."
            )
        pwd = self.password
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
        subj = _name_from_subject(self.subject)
        issuer = subj

        if self.not_before is not None and self.not_after is not None:
            nb = datetime.fromtimestamp(int(self.not_before), tz=timezone.utc)
            na = datetime.fromtimestamp(int(self.not_after), tz=timezone.utc)
        else:
            nb = _now_utc() - timedelta(seconds=300)
            na = nb + timedelta(days=int(self.lifetime_days))

        serial = self.serial if self.serial is not None else x509.random_serial_number()

        builder = (
            x509.CertificateBuilder()
            .subject_name(subj)
            .issuer_name(issuer)
            .public_key(public_key)
            .serial_number(serial)
            .not_valid_before(nb)
            .not_valid_after(na)
        )

        bc = _bc_from_spec(
            self.extensions.get("basic_constraints") if self.extensions else None
        )
        if bc:
            builder = builder.add_extension(bc, critical=True)

        ku = _ku_from_spec(
            self.extensions.get("key_usage") if self.extensions else None
        )
        if ku:
            builder = builder.add_extension(ku, critical=True)

        eku = _eku_from_spec(
            self.extensions.get("extended_key_usage") if self.extensions else None
        )
        if eku:
            builder = builder.add_extension(eku, critical=False)

        san = _san_from_spec(
            self.extensions.get("subject_alt_name")
            if self.extensions and self.extensions.get("subject_alt_name")
            else self.san
        )
        if san:
            builder = builder.add_extension(san, critical=False)

        skid = x509.SubjectKeyIdentifier.from_public_key(public_key)
        builder = builder.add_extension(skid, critical=False)
        akid = x509.AuthorityKeyIdentifier.from_issuer_public_key(public_key)
        builder = builder.add_extension(akid, critical=False)

        if self.extensions and self.extensions.get("name_constraints"):
            nc = self.extensions["name_constraints"]
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

        if self.output_der:
            return cert.public_bytes(serialization.Encoding.DER)
        return cert.public_bytes(serialization.Encoding.PEM)

    @classmethod
    def tls_server(
        cls,
        common_name: str,
        dns_names: Sequence[str] = (),
        ip_addrs: Sequence[str] = (),
        lifetime_days: int = 397,
    ) -> SelfSignedCertificate:
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
    ) -> SelfSignedCertificate:
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
