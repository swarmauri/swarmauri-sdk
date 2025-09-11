"""CFSSL-backed certificate service implementation."""

from __future__ import annotations

import base64
import datetime as dt
import json
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence, Tuple

try:  # pragma: no cover - import guard
    import httpx
except Exception as e:  # pragma: no cover
    raise ImportError(
        "CfsslCertService requires 'httpx'. Install with: pip install httpx"
    ) from e

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    CertBytes,
    CertExtensionSpec,
    CsrBytes,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef
from pydantic import Field


def _pem_to_der(pem_or_der: bytes) -> bytes:
    """Accept PEM or DER and return DER bytes."""
    b = pem_or_der.strip()
    if b.startswith(b"-----BEGIN CERTIFICATE-----"):
        return x509.load_pem_x509_certificate(b).public_bytes(
            encoding=serialization.Encoding.DER
        )
    return b


def _der_to_pem(der: bytes) -> bytes:
    """Return PEM encoding for given DER bytes."""
    return x509.load_der_x509_certificate(der).public_bytes(
        encoding=serialization.Encoding.PEM
    )


def _ts_epoch(ts: Optional[int]) -> Optional[str]:
    """Return RFC3339 UTC string for CFSSL when an epoch is provided."""
    if ts is None:
        return None
    return (
        dt.datetime.utcfromtimestamp(int(ts)).replace(microsecond=0).isoformat() + "Z"
    )


def _parse_name(n: x509.Name) -> Dict[str, str]:
    """Parse an ``x509.Name`` into a simple mapping."""
    m: Dict[str, str] = {}
    for attr in n:
        oid = attr.oid
        if oid == NameOID.COMMON_NAME:
            m["CN"] = attr.value
        elif oid == NameOID.COUNTRY_NAME:
            m["C"] = attr.value
        elif oid == NameOID.STATE_OR_PROVINCE_NAME:
            m["ST"] = attr.value
        elif oid == NameOID.LOCALITY_NAME:
            m["L"] = attr.value
        elif oid == NameOID.ORGANIZATION_NAME:
            m["O"] = attr.value
        elif oid == NameOID.ORGANIZATIONAL_UNIT_NAME:
            m["OU"] = attr.value
        elif oid == NameOID.EMAIL_ADDRESS:
            m["emailAddress"] = attr.value
        else:
            m[str(oid.dotted_string)] = attr.value
    return m


def _ext_key_usage_to_oids(eku: x509.ExtendedKeyUsage) -> Sequence[str]:
    """Convert extended key usage values to CFSSL-friendly OIDs."""
    out: list[str] = []
    for oid in eku:
        if oid == ExtendedKeyUsageOID.SERVER_AUTH:
            out.append("serverAuth")
        elif oid == ExtendedKeyUsageOID.CLIENT_AUTH:
            out.append("clientAuth")
        elif oid == ExtendedKeyUsageOID.CODE_SIGNING:
            out.append("codeSigning")
        elif oid == ExtendedKeyUsageOID.EMAIL_PROTECTION:
            out.append("emailProtection")
        elif oid == ExtendedKeyUsageOID.TIME_STAMPING:
            out.append("timeStamping")
        else:
            out.append(str(oid.dotted_string))
    return tuple(out)


@ComponentBase.register_type(CertServiceBase, "CfsslCertService")
class CfsslCertService(CertServiceBase):
    """Cloudflare CFSSL-backed X.509 signer and validator."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["CfsslCertService"] = "CfsslCertService"

    def __init__(
        self,
        base_url: str,
        *,
        default_profile: Optional[str] = None,
        default_label: Optional[str] = None,
        timeout_s: float = 10.0,
        verify_tls: bool | str = True,
        auth_bearer: Optional[str] = None,
        auth_header: Optional[Tuple[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
        use_bundle_for_verify: bool = True,
    ) -> None:
        super().__init__()
        self._base = base_url.rstrip("/")
        self._profile = default_profile
        self._label = default_label
        self._timeout = float(timeout_s)
        self._verify = verify_tls
        self._use_bundle = bool(use_bundle_for_verify)

        h: Dict[str, str] = {"Accept": "application/json"}
        if headers:
            h.update({str(k): str(v) for k, v in headers.items()})
        if auth_bearer:
            h["Authorization"] = f"Bearer {auth_bearer}"
        if auth_header:
            name, val = auth_header
            h[name] = val

        self._headers = h
        self._client: Optional[httpx.AsyncClient] = None

    async def _client_get(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify,
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _post(self, path: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        cli = await self._client_get()
        r = await cli.post(path, json=payload)
        r.raise_for_status()
        try:
            data = r.json()
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"CFSSL returned non-JSON response for {path}: {e}"
            ) from e
        if not isinstance(data, dict) or not data.get("success", False):
            msg = ""
            if isinstance(data.get("errors"), list) and data["errors"]:
                msg = "; ".join(
                    str(e.get("message", e))
                    for e in data["errors"]
                    if isinstance(e, dict)
                )
            elif data.get("messages"):
                msg = "; ".join(map(str, data["messages"]))
            raise RuntimeError(f"CFSSL error on {path}: {msg or 'unknown error'}")
        return data

    def supports(self) -> Mapping[str, Iterable[str]]:  # type: ignore[override]
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "EC-P256", "EC-P384", "Ed25519"),
            "sig_algs": ("RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
            "features": ("sign_from_csr", "verify", "parse", "bundle"),
            "profiles": ("server", "client", "code_signing"),
        }

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
    ) -> CsrBytes:
        raise NotImplementedError(
            "CfsslCertService does not build CSRs; use X509CertService for CSR creation."
        )

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
    ) -> CertBytes:
        raise NotImplementedError(
            "CfsslCertService does not issue self-signed certs; use X509CertService instead."
        )

    async def sign_cert(  # type: ignore[override]
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
        csr_pem = (
            csr
            if csr.strip().startswith(b"-----BEGIN")
            else x509.load_der_x509_csr(csr).public_bytes(serialization.Encoding.PEM)
        )

        profile = (
            (opts or {}).get("profile")
            or self._profile
            or (ca_key.tags.get("profile") if getattr(ca_key, "tags", None) else None)
        )
        label = (
            (opts or {}).get("label")
            or self._label
            or (ca_key.tags.get("label") if getattr(ca_key, "tags", None) else None)
        )

        payload: Dict[str, Any] = {"certificate_request": csr_pem.decode("utf-8")}
        if profile:
            payload["profile"] = str(profile)
        if label:
            payload["label"] = str(label)

        hosts: list[str] = []
        if extensions and extensions.get("subject_alt_name"):
            san = extensions["subject_alt_name"]  # type: ignore[index]
            for d in san.get("dns") or []:
                hosts.append(str(d))
            for ip in san.get("ip") or []:
                hosts.append(str(ip))
        if hosts:
            payload["hosts"] = hosts

        nb = _ts_epoch(not_before)
        na = _ts_epoch(not_after)
        if nb:
            payload["not_before"] = nb
        if na:
            payload["not_after"] = na

        data = await self._post("/api/v1/cfssl/sign", payload)
        result = data.get("result", {})
        cert_pem = result.get("certificate")
        if not cert_pem:
            raise RuntimeError("CFSSL response missing 'result.certificate'")

        cert_bytes = cert_pem.encode("utf-8")
        return _pem_to_der(cert_bytes) if output_der else cert_bytes

    async def verify_cert(  # type: ignore[override]
        self,
        cert: CertBytes,
        *,
        trust_roots: Optional[Sequence[CertBytes]] = None,
        intermediates: Optional[Sequence[CertBytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = False,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        use_bundle = (opts or {}).get("use_bundle", self._use_bundle)
        flavor = (opts or {}).get("flavor", "optimal")

        cert_pem = cert if cert.strip().startswith(b"-----BEGIN") else _der_to_pem(cert)

        chain_len = 1
        bundle_ok = False
        bundle_reason = None

        if use_bundle:
            payload: Dict[str, Any] = {
                "certificate": cert_pem.decode("utf-8"),
                "flavor": flavor,
            }
            if trust_roots:
                payload["roots"] = "\n".join(
                    (c if isinstance(c, bytes) else c.encode("utf-8")).decode("utf-8")
                    for c in trust_roots
                )
            if intermediates:
                payload["intermediates"] = "\n".join(
                    (c if isinstance(c, bytes) else c.encode("utf-8")).decode("utf-8")
                    for c in intermediates
                )

            try:
                b = await self._post("/api/v1/cfssl/bundle", payload)
                res = b.get("result", {})
                chain_pem = res.get("bundle")
                if chain_pem:
                    chain_len = chain_pem.count("-----BEGIN CERTIFICATE-----")
                    bundle_ok = True
            except Exception as e:  # pragma: no cover - network failure
                bundle_ok = False
                bundle_reason = str(e)

        x = x509.load_pem_x509_certificate(cert_pem)
        now_epoch = int(
            dt.datetime.utcnow().timestamp() if check_time is None else check_time
        )
        nbf = int(x.not_valid_before_utc.timestamp())
        naf = int(x.not_valid_after_utc.timestamp())
        time_ok = (now_epoch >= nbf) and (now_epoch <= naf)

        bc = None
        try:
            bc = x.extensions.get_extension_for_class(x509.BasicConstraints).value
        except Exception:
            pass
        is_ca = bool(bc.ca) if bc else False

        out: Dict[str, Any] = {
            "valid": bool(time_ok and (bundle_ok or not use_bundle)),
            "reason": (None if time_ok else "time_invalid")
            or (None if bundle_ok or not use_bundle else bundle_reason),
            "issuer": _parse_name(x.issuer),
            "subject": _parse_name(x.subject),
            "not_before": nbf,
            "not_after": naf,
            "chain_len": chain_len,
            "is_ca": is_ca,
            "revocation_checked": False if check_revocation else False,
        }
        return out

    async def parse_cert(  # type: ignore[override]
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pem = cert if cert.strip().startswith(b"-----BEGIN") else _der_to_pem(cert)
        c = x509.load_pem_x509_certificate(pem)

        info: Dict[str, Any] = {
            "tbs_version": c.tbs_certificate_bytes is not None and 3 or 3,
            "serial": int(c.serial_number),
            "issuer": _parse_name(c.issuer),
            "subject": _parse_name(c.subject),
            "not_before": int(c.not_valid_before_utc.timestamp()),
            "not_after": int(c.not_valid_after_utc.timestamp()),
        }

        if include_extensions:
            try:
                bc = c.extensions.get_extension_for_class(x509.BasicConstraints).value
                info["basic_constraints"] = {"ca": bc.ca, "path_len": bc.path_length}
            except Exception:
                pass

            try:
                san = c.extensions.get_extension_for_class(
                    x509.SubjectAlternativeName
                ).value
                dns = [str(x.value) for x in san.get_values_for_type(x509.DNSName)]
                ips = [str(x.value) for x in san.get_values_for_type(x509.IPAddress)]
                uris = [
                    str(x.value)
                    for x in san.get_values_for_type(x509.UniformResourceIdentifier)
                ]
                emails = [
                    str(x.value) for x in san.get_values_for_type(x509.RFC822Name)
                ]
                info["san"] = {
                    "dns": dns or None,
                    "ip": ips or None,
                    "uri": uris or None,
                    "email": emails or None,
                }
            except Exception:
                pass

            try:
                ku = c.extensions.get_extension_for_class(x509.KeyUsage).value
                info["key_usage"] = {
                    "digital_signature": ku.digital_signature,
                    "content_commitment": ku.content_commitment,
                    "key_encipherment": ku.key_encipherment,
                    "data_encipherment": ku.data_encipherment,
                    "key_agreement": ku.key_agreement,
                    "key_cert_sign": ku.key_cert_sign,
                    "crl_sign": ku.crl_sign,
                    "encipher_only": ku.encipher_only,
                    "decipher_only": ku.decipher_only,
                }
            except Exception:
                pass

            try:
                eku = c.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
                info["eku"] = list(_ext_key_usage_to_oids(eku))
            except Exception:
                pass

            try:
                skid = c.extensions.get_extension_for_class(
                    x509.SubjectKeyIdentifier
                ).value
                info["skid"] = base64.b16encode(skid.digest).decode("ascii").lower()
            except Exception:
                pass

            try:
                akid = c.extensions.get_extension_for_class(
                    x509.AuthorityKeyIdentifier
                ).value
                if akid.key_identifier:
                    info["akid"] = (
                        base64.b16encode(akid.key_identifier).decode("ascii").lower()
                    )
            except Exception:
                pass

        return info
