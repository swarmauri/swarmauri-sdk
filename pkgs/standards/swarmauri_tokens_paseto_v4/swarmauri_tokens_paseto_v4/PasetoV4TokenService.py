from __future__ import annotations

import base64
import json
import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Sequence

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
)

try:
    import pyseto  # https://pypi.org/project/pyseto/

    _PASETO_OK = True
except Exception:  # pragma: no cover
    _PASETO_OK = False

from swarmauri_core.keys.IKeyProvider import IKeyProvider


class ITokenService:  # pragma: no cover - minimal placeholder
    pass


try:
    from swarmauri_base.tokens.TokenServiceBase import TokenServiceBase
except Exception:  # pragma: no cover - fallback
    from swarmauri_base.ComponentBase import ComponentBase

    class TokenServiceBase(ComponentBase, ITokenService):  # type: ignore[misc]
        type: Literal["TokenServiceBase"] = "TokenServiceBase"


_ALGS = ("v4.public", "v4.local", "paseto.v4.public", "paseto.v4.local")


def _require_pyseto() -> None:
    if not _PASETO_OK:
        raise ImportError(
            "PasetoV4TokenService requires 'pyseto'. Install with: pip install pyseto"
        )


def _now_s() -> int:
    return int(time.time())


def _b64u_to_bytes(s: str) -> bytes:
    pad = -len(s) % 4
    return base64.urlsafe_b64decode(s + ("=" * pad))


def _as_footer_json(d: Dict[str, Any] | None) -> bytes | None:
    if not d:
        return None
    return json.dumps(d, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _as_payload_json(d: Dict[str, Any]) -> bytes:
    return json.dumps(d, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _parse_prefix(token: str) -> tuple[str, str]:
    parts = token.split(".", 2)
    if len(parts) < 3:
        raise ValueError("Invalid PASETO token format")
    return parts[0], parts[1]


class PasetoV4TokenService(TokenServiceBase):
    """PASETO v4 token service supporting ``v4.public`` and ``v4.local``."""

    type: Literal["PasetoV4TokenService"] = "PasetoV4TokenService"

    def __init__(
        self,
        key_provider: IKeyProvider,
        *,
        default_issuer: Optional[str] = None,
        implicit_assertion: Optional[bytes | str] = None,
        local_kids: Optional[Sequence[str]] = None,
    ) -> None:
        super().__init__()
        _require_pyseto()
        self._kp = key_provider
        self._iss = default_issuer
        if isinstance(implicit_assertion, str):
            implicit_assertion = implicit_assertion.encode("utf-8")
        self._ia = implicit_assertion
        self._local_kids = tuple(local_kids) if local_kids else ()

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {"formats": ("PASETO",), "algs": ("v4.public", "v4.local")}

    async def mint(
        self,
        claims: Dict[str, Any],
        *,
        alg: str,
        kid: str | None = None,
        key_version: int | None = None,
        headers: Optional[Dict[str, Any]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        scope: Optional[str] = None,
    ) -> str:
        _require_pyseto()
        if alg not in _ALGS:
            raise ValueError(f"Unsupported alg: {alg}")
        purpose = "public" if "public" in alg else "local"

        now = _now_s()
        payload = dict(claims)
        payload.setdefault("iat", now)
        payload.setdefault("nbf", now)
        if lifetime_s:
            payload.setdefault("exp", now + int(lifetime_s))
        if issuer or self._iss:
            payload.setdefault("iss", issuer or self._iss)
        if subject:
            payload.setdefault("sub", subject)
        if audience:
            payload.setdefault("aud", audience)
        if scope:
            payload.setdefault("scope", scope)

        if purpose == "public":
            if not kid:
                raise ValueError("v4.public mint requires 'kid'")
            ref = await self._kp.get_key(kid, key_version, include_secret=True)
            if not ref.material:
                raise RuntimeError("Signing key not exportable under current policy")
            sk = load_pem_private_key(ref.material, password=None)
            if not isinstance(sk, Ed25519PrivateKey):
                raise ValueError("v4.public requires an Ed25519 private key")
            pem_priv = sk.private_bytes(
                Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
            )
            key = pyseto.Key.new(version=4, purpose="public", key=pem_priv)
            footer = _as_footer_json({"kid": f"{ref.kid}.{ref.version}"})
            token_bytes = pyseto.encode(
                key,
                _as_payload_json(payload),
                footer=footer,
                implicit_assertion=self._ia or b"",
            )
            return token_bytes.decode("utf-8")

        if not kid:
            raise ValueError("v4.local mint requires 'kid'")
        ref = await self._kp.get_key(kid, key_version, include_secret=True)
        if not ref.material:
            raise RuntimeError("Symmetric key not exportable under current policy")
        if len(ref.material) != 32:
            raise ValueError("v4.local requires a 32-byte secret key")
        key = pyseto.Key.new(version=4, purpose="local", key=ref.material)
        footer = _as_footer_json({"kid": f"{ref.kid}.{ref.version}"})
        token_bytes = pyseto.encode(
            key,
            _as_payload_json(payload),
            footer=footer,
            implicit_assertion=self._ia or b"",
        )
        return token_bytes.decode("utf-8")

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, Any]:
        _require_pyseto()
        ver, purpose = _parse_prefix(token)
        if ver != "v4":
            raise ValueError(f"Unsupported PASETO version: {ver}")

        payload_obj: Dict[str, Any] | None = None

        if purpose == "public":
            jwks = await self._kp.jwks()
            keys: list[pyseto.Key] = []
            for jw in jwks.get("keys", []):
                if jw.get("kty") == "OKP" and jw.get("crv") == "Ed25519" and "x" in jw:
                    x = _b64u_to_bytes(jw["x"])
                    pub = Ed25519PublicKey.from_public_bytes(x)
                    pem_pub = pub.public_bytes(
                        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
                    )
                    keys.append(
                        pyseto.Key.new(version=4, purpose="public", key=pem_pub)
                    )

            last_err: Optional[Exception] = None
            for k in keys:
                try:
                    res = pyseto.decode(k, token, implicit_assertion=self._ia or b"")
                    payload_obj = json.loads(res.payload)
                    break
                except Exception as e:  # pragma: no cover
                    last_err = e
                    continue
            if payload_obj is None:
                raise ValueError(
                    f"PASETO verification failed (public): {last_err}"
                ) from last_err

        else:
            if not self._local_kids:
                raise RuntimeError(
                    "v4.local verify requires PasetoV4TokenService(local_kids=[...])"
                )
            last_err: Optional[Exception] = None
            for kid in self._local_kids:
                try:
                    ref = await self._kp.get_key(kid, None, include_secret=True)
                    if not ref.material or len(ref.material) != 32:
                        continue
                    k = pyseto.Key.new(version=4, purpose="local", key=ref.material)
                    res = pyseto.decode(k, token, implicit_assertion=self._ia or b"")
                    payload_obj = json.loads(res.payload)
                    break
                except Exception as e:
                    last_err = e
                    continue
            if payload_obj is None:
                raise ValueError(
                    f"PASETO verification failed (local): {last_err}"
                ) from last_err

        now = _now_s()
        leeway = int(leeway_s)

        if "exp" in payload_obj and now > int(payload_obj["exp"]) + leeway:
            raise ValueError("Token expired")
        if "nbf" in payload_obj and now + leeway < int(payload_obj["nbf"]):
            raise ValueError("Token not yet valid")
        if "iat" in payload_obj and now + leeway < int(payload_obj["iat"]):
            raise ValueError("Token 'iat' is in the future")

        expected_iss = issuer or self._iss
        if expected_iss is not None and payload_obj.get("iss") != expected_iss:
            raise ValueError("Issuer (iss) mismatch")

        if audience is not None:
            aud_claim = payload_obj.get("aud")
            if isinstance(audience, str):
                ok = audience == aud_claim or (
                    isinstance(aud_claim, list) and audience in aud_claim
                )
            else:
                ok = any(
                    a == aud_claim or (isinstance(aud_claim, list) and a in aud_claim)
                    for a in audience
                )
            if not ok:
                raise ValueError("Audience (aud) mismatch")

        return payload_obj

    async def jwks(self) -> Mapping[str, Any]:
        return await self._kp.jwks()
