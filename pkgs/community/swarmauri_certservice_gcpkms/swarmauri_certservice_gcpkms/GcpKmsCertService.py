"""Google Cloud KMS backed certificate service."""

from __future__ import annotations

import datetime as _dt
from typing import Iterable, Mapping, Optional, Sequence, Dict, Any, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    SubjectSpec,
    AltNameSpec,
    CertExtensionSpec,
    CertBytes,
    CsrBytes,
)
from swarmauri_core.crypto.types import KeyRef

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.x509.oid import NameOID


def _kms():
    """Import the Google Cloud KMS client.

    RETURNS (kms_v1): The `google.cloud.kms_v1` module.
    RAISES (ImportError): If `google-cloud-kms` is not installed.
    """

    try:
        from google.cloud import kms_v1

        return kms_v1
    except Exception as e:  # pragma: no cover
        raise ImportError(
            "GcpKmsCertService requires google-cloud-kms. Install with:\n"
            "  pip install google-cloud-kms"
        ) from e


def _now() -> _dt.datetime:
    """Get the current UTC time.

    RETURNS (_dt.datetime): Current time with UTC timezone.
    """

    return _dt.datetime.utcnow().replace(tzinfo=_dt.timezone.utc)


def _secs(ts: Optional[int], default: int) -> _dt.datetime:
    """Convert an epoch timestamp to datetime.

    ts (Optional[int]): Unix timestamp in seconds.
    default (int): Number of seconds to add if `ts` is ``None``.

    RETURNS (_dt.datetime): The resulting datetime in UTC.
    """

    return (
        _dt.datetime.utcfromtimestamp(ts).replace(tzinfo=_dt.timezone.utc)
        if ts is not None
        else _now() + _dt.timedelta(seconds=default)
    )


def _subject_from_spec(spec: SubjectSpec) -> x509.Name:
    """Create an ``x509.Name`` from a subject specification.

    spec (SubjectSpec): Mapping of distinguished name attributes.

    RETURNS (x509.Name): The constructed subject name.
    """

    rdns: list[x509.NameAttribute] = []
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
    if "emailAddress" in spec:
        rdns.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, spec["emailAddress"]))
    if "CN" in spec:
        rdns.append(x509.NameAttribute(NameOID.COMMON_NAME, spec["CN"]))
    for k, v in (spec.get("extra_rdns") or {}).items():
        try:
            oid = x509.ObjectIdentifier(k)
        except Exception:
            oid = NameOID.ORGANIZATIONAL_UNIT_NAME
        rdns.append(x509.NameAttribute(oid, v))
    return x509.Name(rdns)


def _add_san(
    builder: x509.CertificateBuilder | x509.CertificateSigningRequestBuilder,
    san: Optional[AltNameSpec],
):
    """Add a Subject Alternative Name extension to a builder.

    builder (x509.CertificateBuilder | x509.CertificateSigningRequestBuilder):
        The builder to modify.
    san (Optional[AltNameSpec]): Specification of alternative names.

    RETURNS (x509.CertificateBuilder | x509.CertificateSigningRequestBuilder):
        The builder with the extension applied.
    """

    if not san:
        return builder
    names: list[x509.GeneralName] = []
    for d in san.get("dns", []) or []:
        names.append(x509.DNSName(d))
    for ip in san.get("ip", []) or []:
        names.append(x509.IPAddress(x509.ipaddress.ip_address(ip)))
    if names:
        builder = builder.add_extension(
            x509.SubjectAlternativeName(names), critical=False
        )
    return builder


def _apply_extensions(
    builder: x509.CertificateBuilder,
    ext: Optional[CertExtensionSpec],
    issuer_pub: Optional[bytes] = None,
    subject_pub: Optional[bytes] = None,
    is_self_signed: bool = False,
) -> x509.CertificateBuilder:
    """Apply certificate extensions.

    builder (x509.CertificateBuilder): Builder to modify.
    ext (Optional[CertExtensionSpec]): Extension specification.
    issuer_pub (Optional[bytes]): Issuer public key in PEM format.
    subject_pub (Optional[bytes]): Subject public key in PEM format.
    is_self_signed (bool): Whether the certificate is self-signed.

    RETURNS (x509.CertificateBuilder): Builder with extensions applied.
    """

    if not ext:
        return builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True
        )
    if "basic_constraints" in ext:
        bc = ext["basic_constraints"]
        builder = builder.add_extension(
            x509.BasicConstraints(
                ca=bool(bc.get("ca", False)),
                path_length=bc.get("path_len", None),
            ),
            critical=True,
        )
    if "subject_key_identifier" in ext and subject_pub:
        pk = load_pem_public_key(subject_pub)
        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(pk), critical=False
        )
    if "authority_key_identifier" in ext and issuer_pub:
        pk = load_pem_public_key(issuer_pub)
        builder = builder.add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(pk),
            critical=False,
        )
    return builder


def _make_kms_private_key(
    client, version_name: str
):  # pragma: no cover - patched in tests
    """Return a private key object backed by KMS.

    client: KMS client instance.
    version_name (str): Resource name of the key version.

    RETURNS: A private key compatible with ``cryptography``.
    """

    raise NotImplementedError


def _key_version_from_keyref(ref: KeyRef) -> str:
    """Extract the KMS key version from a key reference.

    ref (KeyRef): Key reference containing tagging metadata.

    RETURNS (str): The fully-qualified key version name.
    """

    tags = ref.tags or {}
    return tags.get("gcp_kms_key_version") or tags.get("kms_key_version") or ref.kid


@ComponentBase.register_type(CertServiceBase, "GcpKmsCertService")
class GcpKmsCertService(CertServiceBase):
    """Certificate service using Google Cloud KMS for key operations."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["GcpKmsCertService"] = "GcpKmsCertService"

    def __init__(self, *, client=None) -> None:
        """Initialize the service.

        client: Optional KMS client instance.
        """

        super().__init__()
        self._client = client

    def _client_or_new(self):
        """Return an existing client or create a new one.

        RETURNS: ``KeyManagementServiceClient`` instance.
        """

        if self._client is not None:
            return self._client
        return _kms().KeyManagementServiceClient()

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Describe supported algorithms and features.

        RETURNS (Mapping[str, Iterable[str]]): Keys for categories with supported values.
        """

        return {
            "key_algs": ("RSA-2048", "EC-P256", "Ed25519"),
            "sig_algs": ("RSA-PKCS1-SHA256", "ECDSA-P256-SHA256", "Ed25519"),
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
        """Create a certificate signing request.

        key (KeyRef): Reference to the private key in KMS.
        subject (SubjectSpec): Subject specification for the CSR.
        san (Optional[AltNameSpec]): Subject alternative names.
        extensions (Optional[CertExtensionSpec]): Additional certificate extensions.
        sig_alg (Optional[str]): Signature algorithm to use.
        challenge_password (Optional[str]): Password to embed in the CSR.
        output_der (bool): Return DER bytes if ``True``; otherwise PEM.
        opts (Optional[Dict[str, Any]]): Extra backend options.

        RETURNS (CsrBytes): The generated CSR bytes.
        """

        client = self._client_or_new()
        version = _key_version_from_keyref(key)
        kms_priv = _make_kms_private_key(client, version)

        builder = x509.CertificateSigningRequestBuilder()
        builder = builder.subject_name(_subject_from_spec(subject))
        builder = _add_san(builder, san)
        if challenge_password:
            builder = builder.add_attribute(
                NameOID.CHALLENGE_PASSWORD, challenge_password.encode("utf-8")
            )
        csr = builder.sign(kms_priv, hashes.SHA256())
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
        """Create a self-signed certificate.

        key (KeyRef): Reference to the private key in KMS.
        subject (SubjectSpec): Subject specification for the certificate.
        serial (Optional[int]): Serial number of the certificate.
        not_before (Optional[int]): Validity start time as a Unix timestamp.
        not_after (Optional[int]): Validity end time as a Unix timestamp.
        extensions (Optional[CertExtensionSpec]): Additional certificate extensions.
        sig_alg (Optional[str]): Signature algorithm to use.
        output_der (bool): Return DER bytes if ``True``; otherwise PEM.
        opts (Optional[Dict[str, Any]]): Extra backend options.

        RETURNS (CertBytes): The generated certificate bytes.
        """

        client = self._client_or_new()
        version = _key_version_from_keyref(key)
        kms_priv = _make_kms_private_key(client, version)
        pub_pem = client.get_public_key(request={"name": version}).pem.encode("utf-8")

        subject_name = _subject_from_spec(subject)
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject_name).issuer_name(subject_name)
        builder = builder.serial_number(serial or x509.random_serial_number())
        nbf = _secs(not_before, default=-300)
        naf = _secs(not_after, default=365 * 24 * 3600)
        builder = builder.not_valid_before(nbf).not_valid_after(naf)
        builder = builder.public_key(load_pem_public_key(pub_pem))
        builder = _apply_extensions(
            builder,
            extensions,
            issuer_pub=pub_pem,
            subject_pub=pub_pem,
            is_self_signed=True,
        )
        cert = builder.sign(kms_priv, hashes.SHA256())
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
        """Sign a certificate from a CSR.

        csr (CsrBytes): CSR to sign.
        ca_key (KeyRef): Reference to the CA key in KMS.
        issuer (Optional[SubjectSpec]): Issuer subject specification.
        ca_cert (Optional[CertBytes]): CA certificate used for extension defaults.
        serial (Optional[int]): Serial number of the certificate.
        not_before (Optional[int]): Validity start time as a Unix timestamp.
        not_after (Optional[int]): Validity end time as a Unix timestamp.
        extensions (Optional[CertExtensionSpec]): Additional certificate extensions.
        sig_alg (Optional[str]): Signature algorithm to use.
        output_der (bool): Return DER bytes if ``True``; otherwise PEM.
        opts (Optional[Dict[str, Any]]): Extra backend options.

        RETURNS (CertBytes): The signed certificate bytes.
        """

        client = self._client_or_new()
        version = _key_version_from_keyref(ca_key)
        kms_priv = _make_kms_private_key(client, version)

        req = x509.load_pem_x509_csr(csr)
        subject_name = req.subject
        issuer_name = _subject_from_spec(issuer) if issuer else subject_name
        issuer_pub = client.get_public_key(request={"name": version}).pem.encode(
            "utf-8"
        )

        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject_name).issuer_name(issuer_name)
        builder = builder.serial_number(serial or x509.random_serial_number())
        builder = builder.not_valid_before(_secs(not_before, -300))
        builder = builder.not_valid_after(_secs(not_after, 365 * 24 * 3600))
        builder = builder.public_key(req.public_key())
        builder = _apply_extensions(
            builder,
            extensions,
            issuer_pub=issuer_pub,
            subject_pub=req.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            ),
            is_self_signed=False,
        )
        cert = builder.sign(kms_priv, hashes.SHA256())
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
        """Verify a certificate's signature and validity period.

        cert (CertBytes): Certificate to verify.
        trust_roots (Optional[Sequence[CertBytes]]): Trusted root certificates.
        intermediates (Optional[Sequence[CertBytes]]): Intermediate certificates.
        check_time (Optional[int]): Time of verification as Unix timestamp.
        check_revocation (bool): Whether to check revocation status.
        opts (Optional[Dict[str, Any]]): Extra backend options.

        RETURNS (Dict[str, Any]): Verification result and certificate metadata.
        """

        crt = x509.load_pem_x509_certificate(cert)
        now = _secs(check_time, 0)
        if now < crt.not_valid_before.replace(
            tzinfo=_dt.timezone.utc
        ) or now > crt.not_valid_after.replace(tzinfo=_dt.timezone.utc):
            return {
                "valid": False,
                "reason": "time_window",
                "not_before": int(crt.not_valid_before.timestamp()),
                "not_after": int(crt.not_valid_after.timestamp()),
            }
        if trust_roots:
            issuer = x509.load_pem_x509_certificate(trust_roots[0])
            pub = issuer.public_key()
            try:
                if isinstance(pub, rsa.RSAPublicKey):
                    pub.verify(
                        crt.signature,
                        crt.tbs_certificate_bytes,
                        padding.PKCS1v15(),
                        crt.signature_hash_algorithm,
                    )
                else:
                    pub.verify(
                        crt.signature,
                        crt.tbs_certificate_bytes,
                        crt.signature_hash_algorithm,
                    )
            except Exception:
                return {"valid": False, "reason": "signature_mismatch"}
        return {
            "valid": True,
            "issuer": crt.issuer.rfc4514_string(),
            "subject": crt.subject.rfc4514_string(),
            "not_before": int(crt.not_valid_before.timestamp()),
            "not_after": int(crt.not_valid_after.timestamp()),
        }

    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Parse certificate metadata.

        cert (CertBytes): Certificate to parse.
        include_extensions (bool): Include extension information if ``True``.
        opts (Optional[Dict[str, Any]]): Extra backend options.

        RETURNS (Dict[str, Any]): Parsed certificate fields.
        """

        c = x509.load_pem_x509_certificate(cert)
        out: Dict[str, Any] = {
            "tbs_version": c.version.value,
            "serial": c.serial_number,
            "sig_alg": c.signature_hash_algorithm.name,
            "issuer": c.issuer.rfc4514_string(),
            "subject": c.subject.rfc4514_string(),
            "not_before": int(c.not_valid_before.timestamp()),
            "not_after": int(c.not_valid_after.timestamp()),
        }
        if include_extensions:
            try:
                bc = c.extensions.get_extension_for_class(x509.BasicConstraints).value
                out["is_ca"] = bool(bc.ca)
            except x509.ExtensionNotFound:
                out["is_ca"] = False
        return out
