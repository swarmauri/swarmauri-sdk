from __future__ import annotations

import base64
import hashlib
import json
import typing as t
from dataclasses import dataclass

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519

from swarmauri_core.crypto.types import JWAAlg, KeyRef


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _sha256_b64url(data: bytes) -> str:
    return _b64url(hashlib.sha256(data).digest())


def _b64url_dec(data: str) -> bytes:
    pad = "=" * ((4 - (len(data) % 4)) % 4)
    return base64.urlsafe_b64decode(data + pad)


def _json_c14n(obj: t.Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _jwk_thumbprint_b64url(jwk: dict) -> str:
    """Compute the RFC 7638 JWK thumbprint."""

    kty = jwk["kty"]
    if kty == "RSA":
        ordered = {"e": jwk["e"], "kty": "RSA", "n": jwk["n"]}
    elif kty == "EC":
        ordered = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
    elif kty == "OKP":
        ordered = {"crv": jwk["crv"], "kty": "OKP", "x": jwk["x"]}
    else:
        raise ValueError(f"Unsupported kty for thumbprint: {kty}")
    return _sha256_b64url(_json_c14n(ordered))


def _ath_from_access_token(tok: str) -> str:
    """Generate the DPoP access token hash ("ath" claim)."""

    if tok.startswith("Bearer "):
        tok = tok[7:]
    return _sha256_b64url(tok.encode("ascii"))


@dataclass
class _KeyMat:
    keyref: t.Mapping[str, t.Any]
    pub_jwk: dict
    alg: JWAAlg


def _derive_public_jwk_from_priv_pem(pem_bytes: bytes) -> dict:
    key = load_pem_private_key(pem_bytes, password=None)
    pub = key.public_key()
    if isinstance(pub, rsa.RSAPublicKey):
        nums = pub.public_numbers()
        n = nums.n.to_bytes((nums.n.bit_length() + 7) // 8, "big")
        e = nums.e.to_bytes((nums.e.bit_length() + 7) // 8, "big")
        return {"kty": "RSA", "n": _b64url(n), "e": _b64url(e)}
    if isinstance(pub, ec.EllipticCurvePublicKey):
        nums = pub.public_numbers()
        if isinstance(pub.curve, ec.SECP256R1):
            x = nums.x.to_bytes(32, "big")
            y = nums.y.to_bytes(32, "big")
            return {"kty": "EC", "crv": "P-256", "x": _b64url(x), "y": _b64url(y)}
        raise ValueError("Unsupported EC curve for JWK export")
    if isinstance(pub, ed25519.Ed25519PublicKey):
        raw = pub.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        return {"kty": "OKP", "crv": "Ed25519", "x": _b64url(raw)}
    raise ValueError("Unsupported key type for JWK export")


def _resolve_keyref(key: KeyRef, alg: t.Optional[str]) -> _KeyMat:
    if not isinstance(key, dict):
        raise TypeError("DPoP KeyRef must be a dict")
    kind = key.get("kind")
    alg_token = JWAAlg(alg or key.get("alg") or "ES256")
    if kind == "pem":
        priv = key.get("priv")
        if isinstance(priv, str):
            priv = priv.encode("utf-8")
        if not isinstance(priv, (bytes, bytearray)):
            raise TypeError("KeyRef['priv'] must be PEM bytes|str for kind='pem'")
        priv_bytes = bytes(priv)
        pub_jwk = _derive_public_jwk_from_priv_pem(priv_bytes)
        if alg_token == JWAAlg.EDDSA:
            sk = load_pem_private_key(priv_bytes, password=None)
            if not isinstance(sk, ed25519.Ed25519PrivateKey):
                raise TypeError("PEM is not an Ed25519 private key")
            keyref = {"kind": "cryptography_obj", "obj": sk}
        else:
            keyref = {"kind": "pem", "priv": priv_bytes}
        return _KeyMat(keyref=keyref, pub_jwk=pub_jwk, alg=alg_token)
    if kind == "jwk":
        priv_jwk = key.get("priv")
        if not isinstance(priv_jwk, dict):
            raise TypeError("KeyRef['priv'] must be a private JWK dict for kind='jwk'")
        alg_token = JWAAlg(alg or priv_jwk.get("alg") or "ES256")
        pub_jwk = {
            k: v for k, v in priv_jwk.items() if k in ("kty", "crv", "x", "y", "n", "e")
        }
        if alg_token == JWAAlg.EDDSA and priv_jwk.get("kty") == "OKP":
            d = priv_jwk.get("d")
            if not isinstance(d, str):
                raise TypeError("Ed25519 JWK requires 'd'")
            keyref = {"kind": "raw_ed25519_sk", "bytes": _b64url_dec(d)}
        else:
            keyref = {"kind": "jwk", "priv": priv_jwk}
        return _KeyMat(keyref=keyref, pub_jwk=pub_jwk, alg=alg_token)
    raise TypeError(f"Unsupported KeyRef.kind: {kind}")


__all__ = [
    "_ath_from_access_token",
    "_b64url",
    "_b64url_dec",
    "_jwk_thumbprint_b64url",
    "_json_c14n",
    "_resolve_keyref",
    "_KeyMat",
]
