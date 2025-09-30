from __future__ import annotations

import base64
import datetime as dt
import json
from typing import Any, Iterable, Mapping, Optional, Sequence, Union, Literal
from collections.abc import Mapping as _Mapping

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import (
    ed25519,
    ec,
    rsa,
    padding,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Canon, Envelope
from swarmauri_core.signing.types import Signature
from swarmauri_core.crypto.types import Alg, KeyRef


# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _canon_json_like(obj: Any) -> bytes:
    """
    Deterministic JSON canonicalization that handles:
      - dict / list / primitives
      - Pydantic models (via model_dump()/dict())
      - objects with .dict() or .__dict__
      - bytes (as base64url strings)
    """

    def normalize(v: Any) -> Any:
        if v is None or isinstance(v, (str, int, float, bool)):
            return v
        if isinstance(v, (bytes, bytearray)):
            return {"__bytes__": _b64u(bytes(v))}
        if isinstance(v, dict):
            return {k: normalize(v2) for k, v2 in v.items()}
        if isinstance(v, (list, tuple)):
            return [normalize(x) for x in v]
        if hasattr(v, "model_dump"):
            return normalize(v.model_dump())
        if hasattr(v, "dict"):
            try:
                return normalize(v.dict())
            except Exception:
                pass
        if hasattr(v, "__dict__"):
            return normalize(vars(v))
        return str(v)

    return json.dumps(
        normalize(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _load_private_from_keyref(key: KeyRef):
    """
    Accepts KeyRef.material as PEM (PKCS#8 private) or an already-instantiated
    cryptography private key via KeyRef.tags['crypto_obj'].

    Optional: KeyRef.tags['password'] for encrypted PEM (bytes or str).
    """
    if isinstance(key, dict):
        kind = key.get("kind")
        if kind == "cryptography_obj":
            obj = key.get("obj")
            if isinstance(
                obj,
                (
                    ed25519.Ed25519PrivateKey,
                    ec.EllipticCurvePrivateKey,
                    rsa.RSAPrivateKey,
                ),
            ):
                return obj
        if kind == "pem":
            data = key.get("priv") or key.get("data")
            if isinstance(data, str):
                data = data.encode("utf-8")
            if not isinstance(data, (bytes, bytearray)):
                raise TypeError(
                    "CASigner: KeyRef 'pem' expects 'priv' or 'data' bytes/str."
                )
            password = key.get("password")
            if isinstance(password, str):
                password = password.encode("utf-8")
            return serialization.load_pem_private_key(data, password=password)
    if getattr(key, "tags", None):
        obj = key.tags.get("crypto_obj")
        if obj is not None:
            return obj
        pw = key.tags.get("password", None)
        if isinstance(pw, str):
            pw = pw.encode("utf-8")
        password: Optional[bytes] = pw
    else:
        password = None

    material = getattr(key, "material", None)
    if not isinstance(material, (bytes, bytearray)):
        raise ValueError(
            "CASigner: KeyRef.material must contain PEM-encoded private key bytes or tags['crypto_obj']."
        )

    return serialization.load_pem_private_key(bytes(material), password=password)


def _public_of(
    priv,
) -> Union[ed25519.Ed25519PublicKey, ec.EllipticCurvePublicKey, rsa.RSAPublicKey]:
    return priv.public_key()


def _alg_from_key(priv) -> str:
    if isinstance(priv, ed25519.Ed25519PrivateKey):
        return "Ed25519"
    if isinstance(priv, ec.EllipticCurvePrivateKey):
        return (
            "ECDSA-P256-SHA256"
            if isinstance(priv.curve, ec.SECP256R1)
            else f"ECDSA-{priv.curve.name}-SHA256"
        )
    if isinstance(priv, rsa.RSAPrivateKey):
        return "RSA-PSS-SHA256"
    raise ValueError("Unsupported private key type for CASigner")


def _sign_bytes_with(priv, data: bytes, alg: Optional[str]) -> bytes:
    rsa_ok = (None, "RSA-PSS-SHA256", "PS256", "RS256")
    if isinstance(priv, ed25519.Ed25519PrivateKey):
        if alg not in (None, "Ed25519"):
            raise ValueError("CASigner: Ed25519 key supports only alg='Ed25519'")
        return priv.sign(data)
    if isinstance(priv, ec.EllipticCurvePrivateKey):
        if alg is not None and not str(alg).startswith("ECDSA"):
            raise ValueError("CASigner: EC key supports only ECDSA-* algorithms")
        return priv.sign(data, ec.ECDSA(hashes.SHA256()))
    if isinstance(priv, rsa.RSAPrivateKey):
        if alg not in rsa_ok:
            raise ValueError("CASigner: RSA key supports RSA-PSS-SHA256/PS256/RS256")
        return priv.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
    raise ValueError("Unsupported key for signing")


def _verify_bytes_with(pub, data: bytes, sig: bytes, alg: Optional[str]) -> bool:
    try:
        if isinstance(pub, ed25519.Ed25519PublicKey):
            if alg not in (None, "Ed25519"):
                return False
            pub.verify(sig, data)
            return True
        if isinstance(pub, ec.EllipticCurvePublicKey):
            if alg is not None and not str(alg).startswith("ECDSA"):
                return False
            pub.verify(sig, data, ec.ECDSA(hashes.SHA256()))
            return True
        if isinstance(pub, rsa.RSAPublicKey):
            pub.verify(
                sig,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
    except Exception:
        return False
    return False


def _key_id_from_public(pub) -> str:
    spki = pub.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    return _b64u(hashes.Hash(hashes.SHA256()).finalize() if False else spki)


def _name_from_dict(d: Mapping[str, str]) -> x509.Name:
    attrs = []
    if "C" in d:
        attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, d["C"]))
    if "ST" in d:
        attrs.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, d["ST"]))
    if "L" in d:
        attrs.append(x509.NameAttribute(NameOID.LOCALITY_NAME, d["L"]))
    if "O" in d:
        attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, d["O"]))
    if "OU" in d:
        attrs.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, d["OU"]))
    if "CN" in d:
        attrs.append(x509.NameAttribute(NameOID.COMMON_NAME, d["CN"]))
    if "email" in d:
        attrs.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, d["email"]))
    return x509.Name(attrs)


class _Sig(_Mapping):
    def __init__(self, data: Mapping[str, object]):
        self.data = dict(data)

    def __getitem__(self, k: str) -> object:
        return self.data[k]

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def get(self, k: str, default: object | None = None) -> object | None:
        return self.data.get(k, default)


class CASigner(SigningBase):
    """CA-capable detached signer."""

    type: Literal["CASigner"] = "CASigner"

    def supports(self) -> Mapping[str, Iterable[str]]:
        envelopes = ("detached-bytes", "x509-csr", "structured-json")
        return {
            "signs": ("bytes", "envelope"),
            "verifies": ("bytes", "envelope"),
            "envelopes": envelopes,
            "algs": (
                "Ed25519",
                "ECDSA-P256-SHA256",
                "RSA-PSS-SHA256",
                "PS256",
                "RS256",
            ),
            "canons": ("json",),
            "features": ("multi", "detached_only", "x509"),
        }

    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        priv = _load_private_from_keyref(key)
        sig = _sign_bytes_with(priv, payload, str(alg) if alg is not None else None)
        kid = _key_id_from_public(_public_of(priv))
        return [
            _Sig(
                {
                    "alg": str(alg) if alg else _alg_from_key(priv),
                    "kid": kid,
                    "sig": sig,
                    "created_at": int(dt.datetime.utcnow().timestamp()),
                }
            )
        ]

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        pubs: list[
            Union[ed25519.Ed25519PublicKey, ec.EllipticCurvePublicKey, rsa.RSAPublicKey]
        ] = []
        if opts and "pubkeys" in opts:
            for item in opts["pubkeys"]:  # type: ignore[index]
                if isinstance(
                    item,
                    (
                        ed25519.Ed25519PublicKey,
                        ec.EllipticCurvePublicKey,
                        rsa.RSAPublicKey,
                    ),
                ):
                    pubs.append(item)
                elif isinstance(item, (bytes, bytearray)):
                    pk = serialization.load_pem_public_key(bytes(item))
                    pubs.append(pk)  # type: ignore[arg-type]
                else:
                    raise TypeError(
                        "CASigner.verify_bytes: unsupported public key entry in opts['pubkeys']."
                    )

        min_signers = int(require.get("min_signers", 1)) if require else 1

        accepted = 0
        for sig in signatures:
            alg = sig.get("alg") if isinstance(sig, Mapping) else None
            sig_bytes = sig.get("sig") if isinstance(sig, Mapping) else None
            if not isinstance(sig_bytes, (bytes, bytearray)):
                continue
            ok_one = False
            for pk in pubs:
                if _verify_bytes_with(
                    pk, payload, bytes(sig_bytes), str(alg) if alg is not None else None
                ):
                    ok_one = True
                    break
            if ok_one:
                accepted += 1
            if accepted >= min_signers:
                return True
        return False

    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if canon in (None, "json"):
            return _canon_json_like(env)
        raise ValueError(f"Unsupported canon: {canon}")

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.sign_bytes(key, payload, alg=alg, opts=opts)

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.verify_bytes(payload, signatures, require=require, opts=opts)

    def issue_self_signed(
        self,
        ca_key: KeyRef,
        subject: Mapping[str, str],
        *,
        days: int = 3650,
        is_ca: bool = True,
        pathlen: Optional[int] = None,
        eku: Optional[Sequence[x509.ExtendedKeyUsage]] = None,
        san_dns: Optional[Sequence[str]] = None,
        serial_number: Optional[int] = None,
    ) -> bytes:
        priv = _load_private_from_keyref(ca_key)
        pub = _public_of(priv)
        name = _name_from_dict(subject)

        now = dt.datetime.utcnow()
        builder = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(pub)
            .serial_number(serial_number or x509.random_serial_number())
            .not_valid_before(now - dt.timedelta(minutes=5))
            .not_valid_after(now + dt.timedelta(days=days))
        )

        builder = (
            builder.add_extension(
                x509.BasicConstraints(ca=is_ca, path_length=pathlen), critical=True
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(pub), critical=False
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(pub), critical=False
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True if is_ca else False,
                    crl_sign=True if is_ca else False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
        )

        if eku:
            builder = builder.add_extension(x509.ExtendedKeyUsage(eku), critical=False)

        if san_dns:
            builder = builder.add_extension(
                x509.SubjectAlternativeName([x509.DNSName(d) for d in san_dns]),
                critical=False,
            )

        if isinstance(priv, ed25519.Ed25519PrivateKey):
            cert = builder.sign(private_key=priv, algorithm=None)
        elif isinstance(priv, ec.EllipticCurvePrivateKey):
            cert = builder.sign(private_key=priv, algorithm=hashes.SHA256())
        elif isinstance(priv, rsa.RSAPrivateKey):
            cert = builder.sign(private_key=priv, algorithm=hashes.SHA256())
        else:
            raise ValueError("Unsupported key type for self-signed certificate")

        return cert.public_bytes(Encoding.PEM)

    def create_csr(
        self,
        subject: Mapping[str, str],
        key: KeyRef,
        *,
        san_dns: Optional[Sequence[str]] = None,
        is_ca: bool = False,
        eku_server_client: bool = True,
    ) -> bytes:
        priv = _load_private_from_keyref(key)
        name = _name_from_dict(subject)

        csr_builder = x509.CertificateSigningRequestBuilder().subject_name(name)

        san_list = []
        if san_dns:
            san_list.extend(x509.DNSName(d) for d in san_dns)
        if san_list:
            csr_builder = csr_builder.add_extension(
                x509.SubjectAlternativeName(san_list), critical=False
            )

        if is_ca:
            csr_builder = csr_builder.add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True
            )

        if eku_server_client:
            csr_builder = csr_builder.add_extension(
                x509.ExtendedKeyUsage(
                    [ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH]
                ),
                critical=False,
            )

        if isinstance(priv, ed25519.Ed25519PrivateKey):
            csr = csr_builder.sign(priv, algorithm=None)
        elif isinstance(priv, ec.EllipticCurvePrivateKey):
            csr = csr_builder.sign(priv, hashes.SHA256())
        elif isinstance(priv, rsa.RSAPrivateKey):
            csr = csr_builder.sign(priv, hashes.SHA256())
        else:
            raise ValueError("Unsupported key type for CSR")

        return csr.public_bytes(Encoding.PEM)

    def sign_csr(
        self,
        csr_pem: bytes,
        ca_key: KeyRef,
        ca_cert_pem: bytes,
        *,
        days: int = 825,
        is_ca: bool = False,
        pathlen: Optional[int] = None,
        ocsp_url: Optional[str] = None,
        crl_url: Optional[str] = None,
        serial_number: Optional[int] = None,
    ) -> bytes:
        csr = x509.load_pem_x509_csr(csr_pem)
        if not csr.is_signature_valid:
            raise ValueError("Invalid CSR signature")

        ca_priv = _load_private_from_keyref(ca_key)
        ca_cert = x509.load_pem_x509_certificate(ca_cert_pem)
        now = dt.datetime.utcnow()

        builder = (
            x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(ca_cert.subject)
            .public_key(csr.public_key())
            .serial_number(serial_number or x509.random_serial_number())
            .not_valid_before(now - dt.timedelta(minutes=5))
            .not_valid_after(now + dt.timedelta(days=days))
        )

        for ext in csr.extensions:
            builder = builder.add_extension(ext.value, ext.critical)

        builder = builder.add_extension(
            x509.BasicConstraints(ca=is_ca, path_length=pathlen), critical=True
        )

        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(csr.public_key()), critical=False
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_cert.public_key()),
            critical=False,
        )

        builder = builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=not is_ca,
                data_encipherment=False,
                key_agreement=not is_ca,
                key_cert_sign=is_ca,
                crl_sign=is_ca,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )

        if ocsp_url:
            builder = builder.add_extension(
                x509.AuthorityInformationAccess(
                    [
                        x509.AccessDescription(
                            x509.AuthorityInformationAccessOID.OCSP,
                            x509.UniformResourceIdentifier(ocsp_url),
                        )
                    ]
                ),
                critical=False,
            )
        if crl_url:
            builder = builder.add_extension(
                x509.CRLDistributionPoints(
                    [
                        x509.DistributionPoint(
                            full_name=[x509.UniformResourceIdentifier(crl_url)],
                            relative_name=None,
                            reasons=None,
                            crl_issuer=None,
                        )
                    ]
                ),
                critical=False,
            )

        if isinstance(ca_priv, ed25519.Ed25519PrivateKey):
            cert = builder.sign(private_key=ca_priv, algorithm=None)
        elif isinstance(ca_priv, ec.EllipticCurvePrivateKey):
            cert = builder.sign(private_key=ca_priv, algorithm=hashes.SHA256())
        elif isinstance(ca_priv, rsa.RSAPrivateKey):
            cert = builder.sign(private_key=ca_priv, algorithm=hashes.SHA256())
        else:
            raise ValueError("Unsupported CA key type")

        return cert.public_bytes(Encoding.PEM)

    def verify_chain(
        self,
        leaf_pem: bytes,
        chain_pems: Sequence[bytes] = (),
        roots_pems: Sequence[bytes] = (),
        *,
        at_time: Optional[dt.datetime] = None,
        require_ca: bool = False,
    ) -> bool:
        at = at_time or dt.datetime.utcnow()

        def load_all(pems: Sequence[bytes]) -> list[x509.Certificate]:
            return [x509.load_pem_x509_certificate(p) for p in pems]

        leaf = x509.load_pem_x509_certificate(leaf_pem)
        chain = load_all(chain_pems)
        roots = load_all(roots_pems)

        def valid_at(cert: x509.Certificate) -> bool:
            return cert.not_valid_before <= at <= cert.not_valid_after

        if not valid_at(leaf):
            return False
        for c in chain:
            if not valid_at(c):
                return False
        for r in roots:
            if not valid_at(r):
                return False

        path = [leaf] + list(chain)

        def verify_sig(child: x509.Certificate, issuer: x509.Certificate) -> bool:
            pub = issuer.public_key()
            try:
                if isinstance(pub, rsa.RSAPublicKey):
                    pub.verify(
                        child.signature,
                        child.tbs_certificate_bytes,
                        padding.PKCS1v15(),
                        child.signature_hash_algorithm,
                    )
                elif isinstance(pub, ec.EllipticCurvePublicKey):
                    pub.verify(
                        child.signature,
                        child.tbs_certificate_bytes,
                        ec.ECDSA(child.signature_hash_algorithm),
                    )
                elif isinstance(pub, ed25519.Ed25519PublicKey):
                    pub.verify(child.signature, child.tbs_certificate_bytes)
                else:
                    return False
                return True
            except Exception:
                return False
            except Exception:
                return False

        issuer_matched_root = None
        for idx in range(len(path)):
            child = path[idx]
            issuer = None
            if idx + 1 < len(path):
                issuer = path[idx + 1]
                if child.issuer != issuer.subject or not verify_sig(child, issuer):
                    return False
            else:
                for r in roots:
                    if child.issuer == r.subject and verify_sig(child, r):
                        issuer = r
                        issuer_matched_root = r
                        break
                if issuer is None:
                    return False

        if require_ca and issuer_matched_root:
            try:
                bc = issuer_matched_root.extensions.get_extension_for_class(
                    x509.BasicConstraints
                ).value
                if not bc.ca:
                    return False
            except Exception:
                return False

        return True
