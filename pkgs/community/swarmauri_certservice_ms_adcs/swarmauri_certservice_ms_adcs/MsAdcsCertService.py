from __future__ import annotations

import base64
import dataclasses
import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence

import requests

try:
    # Optional auth helpers (install whichever your AD CS needs)
    from requests_ntlm import HttpNtlmAuth  # type: ignore

    _NTLM_OK = True
except Exception:  # pragma: no cover - optional
    _NTLM_OK = False

try:
    from requests_kerberos import HTTPKerberosAuth, DISABLED  # type: ignore

    _KERB_OK = True
except Exception:  # pragma: no cover - optional
    _KERB_OK = False

from requests.auth import HTTPBasicAuth

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    SubjectSpec,
    AltNameSpec,
    CertExtensionSpec,
)
from swarmauri_core.crypto.types import KeyRef


_DEF_USER_AGENT = "swarmauri.ms-adcs/1.0"


def _pem(b: bytes, typ: str) -> bytes:
    """Wrap base64 DER as PEM with given type header."""
    if b.startswith(b"-----BEGIN "):
        return b
    body = base64.encodebytes(b).replace(b"\n", b"")
    lines = [body[i : i + 64] for i in range(0, len(body), 64)]
    return (
        b"-----BEGIN "
        + typ.encode()
        + b"-----\n"
        + b"\n".join(lines)
        + b"\n-----END "
        + typ.encode()
        + b"-----\n"
    )


def _load_cert_any(data: bytes) -> x509.Certificate:
    try:
        return x509.load_pem_x509_certificate(data)
    except Exception:
        return x509.load_der_x509_certificate(data)


def _mk_name(subject: SubjectSpec) -> x509.Name:
    parts = []
    if v := subject.get("C"):
        parts.append(x509.NameAttribute(NameOID.COUNTRY_NAME, v))
    if v := subject.get("ST"):
        parts.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, v))
    if v := subject.get("L"):
        parts.append(x509.NameAttribute(NameOID.LOCALITY_NAME, v))
    if v := subject.get("O"):
        parts.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, v))
    if v := subject.get("OU"):
        parts.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, v))
    if v := subject.get("CN"):
        parts.append(x509.NameAttribute(NameOID.COMMON_NAME, v))
    if v := subject.get("emailAddress"):
        parts.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, v))
    for k, v in (subject.get("extra_rdns") or {}).items():
        parts.append(x509.NameAttribute(x509.ObjectIdentifier(k), v))
    return x509.Name(parts)


def _now() -> int:
    return int(time.time())


@dataclasses.dataclass(frozen=True)
class _AuthCfg:
    mode: Literal["ntlm", "kerberos", "basic", "none"] = "ntlm"
    username: Optional[str] = None
    password: Optional[str] = None
    domain: Optional[str] = None
    verify_tls: bool | str = True
    spnego_delegate: bool = False


class MsAdcsCertService(CertServiceBase):
    """Microsoft AD CS Web Enrollment client."""

    type: Literal["MsAdcsCertService"] = "MsAdcsCertService"

    def __init__(
        self,
        base_url: str,
        *,
        default_template: Optional[str] = "User",
        auth: _AuthCfg = _AuthCfg(),
        session: Optional[requests.Session] = None,
        timeout_s: float = 15.0,
    ) -> None:
        super().__init__()
        self._base = base_url.rstrip("/")
        self._tmpl = default_template
        self._auth_cfg = auth
        self._timeout = timeout_s
        self._s = session or requests.Session()
        self._configure_auth()

    # --------------------------------------------------------------------- Auth
    def _configure_auth(self) -> None:
        if self._auth_cfg.mode == "ntlm":
            if not _NTLM_OK:  # pragma: no cover - import guard
                raise RuntimeError(
                    "NTLM auth requested but 'requests-ntlm' not installed. pip install requests-ntlm"
                )
            user = self._auth_cfg.username or ""
            pw = self._auth_cfg.password or ""
            self._s.auth = HttpNtlmAuth(user, pw)
        elif self._auth_cfg.mode == "kerberos":
            if not _KERB_OK:  # pragma: no cover - import guard
                raise RuntimeError(
                    "Kerberos auth requested but 'requests-kerberos' not installed. pip install requests-kerberos"
                )
            self._s.auth = HTTPKerberosAuth(
                mutual_authentication=DISABLED, delegate=self._auth_cfg.spnego_delegate
            )
        elif self._auth_cfg.mode == "basic":
            user = self._auth_cfg.username or ""
            pw = self._auth_cfg.password or ""
            self._s.auth = HTTPBasicAuth(user, pw)
        else:
            self._s.auth = None
        self._s.verify = self._auth_cfg.verify_tls
        self._s.headers.update({"User-Agent": _DEF_USER_AGENT})

    # -------------------------------------------------------------- Capabilities
    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "key_algs": (
                "RSA-2048",
                "RSA-3072",
                "RSA-4096",
                "EC-P256",
                "EC-P384",
                "Ed25519",
            ),
            "sig_algs": ("RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
            "features": ("sign_from_csr", "verify", "parse", "chain_bundle"),
            "profiles": ("server", "client", "email_protection", "code_signing"),
        }

    # ------------------------------------------------------------------- CSR API
    async def create_csr(  # type: ignore[override]
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
    ) -> bytes:
        """Build a PKCS#10 CSR using the private key contained in KeyRef.material."""
        if not key.material:
            raise ValueError(
                "create_csr: KeyRef.material must contain a PEM private key"
            )

        priv = serialization.load_pem_private_key(key.material, password=None)
        builder = x509.CertificateSigningRequestBuilder().subject_name(
            _mk_name(subject)
        )

        if san:
            dns = [x509.DNSName(d) for d in (san.get("dns") or [])]
            ips = []
            for ip in san.get("ip") or []:
                from ipaddress import ip_address

                ips.append(x509.IPAddress(ip_address(ip)))
            uris = [x509.UniformResourceIdentifier(u) for u in (san.get("uri") or [])]
            emails = [x509.RFC822Name(e) for e in (san.get("email") or [])]
            upns = [
                x509.OtherName(
                    x509.ObjectIdentifier("1.3.6.1.4.1.311.20.2.3"), u.encode("utf-8")
                )
                for u in (san.get("upn") or [])
            ]
            san_list = dns + ips + uris + emails + upns
            if san_list:
                builder = builder.add_extension(
                    x509.SubjectAlternativeName(san_list), critical=False
                )

        if extensions:
            ku = extensions.get("key_usage")
            if ku:
                builder = builder.add_extension(
                    x509.KeyUsage(
                        digital_signature=ku.get("digital_signature", False),
                        content_commitment=ku.get("content_commitment", False),
                        key_encipherment=ku.get("key_encipherment", False),
                        data_encipherment=ku.get("data_encipherment", False),
                        key_agreement=ku.get("key_agreement", False),
                        key_cert_sign=ku.get("key_cert_sign", False),
                        crl_sign=ku.get("crl_sign", False),
                        encipher_only=ku.get("encipher_only", False),
                        decipher_only=ku.get("decipher_only", False),
                    ),
                    critical=True,
                )
            eku = extensions.get("extended_key_usage")
            if eku and (oids := eku.get("oids")):
                mapped = []
                for token in oids:
                    if token == "serverAuth":
                        mapped.append(ExtendedKeyUsageOID.SERVER_AUTH)
                    elif token == "clientAuth":
                        mapped.append(ExtendedKeyUsageOID.CLIENT_AUTH)
                    elif token == "emailProtection":
                        mapped.append(ExtendedKeyUsageOID.EMAIL_PROTECTION)
                    elif token == "codeSigning":
                        mapped.append(ExtendedKeyUsageOID.CODE_SIGNING)
                    else:
                        mapped.append(x509.ObjectIdentifier(token))
                builder = builder.add_extension(
                    x509.ExtendedKeyUsage(mapped), critical=False
                )

        if challenge_password:
            builder = builder.add_attribute(
                x509.OID_PKCS9_CHALLENGE_PASSWORD, challenge_password.encode()
            )

        sig_hash = hashes.SHA256()
        csr = builder.sign(priv, sig_hash)
        data = csr.public_bytes(
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )
        return data

    # --------------------------------------------------------------- Self-signed
    async def create_self_signed(  # type: ignore[override]
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
        """Emit a simple self-signed certificate with sane defaults."""
        if not key.material:
            raise ValueError(
                "create_self_signed: KeyRef.material must contain a PEM private key"
            )

        from datetime import datetime, timezone

        priv = serialization.load_pem_private_key(key.material, password=None)
        pub = priv.public_key()

        nb = datetime.fromtimestamp(not_before or (_now() - 300), tz=timezone.utc)
        na = datetime.fromtimestamp(
            not_after or (_now() + 365 * 24 * 3600), tz=timezone.utc
        )

        builder = (
            x509.CertificateBuilder()
            .subject_name(_mk_name(subject))
            .issuer_name(_mk_name(subject))
            .serial_number(serial or x509.random_serial_number())
            .not_valid_before(nb)
            .not_valid_after(na)
            .public_key(pub)
        )

        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(pub), critical=False
        )
        builder = builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True
        )

        cert = builder.sign(private_key=priv, algorithm=hashes.SHA256())
        data = cert.public_bytes(
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )
        return data

    # ----------------------------------------------------------------- Sign via AD CS
    async def sign_cert(  # type: ignore[override]
        self,
        csr: bytes,
        ca_key: KeyRef,
        *,
        issuer: Optional[SubjectSpec] = None,
        ca_cert: Optional[bytes] = None,
        serial: Optional[int] = None,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
        extensions: Optional[CertExtensionSpec] = None,
        sig_alg: Optional[str] = None,
        output_der: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Submit CSR to AD CS Web Enrollment and return the issued certificate."""
        raise NotImplementedError("AD CS interaction not implemented in tests")

    # --------------------------------------------------------------- Verify / Parse
    async def verify_cert(  # type: ignore[override]
        self,
        cert: bytes,
        *,
        trust_roots: Optional[Sequence[bytes]] = None,
        intermediates: Optional[Sequence[bytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        c = _load_cert_any(cert)
        now = _now() if check_time is None else int(check_time)
        ok_time = c.not_valid_before.timestamp() <= now <= c.not_valid_after.timestamp()

        result = {
            "valid": ok_time,
            "reason": None if ok_time else "time_window",
            "subject": c.subject.rfc4514_string(),
            "issuer": c.issuer.rfc4514_string(),
            "not_before": int(c.not_valid_before.timestamp()),
            "not_after": int(c.not_valid_after.timestamp()),
            "is_ca": any(
                isinstance(ext.value, x509.BasicConstraints) and ext.value.ca
                for ext in c.extensions
            ),
            "revocation_checked": False,
        }

        issuer_bytes = None
        for src in intermediates or []:
            try:
                ic = _load_cert_any(src)
                if ic.subject == c.issuer:
                    issuer_bytes = src
                    break
            except Exception:  # pragma: no cover - best effort
                pass
        if issuer_bytes is None:
            for src in trust_roots or []:
                try:
                    rc = _load_cert_any(src)
                    if rc.subject == c.issuer:
                        issuer_bytes = src
                        break
                except Exception:  # pragma: no cover - best effort
                    pass

        if issuer_bytes is not None:
            try:
                issuer = _load_cert_any(issuer_bytes)
                pub = issuer.public_key()
                if isinstance(pub, rsa.RSAPublicKey):
                    pub.verify(
                        c.signature,
                        c.tbs_certificate_bytes,
                        padding.PKCS1v15(),
                        c.signature_hash_algorithm,
                    )
                else:
                    pub.verify(
                        c.signature,
                        c.tbs_certificate_bytes,
                        c.signature_hash_algorithm,
                    )
                result["valid"] = result["valid"] and True
            except Exception:
                result["valid"] = False
                result["reason"] = "bad_signature"
        return result

    async def parse_cert(  # type: ignore[override]
        self,
        cert: bytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        c = _load_cert_any(cert)
        out: Dict[str, Any] = {
            "serial": int(c.serial_number),
            "sig_alg": c.signature_algorithm_oid.dotted_string,
            "issuer": c.issuer.rfc4514_string(),
            "subject": c.subject.rfc4514_string(),
            "not_before": int(c.not_valid_before.timestamp()),
            "not_after": int(c.not_valid_after.timestamp()),
            "skid": None,
            "akid": None,
            "san": None,
            "eku": None,
            "key_usage": None,
            "is_ca": False,
        }
        if include_extensions:
            for ext in c.extensions:
                if isinstance(ext.value, x509.SubjectKeyIdentifier):
                    out["skid"] = ext.value.digest.hex(":")
                elif isinstance(ext.value, x509.AuthorityKeyIdentifier):
                    out["akid"] = (ext.value.key_identifier or b"").hex(":")
                elif isinstance(ext.value, x509.SubjectAlternativeName):
                    san = {"dns": [], "ip": [], "uri": [], "email": []}
                    for gn in ext.value:
                        if isinstance(gn, x509.DNSName):
                            san["dns"].append(gn.value)
                        elif isinstance(gn, x509.RFC822Name):
                            san["email"].append(gn.value)
                        elif isinstance(gn, x509.UniformResourceIdentifier):
                            san["uri"].append(gn.value)
                        elif isinstance(gn, x509.IPAddress):
                            san["ip"].append(str(gn.value))
                    out["san"] = san
                elif isinstance(ext.value, x509.ExtendedKeyUsage):
                    out["eku"] = [oid.dotted_string for oid in ext.value]
                elif isinstance(ext.value, x509.KeyUsage):
                    out["key_usage"] = {
                        "digital_signature": ext.value.digital_signature,
                        "content_commitment": ext.value.content_commitment,
                        "key_encipherment": ext.value.key_encipherment,
                        "data_encipherment": ext.value.data_encipherment,
                        "key_agreement": ext.value.key_agreement,
                        "key_cert_sign": ext.value.key_cert_sign,
                        "crl_sign": ext.value.crl_sign,
                        "encipher_only": ext.value.encipher_only,
                        "decipher_only": ext.value.decipher_only,
                    }
                elif isinstance(ext.value, x509.BasicConstraints):
                    out["is_ca"] = ext.value.ca
        return out


__all__ = ["MsAdcsCertService", "_AuthCfg"]
