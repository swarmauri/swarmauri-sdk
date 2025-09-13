"""
DPoP Signer / Verifier
----------------------

Implements RFC 9449 (DPoP) proof *signing* (client side) and *verification*
(server side). Designed to plug into the same SigningBase/ISigning surface used
by other signers (detached signatures), but note that DPoP is a *proof of
possession* over request metadata (method+URL [+ token hash]), not a content
signature. We therefore treat the "payload" as contextual and drive semantics
via opts/require.

Key points:
- sign_bytes(): creates a 'dpop+jwt' proof with header {alg, typ, jwk}.
- verify_bytes(): validates signature (using embedded JWK), claims, iat skew,
  jti replay window, method/url binding, and (optional) 'ath' against a bearer
  access token.
- supports 'ES256', 'RS256', 'EdDSA' for practicality; extend as needed.

KeyRef support:
- {"kind": "pem", "priv": <PEM bytes|str>} — loads private key; derives JWK.
- {"kind": "jwk", "priv": <private JWK dict>} — uses provided JWK (must include
  private fields); derives public JWK for header embedding.

Signature format returned (detached):
{
  "alg": "<JWS alg>",
  "format": "dpop+jwt",
  "sig": "<compact JWS string>",     # the DPoP proof JWT
  "jkt": "<b64url SHA-256 JWK thumbprint>",  # convenience for RS checks
}

Verification options:
- require = {
    "htm": "POST",                   # required HTTP method
    "htu": "https://api.example/x",  # required URL (scheme/host/path[?query])
    "max_skew_s": 300,               # iat window (default 300s)
    "algs": ["ES256","EdDSA"],       # optional allowlist of algs
    "replay": {                      # optional replay store hooks
       "seen": callable(jti)->bool,  # return True if already seen
       "mark": callable(jti, ttl_s)  # persist jti with TTL
    },
    "nonce": "server-issued-nonce",  # optional DPoP-Nonce to enforce
    "access_token": "<Bearer ...>",  # optional; if set, check 'ath'
  }

Notes:
- For resource servers, compare the proof JWK thumbprint to access_token.cnf.jkt.
- For authorization servers issuing sender-constrained tokens, bind cnf.jkt to
  jwk_thumbprint(proof.header.jwk) at /token time.

Dependencies: swarmauri_signing_jws, cryptography.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
import typing as t
from dataclasses import dataclass

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519

from swarmauri_signing_jws import JwsSignerVerifier

# Align with your base / interfaces
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Signature, Envelope, Canon  # types only
from swarmauri_core.crypto.types import KeyRef, JWAAlg

# ────────────────────────── Helpers: base64url / JWK ──────────────────────────


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
    # RFC 7638 canonicalization
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
    # ath = b64url( SHA-256( access_token ) )
    if tok.startswith("Bearer "):
        tok = tok[7:]
    return _sha256_b64url(tok.encode("ascii"))


# ───────────────────────── KeyRef resolution (PEM / JWK) ──────────────────────


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


# ─────────────────────────── DPoP proof builder/verifier ──────────────────────

_ALLOWED_ALGS = {JWAAlg.ES256, JWAAlg.RS256, JWAAlg.EDDSA}


def _now() -> int:
    return int(time.time())


class DpopSigner(SigningBase):
    """DPoP proof signer/verifier that conforms to the SigningBase/ISigning surface."""

    def __init__(self) -> None:
        self._jws = JwsSignerVerifier()

    def supports(self) -> dict[str, t.Iterable[str]]:
        return {
            "algs": tuple(sorted(a.value for a in _ALLOWED_ALGS)),
            "canons": ("raw", "json"),
            "features": ("detached_only",),
        }

    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: t.Optional[Canon] = None,
        opts: t.Optional[dict[str, t.Any]] = None,
    ) -> bytes:
        if canon in (None, "raw"):
            if isinstance(env, (bytes, bytearray)):
                return bytes(env)
            if isinstance(env, str):
                return env.encode("utf-8")
        if canon == "json" or not isinstance(env, (bytes, bytearray, str)):
            return _json_c14n(env)  # type: ignore[arg-type]
        raise ValueError(f"Unsupported canon: {canon}")

    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: t.Optional[str] = None,
        opts: t.Optional[dict[str, t.Any]] = None,
    ) -> t.Sequence[Signature]:
        o = opts or {}
        htm = (o.get("htm") or "").upper()
        htu = o.get("htu") or ""
        if not htm or not htu:
            raise ValueError("DPoP signing requires opts['htm'] and opts['htu']")

        km = _resolve_keyref(key, alg)
        if km.alg not in _ALLOWED_ALGS:
            raise ValueError(f"Unsupported alg for DPoP: {km.alg.value}")

        iat = int(o.get("iat") or _now())
        jti = o.get("jti") or _b64url(
            hashlib.sha256(f"{iat}:{htm}:{htu}".encode()).digest()
        )
        nonce = o.get("nonce")
        access_token = o.get("access_token")

        claims: dict[str, t.Any] = {"htm": htm, "htu": htu, "iat": iat, "jti": jti}
        if nonce:
            claims["nonce"] = str(nonce)
        if access_token:
            claims["ath"] = _ath_from_access_token(access_token)

        header_extra = {"typ": "dpop+jwt", "jwk": km.pub_jwk}
        token = await self._jws.sign_compact(
            payload=claims,
            alg=km.alg,
            key=km.keyref,
            header_extra=header_extra,
        )
        jkt = _jwk_thumbprint_b64url(km.pub_jwk)
        return [
            {
                "alg": km.alg.value,
                "format": "dpop+jwt",
                "sig": token,
                "jkt": jkt,
            }
        ]

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: t.Sequence[Signature],
        *,
        require: t.Optional[dict[str, t.Any]] = None,
        opts: t.Optional[dict[str, t.Any]] = None,
    ) -> bool:
        if not signatures:
            return False
        req = require or {}
        method_req = (req.get("htm") or "").upper()
        url_req = req.get("htu") or ""
        if not method_req or not url_req:
            raise ValueError("DPoP verify requires require['htm'] and require['htu']")

        max_skew = int(req.get("max_skew_s", 300))
        allowed_algs = {
            (a if isinstance(a, JWAAlg) else JWAAlg(a))
            for a in (req.get("algs") or _ALLOWED_ALGS)
        }
        expect_nonce = req.get("nonce")
        expect_ath = req.get("access_token")
        replay = req.get("replay") or {}
        seen = replay.get("seen")
        mark = replay.get("mark")

        now = _now()

        for sig in signatures:
            token = sig.get("sig")
            if not isinstance(token, str):
                continue
            try:
                parts = token.split(".")
                if len(parts) != 3:
                    continue
                header = json.loads(_b64url_dec(parts[0]))
                if header.get("typ") != "dpop+jwt":
                    continue
                alg_raw = header.get("alg")
                jwk = header.get("jwk")
                alg_enum = JWAAlg(alg_raw)
                if alg_enum not in allowed_algs or not isinstance(jwk, dict):
                    continue

                result = await self._jws.verify_compact(
                    token,
                    jwks_resolver=lambda _kid, _alg, jwk=jwk: jwk,
                    alg_allowlist=[alg_enum],
                )
                claims = json.loads(result.payload.decode("utf-8"))

                if (claims.get("htm") or "").upper() != method_req:
                    continue
                if claims.get("htu") != url_req:
                    continue
                iat = int(claims.get("iat", 0))
                if abs(now - iat) > max_skew:
                    continue
                if expect_nonce is not None and claims.get("nonce") != expect_nonce:
                    continue
                if expect_ath is not None:
                    ath = claims.get("ath")
                    if not isinstance(ath, str) or ath != _ath_from_access_token(
                        expect_ath
                    ):
                        continue

                jti = claims.get("jti")
                if not isinstance(jti, str) or not jti:
                    continue
                if seen and seen(jti):
                    continue
                if mark:
                    try:
                        mark(jti, max_skew)
                    except Exception:
                        pass

                return True
            except Exception:
                continue
        return False

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: t.Optional[str] = None,
        canon: t.Optional[Canon] = None,
        opts: t.Optional[dict[str, t.Any]] = None,
    ) -> t.Sequence[Signature]:
        _ = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.sign_bytes(key, b"", alg=alg, opts=opts)

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: t.Sequence[Signature],
        *,
        canon: t.Optional[Canon] = None,
        require: t.Optional[dict[str, t.Any]] = None,
        opts: t.Optional[dict[str, t.Any]] = None,
    ) -> bool:
        _ = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.verify_bytes(b"", signatures, require=require, opts=opts)
