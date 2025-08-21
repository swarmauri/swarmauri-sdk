"""SSH signature token service implementation."""

from __future__ import annotations

import base64
import json
import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)

from swarmauri_base.tokens.TokenServiceBase import TokenServiceBase
from swarmauri_core.keys.IKeyProvider import IKeyProvider


def _b64u(data: bytes) -> str:
    """Return URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64u_d(s: str) -> bytes:
    """Decode URL-safe base64 string with added padding."""
    pad = (-len(s)) % 4
    return base64.urlsafe_b64decode(s + ("=" * pad))


def _now_s() -> int:
    """Return current time in seconds."""
    return int(time.time())


def _canonical_json(obj: Any) -> bytes:
    """Return deterministic JSON representation of an object."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sig_input(namespace: str, payload_b64u: str) -> bytes:
    """Return signature input with namespace binding."""
    return (
        b"sshsig:v1:" + namespace.encode("utf-8") + b":" + payload_b64u.encode("ascii")
    )


_SUPPORTED = ("ssh-ed25519", "ecdsa-sha2-nistp256")


class SshSigTokenService(TokenServiceBase):
    """SSH-signature token service (compact 3-part format, JWT-like)."""

    type: Literal["SshSigTokenService"] = "SshSigTokenService"

    def __init__(
        self,
        key_provider: IKeyProvider,
        *,
        default_issuer: Optional[str] = None,
        default_namespace: str = "token",
    ) -> None:
        """Initialize the service."""
        super().__init__()
        self._kp = key_provider
        self._iss = default_issuer
        self._ns = default_namespace

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return supported formats and algorithms."""
        return {"formats": ("SSHSIG",), "algs": _SUPPORTED}

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
        """Mint a token signed with the given algorithm."""
        if alg not in _SUPPORTED:
            raise ValueError(f"Unsupported SSH signature alg: {alg}")

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

        if not kid:
            raise ValueError("mint() requires 'kid' of a signing key")
        ref = await self._kp.get_key(kid, key_version, include_secret=True)
        if ref.material is None:
            raise RuntimeError("Signing key is not exportable under current policy")

        kidver = f"{ref.kid}.{ref.version}"
        hdr = dict(headers or {})
        hdr.setdefault("typ", "SSHSIG")
        hdr["alg"] = alg
        hdr["kid"] = kidver
        hdr.setdefault("ns", self._ns)

        hdr_b64 = _b64u(_canonical_json(hdr))
        pl_b64 = _b64u(_canonical_json(payload))
        preimage = _sig_input(hdr["ns"], pl_b64)

        sk = load_pem_private_key(ref.material, password=None)
        if alg == "ssh-ed25519":
            if not isinstance(sk, Ed25519PrivateKey):
                raise ValueError("ssh-ed25519 requires an Ed25519 private key (PEM)")
            sig = sk.sign(preimage)
        elif alg == "ecdsa-sha2-nistp256":
            if not isinstance(sk, ec.EllipticCurvePrivateKey) or sk.curve.name not in (
                "secp256r1",
                "prime256v1",
            ):
                raise ValueError(
                    "ecdsa-sha2-nistp256 requires an ECDSA P-256 private key"
                )
            sig = sk.sign(preimage, ec.ECDSA(hashes.SHA256()))
        else:
            raise ValueError(f"Unsupported alg: {alg}")

        return f"{hdr_b64}.{pl_b64}.{_b64u(sig)}"

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, Any]:
        """Verify a token and return its claims."""
        try:
            hdr_b64, pl_b64, sig_b64 = token.split(".", 2)
        except ValueError as exc:
            raise ValueError("Invalid token format") from exc

        hdr = json.loads(_b64u_d(hdr_b64).decode("utf-8"))
        payload = json.loads(_b64u_d(pl_b64).decode("utf-8"))
        sig = _b64u_d(sig_b64)

        if hdr.get("typ") != "SSHSIG":
            raise ValueError("Invalid typ (expected SSHSIG)")
        alg = hdr.get("alg")
        if alg not in _SUPPORTED:
            raise ValueError(f"Unsupported alg: {alg}")
        kidver = hdr.get("kid")
        if not kidver:
            raise ValueError("Missing 'kid' in header")
        ns = hdr.get("ns") or self._ns

        base_kid, _, v_str = kidver.partition(".")
        ver = int(v_str) if v_str else None
        ref = await self._kp.get_key(base_kid, ver, include_secret=False)
        if ref.public is None:
            await self._kp.get_public_jwk(base_kid, ver)
            raise RuntimeError(
                "Public key PEM not available from provider; ensure .public is populated"
            )

        pk = load_pem_public_key(ref.public)
        preimage = _sig_input(ns, pl_b64)
        try:
            if alg == "ssh-ed25519":
                if not isinstance(pk, Ed25519PublicKey):
                    raise ValueError(
                        "Header alg is ssh-ed25519 but public key is not Ed25519"
                    )
                pk.verify(sig, preimage)
            elif alg == "ecdsa-sha2-nistp256":
                if not isinstance(
                    pk, ec.EllipticCurvePublicKey
                ) or pk.curve.name not in ("secp256r1", "prime256v1"):
                    raise ValueError(
                        "Header alg is ecdsa-sha2-nistp256 but public key is not P-256"
                    )
                pk.verify(sig, preimage, ec.ECDSA(hashes.SHA256()))
        except InvalidSignature as exc:
            raise ValueError("Signature verification failed") from exc

        now = _now_s()
        leeway = int(leeway_s)
        if "exp" in payload and now > int(payload["exp"]) + leeway:
            raise ValueError("Token expired")
        if "nbf" in payload and now + leeway < int(payload["nbf"]):
            raise ValueError("Token not yet valid")
        if "iat" in payload and now + leeway < int(payload["iat"]):
            raise ValueError("Token 'iat' is in the future")

        expected_iss = issuer or self._iss
        if expected_iss is not None and payload.get("iss") != expected_iss:
            raise ValueError("Issuer (iss) mismatch")

        if audience is not None:
            aud_claim = payload.get("aud")
            if isinstance(audience, str):
                ok = (audience == aud_claim) or (
                    isinstance(aud_claim, list) and audience in aud_claim
                )
            else:
                ok = any(
                    a == aud_claim or (isinstance(aud_claim, list) and a in aud_claim)
                    for a in audience
                )
            if not ok:
                raise ValueError("Audience (aud) mismatch")

        return payload

    async def jwks(self) -> dict:
        """Return provider's JWKS."""
        return await self._kp.jwks()
