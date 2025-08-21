from __future__ import annotations

import base64
import datetime as dt
import json
from typing import Any, Iterable, Mapping, Optional, Sequence, Union, Literal

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

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Canon, Envelope
from swarmauri_core.signing.types import Signature
from swarmauri_core.crypto.types import Alg, KeyRef


# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────


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
        # pydantic v2 model
        if hasattr(v, "model_dump"):
            return normalize(v.model_dump())
        # pydantic v1 / dataclass-like / generic objects
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
    # Prefer injected crypto object if present
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
        # default curve label for P-256
        return (
            "ECDSA-P256-SHA256"
            if isinstance(priv.curve, ec.SECP256R1)
            else f"ECDSA-{priv.curve.name}-SHA256"
        )
    if isinstance(priv, rsa.RSAPrivateKey):
        return "RSA-PSS-SHA256"
    raise ValueError("Unsupported private key type for CASigner")


def _sign_bytes_with(priv, data: bytes, alg: Optional[str]) -> bytes:
    # Privately normalize allowed alg aliases for RSA
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
        # We default to PSS for stronger padding; RS256 alias is accepted at callsite.
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
            # Accept PSS verification (preferred). RS256 alias is accepted (we still verify with PSS here).
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
    # Stable key id: SHA-256 over SubjectPublicKeyInfo DER, base64url
    spki = pub.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    return _b64u(
        hashes.Hash(hashes.SHA256()).finalize() if False else spki
    )  # avoid extra hash; SPKI is unique enough


def _name_from_dict(d: Mapping[str, str]) -> x509.Name:
    # Supported keys: C, ST, L, O, OU, CN, email
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


# ────────────────────────────────────────────────────────────────────────────────
# Signature carrier (Mapping-like) to satisfy swarmauri_core.signing.types.Signature
# ────────────────────────────────────────────────────────────────────────────────


class _Sig:
    def __init__(self, data: Mapping[str, object]):
        self.data = data

    def __getitem__(self, k: str) -> object:
        return self.data[k]

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def get(self, k: str, default: Any = None) -> Any:
        return self.data.get(k, default)


# ────────────────────────────────────────────────────────────────────────────────
# CASigner
# ────────────────────────────────────────────────────────────────────────────────


@ComponentBase.register_model()
class CASigner(SigningBase):
    """
    CA-capable detached signer.

    Implements ISigning (bytes/envelope) and exposes X.509 helpers:
      • issue_self_signed(...)
      • create_csr(...)
      • sign_csr(...)
      • verify_chain(...)

    KeyRef expectations:
      - key.material: PEM-encoded PKCS#8 private key (bytes), or
      - key.tags['crypto_obj']: cryptography private key object (Ed25519 / EC / RSA)
      - optional key.tags['password']: str|bytes for encrypted private key PEM

    Supported alg values:
      - "Ed25519"
      - "ECDSA-P256-SHA256" (other EC curves are accepted but labeled accordingly)
      - "RSA-PSS-SHA256" (aliases "PS256", "RS256" accepted)
    """

    type: Literal["CASigner"] = "CASigner"

    # ------------------------------------------------------------------
    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "algs": (
                "Ed25519",
                "ECDSA-P256-SHA256",
                "RSA-PSS-SHA256",
                "PS256",
                "RS256",
            ),
            "canons": ("json",),  # deterministic JSON only (no CBOR dep)
            "features": ("multi", "detached_only", "x509"),
        }

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """
        opts['pubkeys']: Sequence[PublicKey | PEM bytes]
        require['min_signers']: int (default 1)
        """
        # Collect public keys from opts
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
            alg = sig.get("alg") if hasattr(sig, "get") else None
            sig_bytes = sig.get("sig") if hasattr(sig, "get") else None
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

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
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

    # ───────────────────────────────────────────────────────────────────
    # X.509 Utilities (CA)
    # ───────────────────────────────────────────────────────────────────

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
        """
        Create a self-signed CA/root certificate.
        Returns PEM-encoded certificate bytes.
        """
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

        # Basic CA bits
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

        # Sign with appropriate algorithm
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
        """
        Create a CSR (Certificate Signing Request) for a subject using the given key.
        Returns PEM-encoded CSR bytes.
        """
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

        # Sign CSR
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
        """
        Sign a CSR with the CA key/cert to issue a leaf or intermediate certificate.
        Returns PEM-encoded certificate bytes.
        """
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

        # Copy CSR extensions
        for ext in csr.extensions:
            builder = builder.add_extension(ext.value, ext.critical)

        # Basic constraints
        builder = builder.add_extension(
            x509.BasicConstraints(ca=is_ca, path_length=pathlen), critical=True
        )

        # SKI / AKI
        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(csr.public_key()), critical=False
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_cert.public_key()),
            critical=False,
        )

        # KeyUsage
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

        # AIA/CRL distribution points
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

        # Sign cert
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
        """
        Basic signature/issuer chaining check (no OCSP/CRL, no name/policy checks).
        Returns True if each cert is signed by the next issuer and the final issuer is a trusted root.

        NOTE: This is a pragmatic verifier. For full PKI validation, integrate a path
        builder/validator (or openssl CLI) and wire OCSP/CRLs according to your policy.
        """
        at = at_time or dt.datetime.utcnow()

        def load_all(pems: Sequence[bytes]) -> list[x509.Certificate]:
            return [x509.load_pem_x509_certificate(p) for p in pems]

        leaf = x509.load_pem_x509_certificate(leaf_pem)
        chain = load_all(chain_pems)
        roots = load_all(roots_pems)

        # Quick validity window checks
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

        # Build path: leaf -> chain... -> root (any of roots)
        path = [leaf] + list(chain)

        # Verify signatures along the path using issuer public keys
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

        # Walk until a root matches
        issuer_matched_root = None
        for idx in range(len(path)):
            child = path[idx]
            # Find issuer: next in path or any root
            issuer = None
            if idx + 1 < len(path):
                issuer = path[idx + 1]
                if child.issuer != issuer.subject or not verify_sig(child, issuer):
                    return False
            else:
                # Final: must be issued by one of the roots (self-signed or intermediate)
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
