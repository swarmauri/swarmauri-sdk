from __future__ import annotations

import datetime
import ipaddress
import time
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID, ObjectIdentifier
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.certs.ICertService import (
    AltNameSpec,
    BasicConstraintsSpec,
    CertBytes,
    CertExtensionSpec,
    CsrBytes,
    ExtendedKeyUsageSpec,
    KeyUsageSpec,
    NameConstraintsSpec,
    SubjectSpec,
)
from swarmauri_core.crypto.types import KeyRef

# helpers: names & algorithms


def _to_x509_name(subject: SubjectSpec) -> x509.Name:
    rdns = []
    if "C" in subject:
        rdns.append(x509.NameAttribute(NameOID.COUNTRY_NAME, subject["C"]))
    if "ST" in subject:
        rdns.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject["ST"]))
    if "L" in subject:
        rdns.append(x509.NameAttribute(NameOID.LOCALITY_NAME, subject["L"]))
    if "O" in subject:
        rdns.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject["O"]))
    if "OU" in subject:
        rdns.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, subject["OU"]))
    if "CN" in subject:
        rdns.append(x509.NameAttribute(NameOID.COMMON_NAME, subject["CN"]))
    if "emailAddress" in subject:
        rdns.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, subject["emailAddress"]))
    for k, v in subject.get("extra_rdns", {}).items():
        try:
            oid = ObjectIdentifier(k) if k[0].isdigit() else getattr(NameOID, k)
        except Exception:
            oid = ObjectIdentifier(k)
        rdns.append(x509.NameAttribute(oid, v))
    return x509.Name(rdns)


def _now_bounds(nbf: Optional[int], naf: Optional[int]) -> Tuple[int, int]:
    now = int(time.time())
    if nbf is None:
        nbf = now - 300
    if naf is None:
        naf = now + 365 * 24 * 3600
    return int(nbf), int(naf)


@dataclass(frozen=True)
class _SigPlan:
    alg_token: str
    hash_alg: Optional[hashes.HashAlgorithm]
    rsa_pss: bool
    ec_curve: Optional[Any]


def _plan_from_inputs(key_ref: KeyRef, sig_alg: Optional[str]) -> _SigPlan:
    tok = (
        sig_alg or str(key_ref.tags.get("sig_alg") or key_ref.tags.get("alg") or "")
    ).upper()
    if tok in ("ED25519",):
        return _SigPlan("Ed25519", None, False, None)
    if tok in ("RSA-PSS-SHA256", "RSAPSSSHA256", "PS256", "RSASSA-PSS-SHA256"):
        return _SigPlan("RSA-PSS-SHA256", hashes.SHA256(), True, None)
    if tok in ("ECDSA-P256-SHA256", "ES256", "ECDSA-P256", "ECDSA_SHA256"):
        return _SigPlan("ECDSA-P256-SHA256", hashes.SHA256(), False, ec.SECP256R1())
    if key_ref.material:
        sk = serialization.load_pem_private_key(key_ref.material, password=None)
        if isinstance(sk, ed25519.Ed25519PrivateKey):
            return _SigPlan("Ed25519", None, False, None)
        if isinstance(sk, rsa.RSAPrivateKey):
            return _SigPlan("RSA-PSS-SHA256", hashes.SHA256(), True, None)
        if isinstance(sk, ec.EllipticCurvePrivateKey):
            curve = sk.curve
            if isinstance(curve, ec.SECP256R1):
                return _SigPlan(
                    "ECDSA-P256-SHA256", hashes.SHA256(), False, ec.SECP256R1()
                )
    return _SigPlan("Ed25519", None, False, None)


def _apply_extensions(
    builder: x509.CertificateBuilder,
    ext: Optional[CertExtensionSpec],
    subject_pub: x509.PublicKeyTypes,
    issuer_cert: Optional[x509.Certificate],
) -> x509.CertificateBuilder:
    ext = ext or {}

    bc: Optional[BasicConstraintsSpec] = ext.get("basic_constraints")
    if bc is not None:
        builder = builder.add_extension(
            x509.BasicConstraints(
                ca=bool(bc.get("ca", False)), path_length=bc.get("path_len")
            ),
            critical=True,
        )

    ku: Optional[KeyUsageSpec] = ext.get("key_usage")
    if ku is not None:
        builder = builder.add_extension(
            x509.KeyUsage(
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
            critical=True,
        )

    eku: Optional[ExtendedKeyUsageSpec] = ext.get("extended_key_usage")
    if eku and eku.get("oids"):
        oids = []
        for oid_s in eku["oids"]:
            if oid_s == "serverAuth":
                oids.append(ExtendedKeyUsageOID.SERVER_AUTH)
            elif oid_s == "clientAuth":
                oids.append(ExtendedKeyUsageOID.CLIENT_AUTH)
            elif oid_s == "codeSigning":
                oids.append(ExtendedKeyUsageOID.CODE_SIGNING)
            elif oid_s == "emailProtection":
                oids.append(ExtendedKeyUsageOID.EMAIL_PROTECTION)
            elif oid_s == "timeStamping":
                oids.append(ExtendedKeyUsageOID.TIME_STAMPING)
            else:
                oids.append(ObjectIdentifier(oid_s))
        builder = builder.add_extension(x509.ExtendedKeyUsage(oids), critical=False)

    nc: Optional[NameConstraintsSpec] = ext.get("name_constraints")
    if nc:

        def _gns(kind_list: Optional[Sequence[str]], ctor):
            return [ctor(x) for x in (kind_list or [])]

        permitted = (
            _gns(nc.get("permitted_dns"), x509.DNSName)
            + _gns(
                nc.get("permitted_ip"),
                lambda s: x509.IPAddress(ipaddress.ip_network(s, strict=False)),
            )
            + _gns(nc.get("permitted_uri"), x509.UniformResourceIdentifier)
            + _gns(nc.get("permitted_email"), x509.RFC822Name)
        )
        excluded = (
            _gns(nc.get("excluded_dns"), x509.DNSName)
            + _gns(
                nc.get("excluded_ip"),
                lambda s: x509.IPAddress(ipaddress.ip_network(s, strict=False)),
            )
            + _gns(nc.get("excluded_uri"), x509.UniformResourceIdentifier)
            + _gns(nc.get("excluded_email"), x509.RFC822Name)
        )
        builder = builder.add_extension(
            x509.NameConstraints(
                permitted_subtrees=permitted or None, excluded_subtrees=excluded or None
            ),
            critical=True,
        )

    if ext.get("subject_key_identifier", True):
        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(subject_pub), critical=False
        )
    if (
        ext.get("authority_key_identifier", bool(issuer_cert is not None))
        and issuer_cert is not None
    ):
        builder = builder.add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(
                issuer_cert.public_key()
            ),
            critical=False,
        )

    return builder


def _load_priv(material: bytes):
    return serialization.load_pem_private_key(material, password=None)


def _sign(
    builder: Union[x509.CertificateSigningRequestBuilder, x509.CertificateBuilder],
    plan: _SigPlan,
    sk_obj,
):
    if isinstance(sk_obj, ed25519.Ed25519PrivateKey):
        return builder.sign(sk_obj, algorithm=None)
    if isinstance(sk_obj, rsa.RSAPrivateKey):
        if plan.rsa_pss:
            if isinstance(builder, x509.CertificateSigningRequestBuilder):
                return builder.sign(sk_obj, plan.hash_alg)
            return builder.sign(sk_obj, plan.hash_alg)
        return builder.sign(sk_obj, plan.hash_alg)
    if isinstance(sk_obj, ec.EllipticCurvePrivateKey):
        return builder.sign(sk_obj, plan.hash_alg)
    raise ValueError("Unsupported private key type for signing")


def _pub_from_keyref(key: KeyRef):
    if key.public:
        return serialization.load_pem_public_key(
            key.public
            if isinstance(key.public, (bytes, bytearray))
            else key.public.encode("utf-8")
        )
    if key.material:
        return serialization.load_pem_private_key(
            key.material, password=None
        ).public_key()
    raise ValueError("KeyRef must carry .public or .material")


def _pem_or_der(obj, output_der: bool) -> bytes:
    if isinstance(obj, x509.CertificateSigningRequest):
        if output_der:
            return obj.public_bytes(serialization.Encoding.DER)
        return obj.public_bytes(serialization.Encoding.PEM)
    if isinstance(obj, x509.Certificate):
        if output_der:
            return obj.public_bytes(serialization.Encoding.DER)
        return obj.public_bytes(serialization.Encoding.PEM)
    raise TypeError("Unsupported serialization type")


def _mk_san(san: Optional[AltNameSpec]) -> Optional[x509.SubjectAlternativeName]:
    if not san:
        return None
    gns = []
    for d in san.get("dns", []) or []:
        gns.append(x509.DNSName(d))
    for s in san.get("email", []) or []:
        gns.append(x509.RFC822Name(s))
    for u in san.get("uri", []) or []:
        gns.append(x509.UniformResourceIdentifier(u))
    for ip in san.get("ip", []) or []:
        gns.append(x509.IPAddress(ipaddress.ip_address(ip)))
    return x509.SubjectAlternativeName(gns) if gns else None


@ComponentBase.register_type(CertServiceBase, "X509CertService")
class X509CertService(CertServiceBase):
    """CSR/X.509 issuance & verification using ``cryptography``"""

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "key_algs": ("Ed25519", "RSA-2048", "RSA-3072", "EC-P256"),
            "sig_algs": ("Ed25519", "RSA-PSS-SHA256", "ECDSA-P256-SHA256"),
            "features": (
                "csr",
                "self_signed",
                "sign_from_csr",
                "verify",
                "parse",
                "san",
                "eku",
                "key_usage",
                "akid",
                "skid",
            ),
            "profiles": (
                "server",
                "client",
                "code_signing",
                "email_protection",
            ),
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
            raise ValueError("create_csr requires KeyRef.material")
        sk = _load_priv(key.material)
        plan = _plan_from_inputs(key, sig_alg)

        builder = x509.CertificateSigningRequestBuilder().subject_name(
            _to_x509_name(subject)
        )

        san_ext = _mk_san(san)
        if san_ext:
            builder = builder.add_extension(san_ext, critical=False)

        if challenge_password:
            builder = builder.add_attribute(
                x509.oid.AttributeOID.CHALLENGE_PASSWORD,
                challenge_password.encode("utf-8"),
            )

        csr = _sign(builder, plan, sk)
        return _pem_or_der(csr, output_der)

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
        if not key.material:
            raise ValueError("create_self_signed requires KeyRef.material")
        sk = _load_priv(key.material)
        pub = sk.public_key()
        plan = _plan_from_inputs(key, sig_alg)
        nbf, naf = _now_bounds(not_before, not_after)

        builder = (
            x509.CertificateBuilder()
            .subject_name(_to_x509_name(subject))
            .issuer_name(_to_x509_name(subject))
            .public_key(pub)
            .serial_number(serial or x509.random_serial_number())
            .not_valid_before(datetime.datetime.fromtimestamp(nbf, datetime.UTC))
            .not_valid_after(datetime.datetime.fromtimestamp(naf, datetime.UTC))
        )

        if extensions is None:
            extensions = {
                "basic_constraints": {"ca": False},
                "subject_key_identifier": True,
                "authority_key_identifier": False,
            }

        builder = _apply_extensions(builder, extensions, pub, issuer_cert=None)
        cert = _sign(builder, plan, sk)
        return _pem_or_der(cert, output_der)

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
        if not ca_key.material:
            raise ValueError("sign_cert requires CA KeyRef.material")

        try:
            try:
                _csr = x509.load_pem_x509_csr(csr)
            except ValueError:
                _csr = x509.load_der_x509_csr(csr)
        except Exception as e:  # pragma: no cover
            raise ValueError(f"Invalid CSR: {e}") from e

        if not _csr.is_signature_valid:
            raise ValueError("CSR signature invalid")

        issuer_cert_obj: Optional[x509.Certificate] = None
        if ca_cert:
            try:
                try:
                    issuer_cert_obj = x509.load_pem_x509_certificate(ca_cert)
                except ValueError:
                    issuer_cert_obj = x509.load_der_x509_certificate(ca_cert)
            except Exception as e:  # pragma: no cover
                raise ValueError(f"Invalid ca_cert: {e}") from e

        issuer_name = (
            _to_x509_name(issuer)
            if issuer
            else (issuer_cert_obj.subject if issuer_cert_obj else _csr.subject)
        )

        sk = _load_priv(ca_key.material)
        plan = _plan_from_inputs(ca_key, sig_alg)
        nbf, naf = _now_bounds(not_before, not_after)

        builder = (
            x509.CertificateBuilder()
            .subject_name(_csr.subject)
            .issuer_name(issuer_name)
            .public_key(_csr.public_key())
            .serial_number(serial or x509.random_serial_number())
            .not_valid_before(datetime.datetime.fromtimestamp(nbf, datetime.UTC))
            .not_valid_after(datetime.datetime.fromtimestamp(naf, datetime.UTC))
        )

        try:
            san_req = _csr.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            )
            builder = builder.add_extension(san_req.value, critical=False)
        except x509.ExtensionNotFound:
            pass

        if extensions is None:
            extensions = {
                "basic_constraints": {"ca": False},
                "subject_key_identifier": True,
                "authority_key_identifier": True,
            }
        builder = _apply_extensions(
            builder, extensions, _csr.public_key(), issuer_cert=issuer_cert_obj
        )

        cert = _sign(builder, plan, sk)
        return _pem_or_der(cert, output_der)

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
        try:
            try:
                leaf = x509.load_pem_x509_certificate(cert)
            except ValueError:
                leaf = x509.load_der_x509_certificate(cert)
        except Exception as e:  # pragma: no cover
            raise ValueError(f"Invalid certificate: {e}") from e

        now = int(time.time()) if check_time is None else int(check_time)
        if now < int(leaf.not_valid_before_utc.timestamp()):
            return {"valid": False, "reason": "not_yet_valid"}
        if now > int(leaf.not_valid_after_utc.timestamp()):
            return {"valid": False, "reason": "expired"}

        if not trust_roots:
            try:
                leaf.public_key().verify(
                    leaf.signature,
                    leaf.tbs_certificate_bytes,
                    padding.PKCS1v15()
                    if isinstance(leaf.public_key(), rsa.RSAPublicKey)
                    else ec.ECDSA(leaf.signature_hash_algorithm)
                    if isinstance(leaf.public_key(), ec.EllipticCurvePublicKey)
                    else None,
                    leaf.signature_hash_algorithm
                    if not isinstance(leaf.public_key(), ed25519.Ed25519PublicKey)
                    else None,
                )
                return {
                    "valid": True,
                    "reason": None,
                    "chain_len": 1,
                    "is_ca": _is_ca(leaf),
                    "issuer": _name_to_str(leaf.issuer),
                    "subject": _name_to_str(leaf.subject),
                    "not_before": int(leaf.not_valid_before_utc.timestamp()),
                    "not_after": int(leaf.not_valid_after_utc.timestamp()),
                }
            except Exception:
                return {"valid": False, "reason": "untrusted_without_roots"}

        chain_pool: Dict[str, x509.Certificate] = {}
        for pem in intermediates or []:
            c = _load_cert_any(pem)
            chain_pool[_name_to_str(c.subject)] = c
        roots = [_load_cert_any(b) for b in (trust_roots or [])]

        cur = leaf
        length = 1
        while True:
            issuer_dn = _name_to_str(cur.issuer)
            subj_dn = _name_to_str(cur.subject)
            maybe_root = next(
                (r for r in roots if _name_to_str(r.subject) == issuer_dn), None
            )
            if maybe_root:
                _verify_signed_by(cur, maybe_root)
                _verify_self_signed(maybe_root)
                length += 1 if subj_dn != issuer_dn else 0
                return {
                    "valid": True,
                    "reason": None,
                    "chain_len": length,
                    "is_ca": _is_ca(leaf),
                    "issuer": _name_to_str(leaf.issuer),
                    "subject": _name_to_str(leaf.subject),
                    "not_before": int(leaf.not_valid_before_utc.timestamp()),
                    "not_after": int(leaf.not_valid_after_utc.timestamp()),
                    "revocation_checked": False if not check_revocation else False,
                }
            inter = chain_pool.get(issuer_dn)
            if not inter:
                return {"valid": False, "reason": "incomplete_chain"}
            _verify_signed_by(cur, inter)
            cur = inter
            length += 1

    async def parse_cert(
        self,
        cert: CertBytes,
        *,
        include_extensions: bool = True,
        opts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        c = _load_cert_any(cert)
        out: Dict[str, Any] = {
            "tbs_version": c.version.value,
            "serial": int(c.serial_number),
            "sig_alg": str(c.signature_hash_algorithm.name)
            if c.signature_hash_algorithm
            else "ed25519",
            "issuer": _name_to_mapping(c.issuer),
            "subject": _name_to_mapping(c.subject),
            "not_before": int(c.not_valid_before_utc.timestamp()),
            "not_after": int(c.not_valid_after_utc.timestamp()),
            "is_ca": _is_ca(c),
        }
        if include_extensions:
            try:
                skid = c.extensions.get_extension_for_class(
                    x509.SubjectKeyIdentifier
                ).value.digest
                out["skid"] = skid.hex(":")
            except x509.ExtensionNotFound:
                pass
            try:
                akid = c.extensions.get_extension_for_class(
                    x509.AuthorityKeyIdentifier
                ).value.key_identifier
                if akid:
                    out["akid"] = akid.hex(":")
            except x509.ExtensionNotFound:
                pass
            try:
                san = c.extensions.get_extension_for_class(
                    x509.SubjectAlternativeName
                ).value
                out["san"] = {
                    "dns": [x.value for x in san.get_values_for_type(x509.DNSName)],
                    "ip": [str(x) for x in san.get_values_for_type(x509.IPAddress)],
                    "uri": [
                        x.value
                        for x in san.get_values_for_type(x509.UniformResourceIdentifier)
                    ],
                    "email": [
                        x.value for x in san.get_values_for_type(x509.RFC822Name)
                    ],
                }
            except x509.ExtensionNotFound:
                pass
            try:
                eku = c.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
                out["eku"] = [str(oid.dotted_string) for oid in eku]
            except x509.ExtensionNotFound:
                pass
            try:
                ku = c.extensions.get_extension_for_class(x509.KeyUsage).value
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
            except x509.ExtensionNotFound:
                pass
        return out


def _load_cert_any(b: bytes) -> x509.Certificate:
    try:
        return x509.load_pem_x509_certificate(b)
    except ValueError:
        return x509.load_der_x509_certificate(b)


def _name_to_str(n: x509.Name) -> str:
    return ", ".join([f"{attr.oid.dotted_string}={attr.value}" for attr in n])


def _name_to_mapping(n: x509.Name) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for a in n:
        k = {
            NameOID.COUNTRY_NAME: "C",
            NameOID.STATE_OR_PROVINCE_NAME: "ST",
            NameOID.LOCALITY_NAME: "L",
            NameOID.ORGANIZATION_NAME: "O",
            NameOID.ORGANIZATIONAL_UNIT_NAME: "OU",
            NameOID.COMMON_NAME: "CN",
            NameOID.EMAIL_ADDRESS: "emailAddress",
        }.get(a.oid, a.oid.dotted_string)
        out[k] = a.value
    return out


def _is_ca(cert: x509.Certificate) -> bool:
    try:
        bc = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
        return bool(bc.ca)
    except x509.ExtensionNotFound:
        return False


def _verify_self_signed(cert: x509.Certificate) -> None:
    _verify_signed_by(cert, cert)


def _verify_signed_by(child: x509.Certificate, issuer: x509.Certificate) -> None:
    pk = issuer.public_key()
    if isinstance(pk, rsa.RSAPublicKey):
        pk.verify(
            child.signature,
            child.tbs_certificate_bytes,
            padding.PKCS1v15(),
            child.signature_hash_algorithm,
        )
        return
    if isinstance(pk, ec.EllipticCurvePublicKey):
        pk.verify(
            child.signature,
            child.tbs_certificate_bytes,
            ec.ECDSA(child.signature_hash_algorithm),
        )
        return
    if isinstance(pk, ed25519.Ed25519PublicKey):
        pk.verify(child.signature, child.tbs_certificate_bytes)
        return
    raise ValueError("Unsupported issuer public key type for verification")
