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

Dependencies: PyJWT, cryptography.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
import typing as t
from dataclasses import dataclass

import jwt
from jwt import algorithms as jwt_algs
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# Align with your base / interfaces
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Signature, Envelope, Canon  # types only

# ────────────────────────── Helpers: base64url / JWK ──────────────────────────


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _sha256_b64url(data: bytes) -> str:
    return _b64url(hashlib.sha256(data).digest())


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
    priv: t.Any  # PyJWT accepts cryptography key object or PEM string
    pub_jwk: dict  # public JWK (embedded into DPoP header)
    alg: str  # JWS alg hint


def _derive_public_jwk_from_priv_pem(pem_bytes: bytes, alg: str) -> dict:
    key = load_pem_private_key(pem_bytes, password=None)
    jwk = jwt_algs.get_default_algorithms()[alg].to_jwk(key.public_key())
    return json.loads(jwk)


def _resolve_keyref(key: dict, alg: t.Optional[str]) -> _KeyMat:
    if not isinstance(key, dict):
        raise TypeError("DPoP KeyRef must be a dict")
    kind = key.get("kind")
    if kind == "pem":
        priv = key.get("priv")
        if isinstance(priv, str):
            priv = priv.encode("utf-8")
        if not isinstance(priv, (bytes, bytearray)):
            raise TypeError("KeyRef['priv'] must be PEM bytes|str for kind='pem'")
        # Default alg if not provided: ES256 preferred; allow RS256/EdDSA via override
        the_alg = alg or key.get("alg") or "ES256"
        pub_jwk = _derive_public_jwk_from_priv_pem(bytes(priv), the_alg)
        return _KeyMat(priv=bytes(priv), pub_jwk=pub_jwk, alg=the_alg)
    if kind == "jwk":
        priv_jwk = key.get("priv")
        if not isinstance(priv_jwk, dict):
            raise TypeError("KeyRef['priv'] must be a private JWK dict for kind='jwk'")
        # alg hint from arg or jwk["alg"] or default ES256
        the_alg = alg or priv_jwk.get("alg") or "ES256"
        # Build a public JWK by dropping private params
        pub_jwk = {
            k: v for k, v in priv_jwk.items() if k in ("kty", "crv", "x", "y", "n", "e")
        }
        return _KeyMat(priv=priv_jwk, pub_jwk=pub_jwk, alg=the_alg)
    raise TypeError(f"Unsupported KeyRef.kind: {kind}")


# ─────────────────────────── DPoP proof builder/verifier ──────────────────────

_ALLOWED_ALGS = {"ES256", "RS256", "EdDSA"}


def _now() -> int:
    return int(time.time())


class DpopSigner(SigningBase):
    """DPoP proof signer/verifier that conforms to the SigningBase/ISigning surface."""

    def supports(self) -> dict[str, t.Iterable[str]]:
        return {
            "algs": tuple(sorted(_ALLOWED_ALGS)),
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
        key: dict,
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
            raise ValueError(f"Unsupported alg for DPoP: {km.alg}")

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

        header = {"typ": "dpop+jwt", "alg": km.alg, "jwk": km.pub_jwk}

        token = jwt.encode(
            payload=claims,
            key=km.priv,
            algorithm=km.alg,
            headers=header,
        )
        jkt = _jwk_thumbprint_b64url(km.pub_jwk)
        return [{"alg": km.alg, "format": "dpop+jwt", "sig": token, "jkt": jkt}]

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
        allowed_algs = set(req.get("algs") or _ALLOWED_ALGS)
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
                header = jwt.get_unverified_header(token)
                if header.get("typ") != "dpop+jwt":
                    continue
                alg = header.get("alg")
                jwk = header.get("jwk")
                if alg not in allowed_algs or not isinstance(jwk, dict):
                    continue

                key_obj = jwt_algs.get_default_algorithms()[alg].from_jwk(
                    json.dumps(jwk)
                )
                claims = jwt.decode(
                    token,
                    key=key_obj,
                    algorithms=[alg],
                    options={"verify_aud": False, "verify_exp": False},
                )

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
                if isinstance(jti, str) and seen and seen(jti):
                    continue
                if isinstance(jti, str) and mark:
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
        key: dict,
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
