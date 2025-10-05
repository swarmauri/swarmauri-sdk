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

import json
import time
import typing as t
from uuid import uuid4

from swarmauri_signing_jws import JwsSignerVerifier

# Align with your base / interfaces
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Signature, Envelope, Canon  # types only
from swarmauri_core.crypto.types import Alg, KeyRef, JWAAlg

from ._utils import (
    _ath_from_access_token,
    _b64url_dec,
    _jwk_thumbprint_b64url,
    _json_c14n,
    _resolve_keyref,
)

# ────────────────────────── Helpers: base64url / JWK ──────────────────────────
# ─────────────────────────── DPoP proof builder/verifier ──────────────────────

_ALLOWED_ALGS = {JWAAlg.ES256, JWAAlg.RS256, JWAAlg.EDDSA}


def _now() -> int:
    return int(time.time())


class DpopSigner(SigningBase):
    """DPoP proof signer/verifier that conforms to the SigningBase/ISigning surface."""

    def __init__(self) -> None:
        self._jws = JwsSignerVerifier()

    def supports(self) -> dict[str, t.Iterable[str]]:
        structured = ("detached-bytes", "dpop-http-request", "structured-json")
        return {
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("raw", "mapping", *structured),
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
        jti = o.get("jti") or str(uuid4())
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

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: t.Optional[Alg] = None,
        opts: t.Optional[t.Mapping[str, t.Any]] = None,
    ) -> t.Sequence[Signature]:
        return await self.sign_bytes(key, digest, alg=alg, opts=opts)

    async def verify_digest(
        self,
        digest: bytes,
        signatures: t.Sequence[Signature],
        *,
        require: t.Optional[t.Mapping[str, t.Any]] = None,
        opts: t.Optional[t.Mapping[str, t.Any]] = None,
    ) -> bool:
        return await self.verify_bytes(digest, signatures, require=require, opts=opts)

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
