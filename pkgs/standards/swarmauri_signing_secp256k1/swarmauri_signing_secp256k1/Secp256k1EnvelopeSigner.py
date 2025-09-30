from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Union

from swarmauri_core.signing.ISigning import ISigning, Signature, Envelope, Canon
from swarmauri_core.crypto.types import KeyRef, Alg

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import (
        load_pem_private_key,
        load_pem_public_key,
    )
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.utils import (
        decode_dss_signature,
        encode_dss_signature,
    )

    _CRYPTO_OK = True
except Exception:  # pragma: no cover
    _CRYPTO_OK = False

try:
    import cbor2  # optional canonicalization

    _CBOR_OK = True
except Exception:  # pragma: no cover
    _CBOR_OK = False


# ───────────────────────── Canonicalization ─────────────────────────


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _canon_cbor(obj: Any) -> bytes:
    if not _CBOR_OK:
        raise RuntimeError("CBOR canonicalization requires 'cbor2' to be installed.")
    return cbor2.dumps(obj)


# ───────────────────────── JWK helpers ─────────────────────────


def _b64u_to_bytes(s: str) -> bytes:
    import base64

    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("ascii"))


def _jwk_thumbprint_sha256_ec(jwk: Mapping[str, Any]) -> str:
    if jwk.get("kty") != "EC":
        raise ValueError("JWK kty must be 'EC' for thumbprint.")
    obj = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
    data = json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


# ───────────────────────── Key loading ─────────────────────────


def _ensure_crypto():
    if not _CRYPTO_OK:
        raise RuntimeError(
            "Secp256k1EnvelopeSigner requires 'cryptography'. Install with: pip install cryptography"
        )


def _curve_from_crv(crv: str):
    c = crv.upper()
    if c in ("SECP256K1", "P-256K", "K-256"):
        return ec.SECP256K1()
    raise ValueError(f"Unsupported curve for this signer: {crv} (expected secp256k1)")


def _load_private_from_pem(
    pem_bytes: bytes, passphrase: Optional[Union[str, bytes]]
) -> ec.EllipticCurvePrivateKey:
    _ensure_crypto()
    pw = None
    if isinstance(passphrase, str):
        pw = passphrase.encode("utf-8")
    elif isinstance(passphrase, (bytes, bytearray)):
        pw = bytes(passphrase)
    key = load_pem_private_key(pem_bytes, password=pw)
    if not isinstance(key, ec.EllipticCurvePrivateKey) or not isinstance(
        key.curve, ec.SECP256K1
    ):
        raise TypeError("PEM private key is not secp256k1.")
    return key


def _load_public_from_pem(pem_bytes: bytes) -> ec.EllipticCurvePublicKey:
    _ensure_crypto()
    pub = load_pem_public_key(pem_bytes)
    if not isinstance(pub, ec.EllipticCurvePublicKey) or not isinstance(
        pub.curve, ec.SECP256K1
    ):
        raise TypeError("PEM public key is not secp256k1.")
    return pub


def _private_from_jwk(jwk: Mapping[str, Any]) -> ec.EllipticCurvePrivateKey:
    _ensure_crypto()
    if jwk.get("kty") != "EC":
        raise ValueError("JWK kty must be 'EC'.")
    curve = _curve_from_crv(jwk["crv"])
    x = int.from_bytes(_b64u_to_bytes(jwk["x"]), "big")
    y = int.from_bytes(_b64u_to_bytes(jwk["y"]), "big")
    d = int.from_bytes(_b64u_to_bytes(jwk["d"]), "big")
    pub_numbers = ec.EllipticCurvePublicNumbers(x=x, y=y, curve=curve)
    priv_numbers = ec.EllipticCurvePrivateNumbers(
        private_value=d, public_numbers=pub_numbers
    )
    return priv_numbers.private_key()


def _public_from_jwk(jwk: Mapping[str, Any]) -> ec.EllipticCurvePublicKey:
    _ensure_crypto()
    if jwk.get("kty") != "EC":
        raise ValueError("JWK kty must be 'EC'.")
    curve = _curve_from_crv(jwk["crv"])
    x = int.from_bytes(_b64u_to_bytes(jwk["x"]), "big")
    y = int.from_bytes(_b64u_to_bytes(jwk["y"]), "big")
    return ec.EllipticCurvePublicNumbers(x=x, y=y, curve=curve).public_key()


def _keyref_to_private(
    key: KeyRef, passphrase: Optional[Union[str, bytes]]
) -> ec.EllipticCurvePrivateKey:
    """
    Accepted KeyRef forms:
      - {"kind":"pem_priv", "data": <bytes|str>}
      - {"kind":"pem_priv_path", "path": <str>}
      - {"kind":"jwk_priv", "jwk": {"kty":"EC","crv":"secp256k1","x","y","d"}}
      - {"kind":"cryptography_obj", "obj": EllipticCurvePrivateKey}
    """
    _ensure_crypto()
    if isinstance(key, dict):
        k = key.get("kind")
        if k == "cryptography_obj" and isinstance(
            key.get("obj"), ec.EllipticCurvePrivateKey
        ):
            sk = key["obj"]  # type: ignore[assignment]
            if not isinstance(sk.curve, ec.SECP256K1):
                raise TypeError("Provided private key is not secp256k1.")
            return sk
        if k == "pem_priv":
            data = key.get("data")
            if isinstance(data, str):
                data = data.encode("utf-8")
            if not isinstance(data, (bytes, bytearray)):
                raise TypeError("pem_priv KeyRef requires 'data' as bytes/str.")
            return _load_private_from_pem(bytes(data), passphrase)
        if k == "pem_priv_path":
            path = key.get("path")
            if not isinstance(path, str):
                raise TypeError("pem_priv_path KeyRef requires 'path' string.")
            with open(path, "rb") as f:
                return _load_private_from_pem(f.read(), passphrase)
        if k == "jwk_priv":
            jwk = key.get("jwk")
            if not isinstance(jwk, Mapping):
                raise TypeError("jwk_priv KeyRef requires 'jwk' mapping.")
            return _private_from_jwk(jwk)
    raise TypeError("Unsupported KeyRef for secp256k1 private key.")


def _keyref_to_public(entry: Any) -> ec.EllipticCurvePublicKey:
    """
    Accepted forms (for opts['pubkeys'] and kid derivation):
      - {"kind":"pem_pub","data":<bytes|str>}
      - {"kind":"pem_pub_path","path":<str>}
      - {"kind":"jwk_pub","jwk": {"kty":"EC","crv":"secp256k1","x","y"}}
      - {"kind":"cryptography_obj","obj": EllipticCurvePublicKey}
      - bytes/str PEM
      - direct JWK mapping (dict with kty='EC', crv='secp256k1', x, y)
    """
    _ensure_crypto()
    if isinstance(entry, dict):
        k = entry.get("kind")
        if k == "cryptography_obj" and isinstance(
            entry.get("obj"), ec.EllipticCurvePublicKey
        ):
            pk = entry["obj"]  # type: ignore[assignment]
            if not isinstance(pk.curve, ec.SECP256K1):
                raise TypeError("Provided public key is not secp256k1.")
            return pk
        if k == "pem_pub":
            data = entry.get("data")
            if isinstance(data, str):
                data = data.encode("utf-8")
            return _load_public_from_pem(bytes(data))
        if k == "pem_pub_path":
            path = entry.get("path")
            with open(path, "rb") as f:
                return _load_public_from_pem(f.read())
        if k == "jwk_pub":
            jwk = entry.get("jwk")
            if not isinstance(jwk, Mapping):
                raise TypeError("jwk_pub requires 'jwk' mapping.")
            return _public_from_jwk(jwk)
        if entry.get("kty") == "EC":
            return _public_from_jwk(entry)
    elif isinstance(entry, ec.EllipticCurvePublicKey):
        if not isinstance(entry.curve, ec.SECP256K1):
            raise TypeError("Provided public key is not secp256k1.")
        return entry
    elif isinstance(entry, (bytes, bytearray, str)):
        data = entry.encode("utf-8") if isinstance(entry, str) else bytes(entry)
        try:
            return _load_public_from_pem(data)
        except Exception as e:  # pragma: no cover
            raise TypeError(
                "bytes/str given is not a valid secp256k1 PEM public key."
            ) from e
    raise TypeError("Unsupported public key format for secp256k1.")


def _kid_from_public(
    pk: ec.EllipticCurvePublicKey, jwk_hint: Optional[Mapping[str, Any]] = None
) -> str:
    try:
        if jwk_hint and jwk_hint.get("kty") == "EC":
            return _jwk_thumbprint_sha256_ec(jwk_hint)
    except Exception:  # pragma: no cover
        pass
    spki = pk.public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return hashlib.sha256(spki).hexdigest()


# ───────────────────────── Signature mapping ─────────────────────────


@dataclass(frozen=True)
class _Sig:
    data: Dict[str, Any]

    def __getitem__(self, k: str) -> object:
        return self.data[k]

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def get(self, k: str, default: Any = None) -> Any:
        return self.data.get(k, default)


# ───────────────────────── Concrete signer ─────────────────────────


class Secp256k1EnvelopeSigner(ISigning):
    """
    ECDSA (secp256k1) detached signer for bytes and canonicalized envelopes.

    Algorithms:
      - ES256K (ECDSA over secp256k1 with SHA-256)
      - 'ECDSA-SHA256' accepted as a synonym

    Private KeyRef accepted:
      - {"kind":"pem_priv","data": <PEM bytes|str>}
      - {"kind":"pem_priv_path","path": <str>}
      - {"kind":"jwk_priv","jwk": {"kty":"EC","crv":"secp256k1","x","y","d"}}
      - {"kind":"cryptography_obj","obj": EllipticCurvePrivateKey}

    Verification keys (opts["pubkeys"]) accepted as:
      - {"kind":"pem_pub","data": <PEM bytes|str>}
      - {"kind":"pem_pub_path","path": <str>}
      - {"kind":"jwk_pub","jwk": {"kty":"EC","crv":"secp256k1","x","y"}}
      - {"kind":"cryptography_obj","obj": EllipticCurvePublicKey}
      - direct PEM (bytes/str)
      - direct JWK mapping (dict with kty='EC', crv='secp256k1', x, y)

    Signature format:
      - DER (ASN.1) by default; include {"fmt":"DER"} in the signature map.
      - JOSE raw r||s: pass opts={"format":"RAW"} to sign/verify.
    """

    def supports(self) -> Mapping[str, Iterable[str]]:
        algs = ("ES256K", "ECDSA-SHA256")
        canons = ("json", "cbor") if _CBOR_OK else ("json",)
        return {
            "algs": algs,
            "canons": canons,
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("mapping",),
            "features": ("multi", "detached_only"),
        }

    # ── bytes ────────────────────────────────────────────────────────────────

    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        _ensure_crypto()
        if alg not in (None, "ES256K", "ECDSA-SHA256"):
            raise ValueError(
                "Unsupported alg for Secp256k1EnvelopeSigner. Use 'ES256K'."
            )
        sk = _keyref_to_private(key, passphrase=(opts or {}).get("passphrase"))
        if not isinstance(sk.curve, ec.SECP256K1):
            raise TypeError("Private key curve must be secp256k1.")
        der_sig = sk.sign(payload, ec.ECDSA(hashes.SHA256()))

        fmt = (opts or {}).get("format", "DER")
        sig_bytes = der_sig
        if isinstance(fmt, str) and fmt.upper() == "RAW":
            r, s = decode_dss_signature(der_sig)
            size_bytes = (sk.curve.key_size + 7) // 8
            sig_bytes = r.to_bytes(size_bytes, "big") + s.to_bytes(size_bytes, "big")

        kid = _kid_from_public(
            sk.public_key(),
            (opts or {}).get("kid_jwk_hint") if isinstance(opts, Mapping) else None,
        )
        return [
            _Sig(
                {
                    "alg": "ES256K",
                    "kid": kid,
                    "sig": sig_bytes,
                    "fmt": "RAW" if fmt == "RAW" else "DER",
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
        _ensure_crypto()
        min_signers = int((require or {}).get("min_signers", 1))
        allowed_algs = set((require or {}).get("algs", ("ES256K", "ECDSA-SHA256")))
        fmt_pref = (opts or {}).get("format", "DER")

        if not (opts and "pubkeys" in opts):
            raise ValueError(
                "verify_bytes requires opts['pubkeys'] with one or more secp256k1 public keys."
            )
        pubs: list[ec.EllipticCurvePublicKey] = []
        for entry in opts["pubkeys"]:  # type: ignore[index]
            pk = _keyref_to_public(entry)
            if not isinstance(pk.curve, ec.SECP256K1):
                raise TypeError("All verification public keys must be secp256k1.")
            pubs.append(pk)

        accepted = 0
        for sig in signatures:
            alg = sig.get("alg")
            if not isinstance(alg, str) or alg not in allowed_algs:
                continue
            sig_bytes = sig.get("sig")
            if not isinstance(sig_bytes, (bytes, bytearray)):
                continue

            any_verified = False
            for pk in pubs:
                try:
                    if (isinstance(fmt_pref, str) and fmt_pref.upper() == "RAW") or (
                        isinstance(sig.get("fmt"), str)
                        and sig.get("fmt").upper() == "RAW"
                    ):
                        size_bytes = (pk.curve.key_size + 7) // 8
                        if len(sig_bytes) != 2 * size_bytes:
                            raise InvalidSignature(
                                "Invalid RAW ECDSA signature length for secp256k1."
                            )
                        r = int.from_bytes(sig_bytes[:size_bytes], "big")
                        s = int.from_bytes(sig_bytes[size_bytes:], "big")
                        der = encode_dss_signature(r, s)
                        pk.verify(der, payload, ec.ECDSA(hashes.SHA256()))
                    else:
                        pk.verify(bytes(sig_bytes), payload, ec.ECDSA(hashes.SHA256()))
                    any_verified = True
                    break
                except InvalidSignature:
                    continue

            if any_verified:
                accepted += 1
                if accepted >= min_signers:
                    return True

        return False

    # ── canonicalization ─────────────────────────────────────────────────────

    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if canon in (None, "json"):
            return _canon_json(env)  # type: ignore[arg-type]
        if canon == "cbor":
            return _canon_cbor(env)  # type: ignore[arg-type]
        raise ValueError(f"Unsupported canon: {canon}")

    # ── envelope ─────────────────────────────────────────────────────────────

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
        return await self.sign_bytes(key, payload, alg="ES256K", opts=opts)

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
