from __future__ import annotations

import base64
import datetime as dt
import hashlib
import os
from typing import (
    Any,
    Dict,
    Iterable,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    CertBytes,
    CsrBytes,
    SubjectSpec,
    CertExtensionSpec,
)
from swarmauri_core.crypto.types import KeyRef

try:
    import boto3
except Exception:  # pragma: no cover
    boto3 = None

from cryptography import x509 as cx509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from asn1crypto import algos as a_algos
from asn1crypto import core as a_core
from asn1crypto import x509 as ax509


__all__ = ["AwsKmsCertService"]


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _to_utc(ts: Optional[int], *, default: Optional[int] = None) -> dt.datetime:
    if ts is None:
        ts = default if default is not None else int(_now_utc().timestamp())
    return dt.datetime.fromtimestamp(int(ts), tz=dt.timezone.utc)


def _pem(data_der: bytes, header: str) -> bytes:
    b64 = base64.encodebytes(data_der).replace(b"\n", b"")
    lines = [b64[i : i + 64] for i in range(0, len(b64), 64)]
    body = b"\n".join(lines)
    return (
        b"-----BEGIN "
        + header.encode()
        + b"-----\n"
        + body
        + b"\n-----END "
        + header.encode()
        + b"-----\n"
    )


def _name_from_subject_spec(spec: SubjectSpec) -> ax509.Name:
    mapping = (
        ("C", "country_name"),
        ("ST", "state_or_province_name"),
        ("L", "locality_name"),
        ("O", "organization_name"),
        ("OU", "organizational_unit_name"),
        ("CN", "common_name"),
        ("emailAddress", "email_address"),
    )
    attrs: dict[str, str] = {}
    for short, long_name in mapping:
        v = spec.get(short)
        if v:
            attrs[long_name] = v
    extra = spec.get("extra_rdns") or {}
    attrs.update(extra)
    return ax509.Name.build(attrs)


def _cryptography_name_from_spec(spec: SubjectSpec) -> cx509.Name:
    attrs: list[cx509.NameAttribute] = []
    oid_map = {
        "C": cx509.NameOID.COUNTRY_NAME,
        "ST": cx509.NameOID.STATE_OR_PROVINCE_NAME,
        "L": cx509.NameOID.LOCALITY_NAME,
        "O": cx509.NameOID.ORGANIZATION_NAME,
        "OU": cx509.NameOID.ORGANIZATIONAL_UNIT_NAME,
        "CN": cx509.NameOID.COMMON_NAME,
        "emailAddress": cx509.NameOID.EMAIL_ADDRESS,
    }
    for k, oid in oid_map.items():
        v = spec.get(k)
        if v:
            attrs.append(cx509.NameAttribute(oid, v))
    extra = spec.get("extra_rdns") or {}
    for k, v in extra.items():
        attrs.append(cx509.NameAttribute(cx509.ObjectIdentifier(k), v))
    return cx509.Name(attrs)


def _spki_from_csr(csr: cx509.CertificateSigningRequest) -> ax509.PublicKeyInfo:
    spki_der = csr.public_key().public_bytes(
        Encoding.DER, PublicFormat.SubjectPublicKeyInfo
    )
    return ax509.PublicKeyInfo.load(spki_der)


def _skid_from_pub(pub: Union[cx509.PublicKey, ax509.PublicKeyInfo]) -> bytes:
    if isinstance(pub, ax509.PublicKeyInfo):
        pk_bytes = pub["public_key"].native
    else:
        spki_der = pub.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        spki = ax509.PublicKeyInfo.load(spki_der)
        pk_bytes = spki["public_key"].native
    return hashlib.sha1(bytes(pk_bytes)).digest()


def _akid_from_issuer_pub(
    issuer_pub: Union[cx509.PublicKey, ax509.PublicKeyInfo],
) -> bytes:
    return _skid_from_pub(issuer_pub)


class _SigAlg:
    def __init__(self, tbs_alg: a_algos.AlgorithmIdentifier, kms_alg: str) -> None:
        self.tbs_alg = tbs_alg
        self.kms_alg = kms_alg


def _rsa_pss_sha256_alg() -> _SigAlg:
    params = a_algos.RSASSAPSSParams(
        {
            "hash_algorithm": a_algos.DigestAlgorithm({"algorithm": "sha256"}),
            "mask_gen_algorithm": a_algos.MaskGenAlgorithm(
                {
                    "algorithm": "mgf1",
                    "parameters": a_algos.DigestAlgorithm({"algorithm": "sha256"}),
                }
            ),
            "salt_length": 32,
            "trailer_field": 1,
        }
    )
    alg = a_algos.AlgorithmIdentifier(
        {"algorithm": "1.2.840.113549.1.1.10", "parameters": params}
    )
    return _SigAlg(alg, "RSASSA_PSS_SHA_256")


def _rsa_pkcs1_sha256_alg() -> _SigAlg:
    alg = a_algos.AlgorithmIdentifier({"algorithm": "1.2.840.113549.1.1.11"})
    return _SigAlg(alg, "RSASSA_PKCS1_V1_5_SHA_256")


def _ecdsa_sha256_alg() -> _SigAlg:
    alg = a_algos.AlgorithmIdentifier({"algorithm": "ecdsa_sha256"})
    return _SigAlg(alg, "ECDSA_SHA_256")


def _pick_alg(sig_alg: Optional[str]) -> _SigAlg:
    if sig_alg in (None, "RSA-PSS-SHA256", "RSASSA-PSS-SHA256"):
        return _rsa_pss_sha256_alg()
    if sig_alg in ("RSA-SHA256", "RSASSA-PKCS1v1_5-SHA256", "RS256"):
        return _rsa_pkcs1_sha256_alg()
    if sig_alg in ("ECDSA-P256-SHA256", "ECDSA-SHA256", "ES256"):
        return _ecdsa_sha256_alg()
    raise ValueError(
        "Unsupported signature algorithm '{sig_alg}'. "
        "Use one of: RSA-PSS-SHA256 | RSA-SHA256 | ECDSA-P256-SHA256"
    )


def _ensure_boto3():
    if boto3 is None:
        raise RuntimeError(
            "AwsKmsCertService requires boto3. Install with: pip install boto3"
        )


def _normalize_bytes_maybe_pem(data: bytes) -> Tuple[bytes, str]:
    t = data.strip()
    if t.startswith(b"-----BEGIN "):
        header = t.splitlines()[0].decode()
        if "CERTIFICATE REQUEST" in header or "NEW CERTIFICATE REQUEST" in header:
            kind = "CERTIFICATE REQUEST"
        elif "CERTIFICATE" in header:
            kind = "CERTIFICATE"
        else:
            raise ValueError("Unsupported PEM header")
        lines = [ln for ln in t.splitlines() if b"-----" not in ln]
        der = base64.b64decode(b"".join(lines))
        return der, kind
    try:
        cx509.load_der_x509_csr(t)
        return t, "CERTIFICATE REQUEST"
    except Exception:
        pass
    try:
        cx509.load_der_x509_certificate(t)
        return t, "CERTIFICATE"
    except Exception:
        pass
    return t, "CERTIFICATE"


def _issuer_name_from_cert_pem(issuer_cert_pem: bytes) -> ax509.Name:
    c = cx509.load_pem_x509_certificate(issuer_cert_pem)
    name_der = c.subject.public_bytes(Encoding.DER)
    return ax509.Name.load(name_der)


def _cert_to_pem(cert: ax509.Certificate) -> bytes:
    return _pem(cert.dump(), "CERTIFICATE")


def _cx509_name_to_ax509_name(name: cx509.Name) -> ax509.Name:
    return ax509.Name.load(name.public_bytes(Encoding.DER))


def _mk_validity(not_before: dt.datetime, not_after: dt.datetime) -> ax509.Validity:
    return ax509.Validity(
        {
            "not_before": ax509.Time({"utc_time": not_before}),
            "not_after": ax509.Time({"utc_time": not_after}),
        }
    )


def _rand_serial_160() -> int:
    b = bytearray(os.urandom(20))
    b[0] &= 0x7F
    return int.from_bytes(bytes(b), "big")


def _aws_kms_pubkey_info(kms_client, key_id: str) -> Tuple[ax509.PublicKeyInfo, str]:
    resp = kms_client.get_public_key(KeyId=key_id)
    spki = ax509.PublicKeyInfo.load(resp["PublicKey"])
    key_spec: str = resp.get("KeySpec", "")
    return spki, key_spec


def _csr_copy_extensions(csr: cx509.CertificateSigningRequest) -> list[ax509.Extension]:
    exts: list[ax509.Extension] = []
    for ext in csr.extensions:
        exts.append(
            ax509.Extension(
                {
                    "extn_id": ax509.ExtensionId(ext.oid.dotted_string),
                    "critical": ext.critical,
                    "extn_value": a_core.OctetString(
                        ext.value.public_bytes(Encoding.DER)
                    ),
                }
            )
        )
    return exts


def _combine_extensions(
    csr_exts: list[ax509.Extension],
    extra: Optional[CertExtensionSpec],
    subject_pub: ax509.PublicKeyInfo,
    issuer_pub: Optional[ax509.PublicKeyInfo],
) -> ax509.Extensions:
    by_oid: Dict[str, ax509.Extension] = {
        ext["extn_id"].native: ext for ext in csr_exts
    }
    skid = _skid_from_pub(subject_pub)
    by_oid["subject_key_identifier"] = ax509.Extension(
        {
            "extn_id": "subject_key_identifier",
            "critical": False,
            "extn_value": ax509.SubjectKeyIdentifier(skid),
        }
    )
    if issuer_pub is not None:
        akid = _akid_from_issuer_pub(issuer_pub)
        by_oid["authority_key_identifier"] = ax509.Extension(
            {
                "extn_id": "authority_key_identifier",
                "critical": False,
                "extn_value": ax509.AuthorityKeyIdentifier({"key_identifier": akid}),
            }
        )
    return ax509.Extensions(list(by_oid.values()))


def _build_tbs_from_csr(
    csr: cx509.CertificateSigningRequest,
    issuer_name: ax509.Name,
    serial: Optional[int],
    not_before: dt.datetime,
    not_after: dt.datetime,
    sig_alg: _SigAlg,
    issuer_spki: Optional[ax509.PublicKeyInfo],
) -> Tuple[ax509.TbsCertificate, ax509.PublicKeyInfo]:
    subject_name_ax = _cx509_name_to_ax509_name(csr.subject)
    sub_spki = _spki_from_csr(csr)
    exts = _combine_extensions(
        _csr_copy_extensions(csr),
        extra=None,
        subject_pub=sub_spki,
        issuer_pub=issuer_spki,
    )
    tbs = ax509.TbsCertificate(
        {
            "version": "v3",
            "serial_number": serial if serial is not None else _rand_serial_160(),
            "signature": sig_alg.tbs_alg,
            "issuer": issuer_name,
            "validity": _mk_validity(not_before, not_after),
            "subject": subject_name_ax,
            "subject_public_key_info": sub_spki,
            "extensions": exts,
        }
    )
    return tbs, sub_spki


def _assemble_cert(
    tbs: ax509.TbsCertificate, sig_alg: _SigAlg, signature_bytes: bytes
) -> ax509.Certificate:
    return ax509.Certificate(
        {
            "tbs_certificate": tbs,
            "signature_algorithm": sig_alg.tbs_alg,
            "signature_value": a_core.BitString.from_bytes(signature_bytes),
        }
    )


def _kms_sign(kms, key_id: str, alg: _SigAlg, tbs_der: bytes) -> bytes:
    resp = kms.sign(
        KeyId=key_id, Message=tbs_der, MessageType="RAW", SigningAlgorithm=alg.kms_alg
    )
    return resp["Signature"]


def _extract_kms_key_id_from_keyref(ca_key: KeyRef) -> str:
    if ca_key.tags and "aws_kms_key_id" in ca_key.tags:
        return str(ca_key.tags["aws_kms_key_id"])
    if ca_key.tags and "kms_key_id" in ca_key.tags:
        return str(ca_key.tags["kms_key_id"])
    if ca_key.kid:
        return str(ca_key.kid)
    raise ValueError(
        "AwsKmsCertService: unable to resolve KMS KeyId from KeyRef (expected tags['aws_kms_key_id'] or kid)."
    )


@ComponentBase.register_type(CertServiceBase, "AwsKmsCertService")
class AwsKmsCertService(CertServiceBase):
    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["AwsKmsCertService"] = "AwsKmsCertService"

    def __init__(
        self,
        *,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        session: Optional["boto3.session.Session"] = None,  # type: ignore[name-defined]
        default_sig_alg: str = "RSA-PSS-SHA256",
    ) -> None:
        super().__init__()
        self._region = region_name
        self._endpoint = endpoint_url
        self._session = session
        self._default_sig_alg = default_sig_alg
        self._kms = None

    def _client(self):
        _ensure_boto3()
        if self._kms is not None:
            return self._kms
        sess = self._session or boto3.session.Session()
        self._kms = sess.client(
            "kms", region_name=self._region, endpoint_url=self._endpoint
        )
        return self._kms

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "RSA-4096", "EC-P256", "EC-P384"),
            "sig_algs": ("RSA-PSS-SHA256", "RSA-SHA256", "ECDSA-P256-SHA256"),
            "features": (
                "sign_from_csr",
                "self_signed",
                "verify",
                "parse",
                "akid",
                "skid",
            ),
            "profiles": ("server", "client", "intermediate", "root"),
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
        if not key.material:
            raise NotImplementedError(
                "create_csr requires exportable private key material in KeyRef.material"
            )

        priv = serialization.load_pem_private_key(key.material, password=None)
        builder = cx509.CertificateSigningRequestBuilder().subject_name(
            _cryptography_name_from_spec(subject)
        )

        san_list: list[cx509.GeneralName] = []
        if san:
            for d in san.get("dns") or []:
                san_list.append(cx509.DNSName(d))
            for ip in san.get("ip") or []:
                san_list.append(cx509.IPAddress(cx509.ipaddress.ip_address(ip)))
            for uri in san.get("uri") or []:
                san_list.append(cx509.UniformResourceIdentifier(uri))
            for em in san.get("email") or []:
                san_list.append(cx509.RFC822Name(em))
            if san_list:
                builder = builder.add_extension(
                    cx509.SubjectAlternativeName(san_list), critical=False
                )

        chosen_hash = hashes.SHA256()
        csr = builder.sign(priv, chosen_hash)
        der = csr.public_bytes(Encoding.DER)
        return (
            der
            if output_der
            else cx509.load_der_x509_csr(der).public_bytes(Encoding.PEM)
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
        kms = self._client()
        key_id = _extract_kms_key_id_from_keyref(key)
        sig = _pick_alg(sig_alg or self._default_sig_alg)
        issuer_name_ax = _name_from_subject_spec(subject)
        issuer_spki, _ = _aws_kms_pubkey_info(kms, key_id)

        nbf = _to_utc(not_before, default=int(_now_utc().timestamp() - 300))
        naf = _to_utc(
            not_after, default=int((_now_utc() + dt.timedelta(days=365)).timestamp())
        )

        tbs = ax509.TbsCertificate(
            {
                "version": "v3",
                "serial_number": serial if serial is not None else _rand_serial_160(),
                "signature": sig.tbs_alg,
                "issuer": issuer_name_ax,
                "validity": _mk_validity(nbf, naf),
                "subject": issuer_name_ax,
                "subject_public_key_info": issuer_spki,
                "extensions": ax509.Extensions(
                    [
                        ax509.Extension(
                            {
                                "extn_id": "basic_constraints",
                                "critical": True,
                                "extn_value": ax509.BasicConstraints(
                                    {"ca": True, "path_len_constraint": 1}
                                ),
                            }
                        ),
                        ax509.Extension(
                            {
                                "extn_id": "subject_key_identifier",
                                "critical": False,
                                "extn_value": ax509.SubjectKeyIdentifier(
                                    _skid_from_pub(issuer_spki)
                                ),
                            }
                        ),
                    ]
                ),
            }
        )

        tbs_der = tbs.dump()
        signature = _kms_sign(kms, key_id, sig, tbs_der)
        cert = _assemble_cert(tbs, sig, signature)
        der = cert.dump()
        return der if output_der else _cert_to_pem(cert)

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
        kms = self._client()
        key_id = _extract_kms_key_id_from_keyref(ca_key)
        sig = _pick_alg(sig_alg or self._default_sig_alg)

        csr_der, kind = _normalize_bytes_maybe_pem(csr)
        if kind != "CERTIFICATE REQUEST":
            raise ValueError("sign_cert expects a CSR (PKCS#10)")
        csr_obj = cx509.load_der_x509_csr(csr_der)

        if ca_cert is not None:
            ic_der, _ = _normalize_bytes_maybe_pem(ca_cert)
            ic = cx509.load_der_x509_certificate(ic_der)
            issuer_name_ax = _cx509_name_to_ax509_name(ic.subject)
            issuer_spki = ax509.PublicKeyInfo.load(
                ic.public_key().public_bytes(
                    Encoding.DER, PublicFormat.SubjectPublicKeyInfo
                )
            )
        else:
            if issuer is None:
                raise ValueError(
                    "sign_cert: either 'ca_cert' or 'issuer' must be provided"
                )
            issuer_name_ax = _name_from_subject_spec(issuer)
            issuer_spki, _ = _aws_kms_pubkey_info(kms, key_id)

        nbf = _to_utc(not_before, default=int(_now_utc().timestamp() - 300))
        naf = _to_utc(
            not_after, default=int((_now_utc() + dt.timedelta(days=365)).timestamp())
        )

        tbs, _ = _build_tbs_from_csr(
            csr_obj, issuer_name_ax, serial, nbf, naf, sig, issuer_spki
        )
        signature = _kms_sign(kms, key_id, sig, tbs.dump())
        cert = _assemble_cert(tbs, sig, signature)
        der = cert.dump()
        return der if output_der else _cert_to_pem(cert)

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
        der, _ = _normalize_bytes_maybe_pem(cert)
        c = cx509.load_der_x509_certificate(der)

        now = _to_utc(check_time) if check_time else _now_utc()
        if c.not_valid_before > now or c.not_valid_after < now:
            return {
                "valid": False,
                "reason": "time_window",
                "not_before": int(c.not_valid_before.timestamp()),
                "not_after": int(c.not_valid_after.timestamp()),
            }

        issuer_cert: Optional[cx509.Certificate] = None
        seq = list(intermediates or []) + list(trust_roots or [])
        for cand in seq:
            cd, _ = _normalize_bytes_maybe_pem(cand)
            try:
                issuer_cert = cx509.load_der_x509_certificate(cd)
                if issuer_cert.subject == c.issuer:
                    break
                issuer_cert = None
            except Exception:
                continue

        if issuer_cert is None:
            return {
                "valid": True,
                "reason": None,
                "issuer_known": False,
                "subject": c.subject.rfc4514_string(),
                "not_before": int(c.not_valid_before.timestamp()),
                "not_after": int(c.not_valid_after.timestamp()),
            }

        pub = issuer_cert.public_key()
        tbs = c.tbs_certificate_bytes
        try:
            sa = c.signature_algorithm_oid
            if sa._name in ("sha256_rsa", "sha384_rsa", "sha512_rsa"):
                pub.verify(
                    c.signature, tbs, padding.PKCS1v15(), c.signature_hash_algorithm
                )
            elif (
                sa.dotted_string == cx509.SignatureAlgorithmOID.RSASSA_PSS.dotted_string
            ):
                pub.verify(
                    c.signature,
                    tbs,
                    padding.PSS(
                        mgf=padding.MGF1(c.signature_hash_algorithm),
                        salt_length=c.signature_hash_algorithm.digest_size,
                    ),
                    c.signature_hash_algorithm,
                )
            elif sa._name in (
                "ecdsa_with_sha256",
                "ecdsa_with_sha384",
                "ecdsa_with_sha512",
            ):
                pub.verify(c.signature, tbs, ec.ECDSA(c.signature_hash_algorithm))
            else:
                raise ValueError(
                    f"Unsupported signature algorithm for verify: {sa._name}"
                )
        except Exception as e:  # pragma: no cover - errors tested via failure cases
            return {"valid": False, "reason": f"signature:{e.__class__.__name__}"}

        return {
            "valid": True,
            "reason": None,
            "issuer_known": True,
            "issuer": issuer_cert.subject.rfc4514_string(),
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
        der, _ = _normalize_bytes_maybe_pem(cert)
        c = cx509.load_der_x509_certificate(der)

        out: Dict[str, Any] = {
            "serial": c.serial_number,
            "sig_alg": c.signature_algorithm_oid.dotted_string,
            "issuer": c.issuer.rfc4514_string(),
            "subject": c.subject.rfc4514_string(),
            "not_before": int(c.not_valid_before.timestamp()),
            "not_after": int(c.not_valid_after.timestamp()),
            "is_ca": False,
        }
        if include_extensions:
            try:
                bc = c.extensions.get_extension_for_class(cx509.BasicConstraints).value
                out["is_ca"] = bool(bc.ca)
                if bc.path_length is not None:
                    out["path_len"] = bc.path_length
            except Exception:
                pass
            try:
                san = c.extensions.get_extension_for_class(
                    cx509.SubjectAlternativeName
                ).value
                out["san"] = {
                    "dns": [n.value for n in san.get_values_for_type(cx509.DNSName)],
                    "ip": [
                        str(n.value) for n in san.get_values_for_type(cx509.IPAddress)
                    ],
                    "uri": [
                        n.value
                        for n in san.get_values_for_type(
                            cx509.UniformResourceIdentifier
                        )
                    ],
                    "email": [
                        n.value for n in san.get_values_for_type(cx509.RFC822Name)
                    ],
                }
            except Exception:
                pass
            try:
                ku = c.extensions.get_extension_for_class(cx509.KeyUsage).value
                out["key_usage"] = {
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
                eku = c.extensions.get_extension_for_class(cx509.ExtendedKeyUsage).value
                out["eku"] = [oid.dotted_string for oid in eku]
            except Exception:
                pass
        return out
