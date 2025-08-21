"""Step-ca backed certificate service.

This implementation creates CSRs compliant with RFC 2986 and
handles X.509 certificates as described in RFC 5280.
"""

from __future__ import annotations

import datetime as dt
import ipaddress
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Union,
    Literal,
)

import httpx
from pydantic import Field

from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    CertBytes,
    CertExtensionSpec,
    CsrBytes,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


def _to_name(subj: SubjectSpec) -> x509.Name:
    """Convert a subject specification into an X.509 name."""
    parts: list[x509.NameAttribute] = []
    if "C" in subj:
        parts.append(x509.NameAttribute(NameOID.COUNTRY_NAME, subj["C"]))
    if "ST" in subj:
        parts.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subj["ST"]))
    if "L" in subj:
        parts.append(x509.NameAttribute(NameOID.LOCALITY_NAME, subj["L"]))
    if "O" in subj:
        parts.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, subj["O"]))
    if "OU" in subj:
        parts.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, subj["OU"]))
    if "emailAddress" in subj:
        parts.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, subj["emailAddress"]))
    if "CN" in subj:
        parts.append(x509.NameAttribute(NameOID.COMMON_NAME, subj["CN"]))
    return x509.Name(parts)


def _san_from_spec(san: Optional[AltNameSpec]) -> Optional[x509.SubjectAlternativeName]:
    """Build a SubjectAlternativeName from a specification."""
    if not san:
        return None
    gen = []
    for d in san.get("dns", []) or []:
        gen.append(x509.DNSName(d))
    for ip in san.get("ip", []) or []:
        gen.append(x509.IPAddress(ipaddress.ip_address(ip)))
    for u in san.get("uri", []) or []:
        gen.append(x509.UniformResourceIdentifier(u))
    for e in san.get("email", []) or []:
        gen.append(x509.RFC822Name(e))
    return x509.SubjectAlternativeName(gen) if gen else None


def _extensions_from_spec(ext: Optional[CertExtensionSpec]) -> Sequence[x509.Extension]:
    """Translate extension specification into X.509 extensions."""
    if not ext:
        return ()
    out: list[x509.Extension] = []
    bc = ext.get("basic_constraints")
    if bc is not None:
        out.append(
            x509.Extension(
                x509.ExtensionOID.BASIC_CONSTRAINTS,
                critical=True,
                value=x509.BasicConstraints(
                    ca=bool(bc.get("ca", False)),
                    path_length=bc.get("path_len"),
                ),
            )
        )
    ku = ext.get("key_usage")
    if ku is not None:
        out.append(
            x509.Extension(
                x509.ExtensionOID.KEY_USAGE,
                critical=True,
                value=x509.KeyUsage(
                    digital_signature=bool(ku.get("digital_signature", False)),
                    content_commitment=bool(ku.get("content_commitment", False)),
                    key_encipherment=bool(ku.get("key_encipherment", False)),
                    data_encipherment=bool(ku.get("data_encipherment", False)),
                    key_agreement=bool(ku.get("key_agreement", False)),
                    key_cert_sign=bool(ku.get("key_cert_sign", False)),
                    crl_sign=bool(ku.get("crl_sign", False)),
                    encipher_only=bool(ku.get("encipher_only", False)),
                    decipher_only=bool(ku.get("decipher_only", False)),
                ),
            )
        )
    eku = ext.get("extended_key_usage")
    if eku and (oids := eku.get("oids")):
        vals: list[x509.ObjectIdentifier] = []
        alias = {
            "serverAuth": ExtendedKeyUsageOID.SERVER_AUTH,
            "clientAuth": ExtendedKeyUsageOID.CLIENT_AUTH,
            "codeSigning": ExtendedKeyUsageOID.CODE_SIGNING,
            "emailProtection": ExtendedKeyUsageOID.EMAIL_PROTECTION,
            "timeStamping": ExtendedKeyUsageOID.TIME_STAMPING,
            "OCSPSigning": ExtendedKeyUsageOID.OCSP_SIGNING,
        }
        for s in oids:
            vals.append(alias.get(s, x509.ObjectIdentifier(s)))
        out.append(
            x509.Extension(
                x509.ExtensionOID.EXTENDED_KEY_USAGE,
                critical=False,
                value=x509.ExtendedKeyUsage(vals),
            )
        )
    return tuple(out)


def _load_private_key(ref: KeyRef):
    """Load a private key from a KeyRef."""
    if not ref or ref.material is None:
        raise ValueError(
            "KeyRef.material (private key PEM) is required to create/sign a CSR."
        )
    return serialization.load_pem_private_key(ref.material, password=None)


class StepCaCertService(CertServiceBase):
    """X.509 CSR and certificate handling via a step-ca backend.

    Implements portions of RFC 2986 (CSRs) and RFC 5280 (X.509 certificates).
    """

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["StepCaCertService"] = "StepCaCertService"

    ca_url: str
    verify_tls: Union[bool, str, bytes] = True
    timeout_s: float = 6.0
    provisioner: Optional[str] = None
    token_provider: Optional[Callable[[Dict[str, Any]], Awaitable[str]]] = None

    def __init__(
        self,
        ca_url: str,
        *,
        verify_tls: Union[bool, str, bytes] = True,
        timeout_s: float = 6.0,
        provisioner: Optional[str] = None,
        token_provider: Optional[Callable[[Dict[str, Any]], Awaitable[str]]] = None,
    ) -> None:
        super().__init__(
            ca_url=ca_url.rstrip("/"),
            verify_tls=verify_tls,
            timeout_s=float(timeout_s),
            provisioner=provisioner,
            token_provider=token_provider,
        )
        self._client: Optional[httpx.AsyncClient] = None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.ca_url,
                timeout=self.timeout_s,
                verify=self.verify_tls,
                headers={
                    "Accept": "application/json, application/pem-certificate-chain, text/plain",
                },
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return supported algorithms and features."""
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "EC-P256", "Ed25519"),
            "sig_algs": ("RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
            "features": ("csr", "sign_from_csr", "verify", "parse", "remote_ca"),
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
        sk = _load_private_key(key)
        builder = x509.CertificateSigningRequestBuilder()
        builder = builder.subject_name(_to_name(subject))
        if sanext := _san_from_spec(san):
            builder = builder.add_extension(sanext, critical=False)
        for ext in _extensions_from_spec(extensions):
            builder = builder.add_extension(ext.value, critical=ext.critical)
        if challenge_password:
            builder = builder.add_attribute(
                x509.ObjectIdentifier("1.2.840.113549.1.9.7"),
                challenge_password.encode(),
            )
        if sig_alg is None:
            if isinstance(sk, rsa.RSAPrivateKey):
                csr = builder.sign(sk, hashes.SHA256())
            elif isinstance(sk, ec.EllipticCurvePrivateKey):
                csr = builder.sign(sk, hashes.SHA256())
            elif isinstance(sk, ed25519.Ed25519PrivateKey):
                csr = builder.sign(sk, None)
            else:
                raise ValueError("Unsupported private key type for CSR signing.")
        else:
            if isinstance(sk, rsa.RSAPrivateKey):
                csr = builder.sign(sk, hashes.SHA256())
            elif isinstance(sk, ec.EllipticCurvePrivateKey):
                csr = builder.sign(sk, hashes.SHA256())
            elif isinstance(sk, ed25519.Ed25519PrivateKey):
                csr = builder.sign(sk, None)
            else:
                raise ValueError("Unsupported private key type for CSR signing.")
        encoding = (
            serialization.Encoding.DER if output_der else serialization.Encoding.PEM
        )
        return csr.public_bytes(encoding)

    def _claims_from_csr(self, csr_pem: str) -> Dict[str, Any]:
        """Extract claims for token generation from a CSR."""
        csr = x509.load_pem_x509_csr(csr_pem.encode())
        try:
            cn = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except IndexError:
            cn = ""
        sans: list[str] = []
        try:
            san_ext = csr.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            )
            sans = san_ext.value.get_values_for_type(x509.DNSName)
        except x509.ExtensionNotFound:
            pass
        return {"sub": cn, "sans": sans}

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
        payload: Dict[str, Any] = {}
        if (
            b"BEGIN CERTIFICATE REQUEST" in csr
            or b"BEGIN NEW CERTIFICATE REQUEST" in csr
        ):
            csr_pem = csr.decode() if isinstance(csr, (bytes, bytearray)) else csr
        else:
            csr_pem = (
                x509.load_der_x509_csr(csr)
                .public_bytes(serialization.Encoding.PEM)
                .decode()
            )
        payload["csr"] = csr_pem
        if not_before:
            payload["notBefore"] = dt.datetime.fromtimestamp(
                int(not_before), dt.timezone.utc
            ).isoformat()
        if not_after:
            payload["notAfter"] = dt.datetime.fromtimestamp(
                int(not_after), dt.timezone.utc
            ).isoformat()
        if self.provisioner or (opts and opts.get("provisioner")):
            payload["provisioner"] = (
                opts.get("provisioner") if opts else self.provisioner
            )
        if opts and opts.get("template_data"):
            payload["templateData"] = opts["template_data"]
        if opts and opts.get("extra"):
            payload.update(dict(opts["extra"]))
        ott: Optional[str] = None
        if opts and isinstance(opts.get("ott") or opts.get("token"), str):
            ott = str(opts.get("ott") or opts.get("token"))
        elif self.token_provider:
            claims = self._claims_from_csr(csr_pem)
            ott = await self.token_provider(claims)
        if not ott:
            raise ValueError(
                "StepCaCertService.sign_cert requires 'ott' in opts or a token_provider on the service.",
            )
        payload["ott"] = ott
        payload["token"] = ott
        client = await self._http()
        resp = await client.post("/1.0/sign", json=payload)
        if resp.status_code >= 400:
            try:
                data = resp.json()
                raise RuntimeError(
                    f"step-ca sign failed: {data.get('message') or data}"
                )
            except Exception:  # pragma: no cover - fall through for non-JSON
                raise
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            data = resp.json()
            pem = data.get("crt") or data.get("certificate") or data.get("pem")
            if isinstance(pem, list):
                cert_pem = "\n".join(pem)
            elif isinstance(pem, str):
                cert_pem = pem
            else:
                cert_pem = resp.text
        else:
            cert_pem = resp.text
        if output_der:
            cert = x509.load_pem_x509_certificate(cert_pem.encode())
            return cert.public_bytes(serialization.Encoding.DER)
        return cert_pem.encode()
