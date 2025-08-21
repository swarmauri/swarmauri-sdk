from __future__ import annotations

import base64
import binascii
import datetime as dt
import hashlib
import os
from typing import Dict, Iterable, Literal, Optional, Sequence, Tuple

from pydantic import Field

# --- deps: runtime checks (clear error if missing) ----------------------------
try:
    import pkcs11  # python-pkcs11
    from pkcs11 import Attribute, Mechanism, ObjectClass, PKCS11Error
except Exception as e:  # pragma: no cover
    raise ImportError(
        "Pkcs11CertService requires 'python-pkcs11'. Install with: pip install python-pkcs11"
    ) from e

try:
    # cryptography for parsing/generating SPKIs; quick verifications
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa, padding
except Exception as e:  # pragma: no cover
    raise ImportError(
        "Pkcs11CertService requires 'cryptography'. Install with: pip install cryptography"
    ) from e

try:
    # asn1crypto for flexible CSR/Cert assembly with injected external signatures
    from asn1crypto import algos as asn1_algos
    from asn1crypto import csr as asn1_csr
    from asn1crypto import keys as asn1_keys
    from asn1crypto import x509 as asn1_x509
except Exception as e:  # pragma: no cover
    raise ImportError(
        "Pkcs11CertService requires 'asn1crypto'. Install with: pip install asn1crypto"
    ) from e


# --- your framework surfaces ---------------------------------------------------
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    CertExtensionSpec,
    SubjectSpec,
)
from swarmauri_core.crypto.types import (
    KeyRef,
)  # kid, version, material/public, tags, export_policy


# ---------- helpers ------------------------------------------------------------
def _pem_or_der_to_asn1_pub(pub_bytes: bytes) -> asn1_keys.PublicKeyInfo:
    """Accept PEM or DER public key bytes; return asn1crypto PublicKeyInfo."""
    if b"-----BEGIN" in pub_bytes:
        pub = serialization.load_pem_public_key(pub_bytes)
        der = pub.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    else:
        der = pub_bytes
    return asn1_keys.PublicKeyInfo.load(der)


def _pem_or_der_to_asn1_csr(csr_bytes: bytes) -> asn1_csr.CertificationRequest:
    if b"-----BEGIN" in csr_bytes:
        csr = x509.load_pem_x509_csr(csr_bytes)
        der = csr.public_bytes(serialization.Encoding.DER)
        return asn1_csr.CertificationRequest.load(der)
    return asn1_csr.CertificationRequest.load(csr_bytes)


def _asn1_to_pem_cert(cert: asn1_x509.Certificate) -> bytes:
    b = cert.dump()
    return (
        b"-----BEGIN CERTIFICATE-----\n"
        + base64.encodebytes(b).replace(b"\n", b"\n")[0:-1].replace(b"\n", b"\n")
        + b"\n-----END CERTIFICATE-----\n"
    )


def _asn1_to_pem_csr(req: asn1_csr.CertificationRequest) -> bytes:
    b = req.dump()
    return (
        b"-----BEGIN CERTIFICATE REQUEST-----\n"
        + base64.encodebytes(b)
        + b"-----END CERTIFICATE REQUEST-----\n"
    )


def _name_from_subject_spec(spec: SubjectSpec) -> asn1_x509.Name:
    rdns = []
    mapping = [
        ("C", "country_name"),
        ("ST", "state_or_province_name"),
        ("L", "locality_name"),
        ("O", "organization_name"),
        ("OU", "organizational_unit_name"),
        ("CN", "common_name"),
        ("emailAddress", "email_address"),
    ]
    for k, oid_name in mapping:
        v = spec.get(k)
        if v:
            rdns.append(asn1_x509.NameType.build({oid_name: v}))
    for k, v in (spec.get("extra_rdns") or {}).items():
        rdns.append(asn1_x509.NameType.build({k: v}))
    return (
        asn1_x509.Name.build({"rdn_sequence": [[*rdns]]})
        if rdns
        else asn1_x509.Name.build({})
    )


def _extensions_from_spec(
    spki: asn1_keys.PublicKeyInfo,
    ext: Optional[CertExtensionSpec],
    issuer_spki: Optional[asn1_keys.PublicKeyInfo] = None,
) -> asn1_x509.Extensions:
    ext = ext or {}
    out: list[asn1_x509.Extension] = []

    # basicConstraints
    bc = ext.get("basic_constraints")
    if bc:
        out.append(
            asn1_x509.Extension(
                {
                    "extn_id": "basic_constraints",
                    "critical": True,
                    "extn_value": asn1_x509.BasicConstraints(
                        {
                            "ca": bool(bc.get("ca", False)),
                            "path_len_constraint": bc.get("path_len"),
                        }
                    ),
                }
            )
        )

    # keyUsage
    ku = ext.get("key_usage")
    if ku:
        out.append(
            asn1_x509.Extension(
                {
                    "extn_id": "key_usage",
                    "critical": True,
                    "extn_value": asn1_x509.KeyUsage(
                        {
                            "digital_signature": ku.get("digital_signature", False),
                            "content_commitment": ku.get("content_commitment", False),
                            "key_encipherment": ku.get("key_encipherment", False),
                            "data_encipherment": ku.get("data_encipherment", False),
                            "key_agreement": ku.get("key_agreement", False),
                            "key_cert_sign": ku.get("key_cert_sign", False),
                            "crl_sign": ku.get("crl_sign", False),
                            "encipher_only": ku.get("encipher_only", False),
                            "decipher_only": ku.get("decipher_only", False),
                        }
                    ),
                }
            )
        )

    # extendedKeyUsage
    eku = ext.get("extended_key_usage")
    if eku and eku.get("oids"):
        ekus = []
        for o in eku["oids"]:
            if o == "serverAuth":
                ekus.append(asn1_x509.KeyPurposeId("server_auth"))
            elif o == "clientAuth":
                ekus.append(asn1_x509.KeyPurposeId("client_auth"))
            elif o == "codeSigning":
                ekus.append(asn1_x509.KeyPurposeId("code_signing"))
            elif o == "emailProtection":
                ekus.append(asn1_x509.KeyPurposeId("email_protection"))
            else:
                ekus.append(asn1_x509.KeyPurposeId(o))
        out.append(
            asn1_x509.Extension(
                {
                    "extn_id": "extended_key_usage",
                    "critical": False,
                    "extn_value": asn1_x509.ExtKeyUsageSyntax(ekus),
                }
            )
        )

    # subjectAltName
    san = ext.get("subject_alt_name") or {}
    if san:
        gns = []
        for d in san.get("dns", []) or []:
            gns.append(asn1_x509.GeneralName(name="dNSName", value=d))
        for ip in san.get("ip", []) or []:
            gns.append(asn1_x509.GeneralName(name="iPAddress", value=ip))
        for uri in san.get("uri", []) or []:
            gns.append(
                asn1_x509.GeneralName(name="uniformResourceIdentifier", value=uri)
            )
        for em in san.get("email", []) or []:
            gns.append(asn1_x509.GeneralName(name="rfc822Name", value=em))
        if gns:
            out.append(
                asn1_x509.Extension(
                    {
                        "extn_id": "subject_alt_name",
                        "critical": False,
                        "extn_value": asn1_x509.GeneralNames(gns),
                    }
                )
            )

    # Subject Key Identifier
    if ext.get("subject_key_identifier"):
        spk = spki["public_key"].native
        skid = hashlib.sha1(spk).digest()
        out.append(
            asn1_x509.Extension(
                {
                    "extn_id": "subject_key_identifier",
                    "critical": False,
                    "extn_value": skid,
                }
            )
        )

    # Authority Key Identifier
    if ext.get("authority_key_identifier") and issuer_spki is not None:
        ipk = issuer_spki["public_key"].native
        akid = hashlib.sha1(ipk).digest()
        out.append(
            asn1_x509.Extension(
                {
                    "extn_id": "authority_key_identifier",
                    "critical": False,
                    "extn_value": asn1_x509.AuthorityKeyIdentifier(
                        {"key_identifier": akid}
                    ),
                }
            )
        )

    # provider-specific extras (pass-through)
    for k, v in (ext.get("extra") or {}).items():
        out.append(
            asn1_x509.Extension(
                {
                    "extn_id": k,
                    "critical": False,
                    "extn_value": v,
                }
            )
        )

    return asn1_x509.Extensions(out)


def _now_epoch() -> int:
    return int(dt.datetime.utcnow().timestamp())


def _utc_time(ts: Optional[int]) -> asn1_x509.Time:
    if ts is None:
        ts = _now_epoch()
    return asn1_x509.Time(dt.datetime.utcfromtimestamp(int(ts)))


def _coerce_pem(data: bytes, hdr: bytes, ftr: bytes) -> bytes:
    if b"-----BEGIN" in data:
        return data
    return hdr + base64.encodebytes(data) + ftr


# ---------- PKCS#11 session & signatures --------------------------------------
class _Pkcs11Session:
    """Context manager to open + close an HSM session."""

    def __init__(
        self,
        module_path: str,
        *,
        token_label: Optional[str] = None,
        slot_id: Optional[int] = None,
        pin: Optional[str] = None,
        user_type: Literal["USER", "SO"] = "USER",
    ) -> None:
        self._module = pkcs11.lib(
            pkcs11.get_os_module_path(module_path)
            if hasattr(pkcs11, "get_os_module_path")
            else module_path
        )
        self._slot_id = slot_id
        self._token_label = token_label
        self._pin = pin
        self._user_type = (
            pkcs11.UserType.SO if user_type == "SO" else pkcs11.UserType.USER
        )
        self._session = None

    def __enter__(self):
        if self._slot_id is not None:
            slot = [s for s in self._module.get_slots() if s.slot_id == self._slot_id][
                0
            ]
            token = slot.get_token()
        elif self._token_label is not None:
            token = next(
                t for t in self._module.get_tokens() if t.label == self._token_label
            )
        else:
            token = self._module.get_tokens()[0]
        self._session = token.open(user_type=self._user_type, pin=self._pin)
        return self._session

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._session is not None:
                self._session.close()
        finally:
            self._session = None


def _find_private_key(
    session: pkcs11.Session,
    *,
    pkcs11_uri: Optional[str] = None,
    label: Optional[str] = None,
    key_id: Optional[bytes] = None,
) -> pkcs11.PrivateKey:
    query = {Attribute.CLASS: ObjectClass.PRIVATE_KEY}
    if label:
        query[Attribute.LABEL] = label
    if key_id:
        query[Attribute.ID] = key_id
    obj = next(iter(session.get_objects(query)), None)
    if not obj:
        raise RuntimeError("PKCS#11 private key not found with provided attributes")
    return obj  # type: ignore[return-value]


def _rsa_pss_sha256_params():
    return pkcs11.mechanisms.RSAPSSParams(
        hash=Mechanism.SHA256, mgf=pkcs11.Mechanism.SHA256, salt_len=32
    )


def _sign_with_pkcs11(
    session: pkcs11.Session,
    priv: pkcs11.PrivateKey,
    *,
    algorithm: str,
    tbs: bytes,
) -> bytes:
    if algorithm == "RSA-PSS-SHA256":
        try:
            return priv.sign(
                tbs,
                mechanism=Mechanism.SHA256_RSA_PKCS_PSS,
                mechanism_param=_rsa_pss_sha256_params(),
            )
        except PKCS11Error:
            return priv.sign(
                tbs,
                mechanism=Mechanism.RSA_PKCS_PSS,
                mechanism_param=_rsa_pss_sha256_params(),
            )

    if algorithm == "ECDSA-P256-SHA256":
        try:
            sig = priv.sign(tbs, mechanism=Mechanism.ECDSA_SHA256)
        except PKCS11Error:
            digest = hashlib.sha256(tbs).digest()
            sig = priv.sign(digest, mechanism=Mechanism.ECDSA)
        size = 32
        if len(sig) == 64:
            r = int.from_bytes(sig[:size], "big")
            s = int.from_bytes(sig[size:], "big")
            from asn1crypto.core import Integer, Sequence

            return Sequence([Integer(r), Integer(s)]).dump()
        return sig

    if algorithm == "Ed25519":
        return priv.sign(tbs, mechanism=Mechanism.EDDSA)

    raise ValueError(f"Unsupported signature algorithm for PKCS#11: {algorithm}")


def _sig_alg_identifier(alg: str) -> asn1_algos.SignedDigestAlgorithm:
    if alg == "RSA-PSS-SHA256":
        return asn1_algos.SignedDigestAlgorithm(
            {
                "algorithm": "rsassa_pss",
                "parameters": asn1_algos.RSASSAPSSParams(
                    {
                        "hash_algorithm": asn1_algos.DigestAlgorithm(
                            {"algorithm": "sha256"}
                        ),
                        "mask_gen_algorithm": asn1_algos.MaskGenAlgorithm(
                            {
                                "algorithm": "mgf1",
                                "parameters": asn1_algos.DigestAlgorithm(
                                    {"algorithm": "sha256"}
                                ),
                            }
                        ),
                        "salt_length": 32,
                        "trailer_field": 1,
                    }
                ),
            }
        )
    if alg == "ECDSA-P256-SHA256":
        return asn1_algos.SignedDigestAlgorithm({"algorithm": "ecdsa_with_sha256"})
    if alg == "Ed25519":
        return asn1_algos.SignedDigestAlgorithm({"algorithm": "ed25519"})
    raise ValueError(f"Unsupported signature algorithm identifier mapping: {alg}")


def _parse_keyref_pkcs11_attrs(
    ref: KeyRef,
) -> Tuple[Optional[str], Optional[str], Optional[bytes]]:
    tags = ref.tags or {}
    uri = tags.get("pkcs11_uri")
    label = tags.get("label")
    kid_hex = tags.get("id_hex")
    key_id = binascii.unhexlify(kid_hex) if kid_hex else None
    return uri, label, key_id


# ---------- service ------------------------------------------------------------
@ComponentBase.register_type(CertServiceBase, "Pkcs11CertService")
class Pkcs11CertService(CertServiceBase):
    """PKCS#11-backed X.509 certificate service.

    Implements X.509 (RFC 5280) certificate operations and PKCS#10 (RFC 2986)
    certificate signing requests using keys stored in an HSM.
    """

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["Pkcs11CertService"] = "Pkcs11CertService"

    def __init__(
        self,
        module_path: str,
        *,
        token_label: Optional[str] = None,
        slot_id: Optional[int] = None,
        pin: Optional[str] = None,
        user_type: Literal["USER", "SO"] = "USER",
        default_sig_alg: Literal[
            "RSA-PSS-SHA256", "ECDSA-P256-SHA256", "Ed25519"
        ] = "RSA-PSS-SHA256",
    ) -> None:
        super().__init__()
        self._module_path = module_path
        self._token_label = token_label
        self._slot_id = slot_id
        self._pin = pin
        self._user_type = user_type
        self._default_sig_alg = default_sig_alg

    def supports(self) -> Dict[str, Iterable[str]]:
        return {
            "key_algs": ("RSA-2048", "RSA-3072", "EC-P256", "Ed25519"),
            "sig_algs": (
                "RSA-PSS-SHA256",
                "ECDSA-P256-SHA256",
                "Ed25519",
            ),
            "features": (
                "csr",
                "self_signed",
                "sign_from_csr",
                "verify",
                "parse",
                "akid",
                "skid",
                "san",
                "eku",
                "key_usage",
            ),
            "backends": ("pkcs11",),
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
        opts: Optional[Dict[str, object]] = None,
    ) -> bytes:
        """Build a PKCS#10 CSR and sign it with the subject private key (RFC 2986)."""
        if not key.public:
            raise ValueError("KeyRef.public (PEM/DER) is required to create a CSR")

        sig_alg = sig_alg or self._default_sig_alg
        spki = _pem_or_der_to_asn1_pub(key.public)

        subject_name = _name_from_subject_spec(subject)

        req_exts = _extensions_from_spec(spki, extensions)

        attrs = []
        if challenge_password:
            attrs.append(
                asn1_csr.CRIAttribute(
                    {
                        "type": "challenge_password",
                        "values": [challenge_password.encode("utf-8")],
                    }
                )
            )
        if req_exts:
            attrs.append(
                asn1_csr.CRIAttribute(
                    {"type": "extension_request", "values": [req_exts]}
                )
            )

        cri = asn1_csr.CertificationRequestInfo(
            {
                "version": 0,
                "subject": subject_name,
                "subject_pk_info": spki,
                "attributes": asn1_csr.CRIAttributes(attrs)
                if attrs
                else asn1_csr.CRIAttributes([]),
            }
        )

        sig_alg_id = _sig_alg_identifier(sig_alg)
        tbs = cri.dump()

        with _Pkcs11Session(
            self._module_path,
            token_label=self._token_label,
            slot_id=self._slot_id,
            pin=self._pin,
            user_type=self._user_type,
        ) as sess:
            _, label, key_id = _parse_keyref_pkcs11_attrs(key)
            priv = _find_private_key(sess, label=label, key_id=key_id)
            sig = _sign_with_pkcs11(sess, priv, algorithm=sig_alg, tbs=tbs)

        req = asn1_csr.CertificationRequest(
            {
                "certification_request_info": cri,
                "signature_algorithm": sig_alg_id,
                "signature": sig,
            }
        )

        der = req.dump()
        return der if output_der else _asn1_to_pem_csr(req)

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
        opts: Optional[Dict[str, object]] = None,
    ) -> bytes:
        """Create a self-signed certificate using the HSM private key (RFC 5280)."""
        if not key.public:
            raise ValueError("KeyRef.public (PEM/DER) is required")

        sig_alg = sig_alg or self._default_sig_alg
        subject_name = _name_from_subject_spec(subject)
        spki = _pem_or_der_to_asn1_pub(key.public)

        exts = _extensions_from_spec(spki, extensions, issuer_spki=None)

        tbs = asn1_x509.TbsCertificate(
            {
                "version": "v3",
                "serial_number": int(serial or int.from_bytes(os.urandom(8), "big")),
                "signature": _sig_alg_identifier(sig_alg),
                "issuer": subject_name,
                "validity": asn1_x509.Validity(
                    {
                        "not_before": _utc_time(not_before or _now_epoch() - 300),
                        "not_after": _utc_time(
                            not_after or (_now_epoch() + 365 * 24 * 3600)
                        ),
                    }
                ),
                "subject": subject_name,
                "subject_public_key_info": spki,
                "extensions": exts,
            }
        )

        tbs_bytes = tbs.dump()

        with _Pkcs11Session(
            self._module_path,
            token_label=self._token_label,
            slot_id=self._slot_id,
            pin=self._pin,
            user_type=self._user_type,
        ) as sess:
            _, label, key_id = _parse_keyref_pkcs11_attrs(key)
            priv = _find_private_key(sess, label=label, key_id=key_id)
            sig = _sign_with_pkcs11(sess, priv, algorithm=sig_alg, tbs=tbs_bytes)

        cert = asn1_x509.Certificate(
            {
                "tbs_certificate": tbs,
                "signature_algorithm": _sig_alg_identifier(sig_alg),
                "signature_value": sig,
            }
        )

        der = cert.dump()
        return der if output_der else _asn1_to_pem_cert(cert)

    async def sign_cert(
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
        opts: Optional[Dict[str, object]] = None,
    ) -> bytes:
        """Issue a certificate from CSR using the CA private key (RFC 5280)."""
        sig_alg = sig_alg or self._default_sig_alg

        req = _pem_or_der_to_asn1_csr(csr)
        cri = req["certification_request_info"]

        try:
            _ = x509.load_der_x509_csr(req.dump())
        except Exception as e:
            raise ValueError(f"Invalid CSR: {e}")

        subject_name = cri["subject"]
        spki = cri["subject_pk_info"]

        if ca_cert:
            asn1_ca = asn1_x509.Certificate.load(
                x509.load_pem_x509_certificate(ca_cert).public_bytes(
                    serialization.Encoding.DER
                )
                if b"-----BEGIN" in ca_cert
                else ca_cert
            )
            issuer_name = asn1_ca["tbs_certificate"]["subject"]
            issuer_spki = asn1_ca["tbs_certificate"]["subject_public_key_info"]
        else:
            if not issuer:
                raise ValueError("issuer SubjectSpec or ca_cert required")
            issuer_name = _name_from_subject_spec(issuer)
            issuer_spki = None

        exts = _extensions_from_spec(spki, extensions, issuer_spki=issuer_spki)

        tbs = asn1_x509.TbsCertificate(
            {
                "version": "v3",
                "serial_number": int(serial or int.from_bytes(os.urandom(8), "big")),
                "signature": _sig_alg_identifier(sig_alg),
                "issuer": issuer_name,
                "validity": asn1_x509.Validity(
                    {
                        "not_before": _utc_time(not_before or _now_epoch() - 300),
                        "not_after": _utc_time(
                            not_after or (_now_epoch() + 365 * 24 * 3600)
                        ),
                    }
                ),
                "subject": subject_name,
                "subject_public_key_info": spki,
                "extensions": exts,
            }
        )

        tbs_bytes = tbs.dump()

        with _Pkcs11Session(
            self._module_path,
            token_label=self._token_label,
            slot_id=self._slot_id,
            pin=self._pin,
            user_type=self._user_type,
        ) as sess:
            _, label, key_id = _parse_keyref_pkcs11_attrs(ca_key)
            priv = _find_private_key(sess, label=label, key_id=key_id)
            sig = _sign_with_pkcs11(sess, priv, algorithm=sig_alg, tbs=tbs_bytes)

        cert = asn1_x509.Certificate(
            {
                "tbs_certificate": tbs,
                "signature_algorithm": _sig_alg_identifier(sig_alg),
                "signature_value": sig,
            }
        )

        der = cert.dump()
        return der if output_der else _asn1_to_pem_cert(cert)

    async def verify_cert(
        self,
        cert: bytes,
        *,
        trust_roots: Optional[Sequence[bytes]] = None,
        intermediates: Optional[Sequence[bytes]] = None,
        check_time: Optional[int] = None,
        check_revocation: bool = False,
        opts: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        """Verify a certificate's validity period and signature (RFC 5280)."""
        c = (
            x509.load_pem_x509_certificate(cert)
            if b"-----BEGIN" in cert
            else x509.load_der_x509_certificate(cert)
        )
        now = dt.datetime.fromtimestamp(check_time or _now_epoch(), dt.timezone.utc)
        if c.not_valid_before_utc > now:
            raise ValueError("certificate_not_yet_valid")
        if c.not_valid_after_utc < now:
            raise ValueError("certificate_expired")

        if trust_roots:
            issuer = trust_roots[0]
            ic = (
                x509.load_pem_x509_certificate(issuer)
                if b"-----BEGIN" in issuer
                else x509.load_der_x509_certificate(issuer)
            )
            pub = ic.public_key()
            try:
                if isinstance(pub, rsa.RSAPublicKey):
                    if c.signature_algorithm_oid._name == "rsassaPss":
                        pub.verify(
                            c.signature,
                            c.tbs_certificate_bytes,
                            padding.PSS(
                                mgf=padding.MGF1(c.signature_hash_algorithm),
                                salt_length=padding.PSS.MAX_LENGTH,
                            ),
                            c.signature_hash_algorithm,
                        )
                    else:
                        pub.verify(
                            c.signature,
                            c.tbs_certificate_bytes,
                            padding.PKCS1v15(),
                            c.signature_hash_algorithm,
                        )
                elif isinstance(pub, ec.EllipticCurvePublicKey):
                    pub.verify(
                        c.signature,
                        c.tbs_certificate_bytes,
                        ec.ECDSA(c.signature_hash_algorithm),
                    )
                elif isinstance(pub, ed25519.Ed25519PublicKey):
                    pub.verify(c.signature, c.tbs_certificate_bytes)
                else:
                    pub.verify(c.signature, c.tbs_certificate_bytes)
            except Exception as e:  # pragma: no cover - verify errors
                raise ValueError(f"bad_signature: {e}") from e

        return {"valid": True}

    async def parse_cert(
        self, cert: bytes, *, opts: Optional[Dict[str, object]] = None
    ) -> Dict[str, object]:
        """Parse certificate details into a dictionary (RFC 5280)."""
        c = (
            x509.load_pem_x509_certificate(cert)
            if b"-----BEGIN" in cert
            else x509.load_der_x509_certificate(cert)
        )
        return {
            "subject": c.subject.rfc4514_string(),
            "issuer": c.issuer.rfc4514_string(),
            "serial": c.serial_number,
            "not_before": int(c.not_valid_before_utc.timestamp()),
            "not_after": int(c.not_valid_after_utc.timestamp()),
        }
