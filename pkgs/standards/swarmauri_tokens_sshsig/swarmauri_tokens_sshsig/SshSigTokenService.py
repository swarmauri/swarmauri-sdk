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
    """Encode bytes as URL-safe base64 without padding.

    data (bytes): Bytes to encode.
    RETURNS (str): Base64url-encoded string without padding.
    """
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64u_d(s: str) -> bytes:
    """Decode URL-safe base64 string with proper padding.

    s (str): Base64url string to decode.
    RETURNS (bytes): Decoded bytes.
    """
    pad = (-len(s)) % 4
    return base64.urlsafe_b64decode(s + ("=" * pad))


def _now_s() -> int:
    """Get the current time in seconds.

    RETURNS (int): Unix timestamp in seconds.
    """
    return int(time.time())


def _canonical_json(obj: Any) -> bytes:
    """Serialize an object to deterministic JSON bytes.

    obj (Any): Object to serialize.
    RETURNS (bytes): Canonical JSON representation encoded as UTF-8.
    """
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sig_input(namespace: str, payload_b64u: str) -> bytes:
    """Construct the signature preimage with namespace binding.

    namespace (str): Namespace associated with the token.
    payload_b64u (str): Base64url-encoded payload.
    RETURNS (bytes): Bytes used as signing input.
    """
    return (
        b"sshsig:v1:" + namespace.encode("utf-8") + b":" + payload_b64u.encode("ascii")
    )


_SUPPORTED = ("ssh-ed25519", "ecdsa-sha2-nistp256")


class SshSigTokenService(TokenServiceBase):
    """Token service using SSH signatures in a compact three-part format."""

    type: Literal["SshSigTokenService"] = "SshSigTokenService"

    def __init__(
        self,
        key_provider: IKeyProvider,
        *,
        default_issuer: Optional[str] = None,
        default_namespace: str = "token",
    ) -> None:
        """Initialize the token service.

        key_provider (IKeyProvider): Provider used to resolve signing keys.
        default_issuer (Optional[str]): Issuer claim applied when minting tokens.
        default_namespace (str): Namespace used when constructing signatures.
        RETURNS (None): The initialized service.
        """
        super().__init__()
        self._kp = key_provider
        self._iss = default_issuer
        self._ns = default_namespace

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Describe supported token formats and algorithms.

        RETURNS (Mapping[str, Iterable[str]]): Mapping of supported formats and
            algorithm identifiers.
        """
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
        """Mint a signed SSHSIG token.

        claims (Dict[str, Any]): Claims to encode in the payload.
        alg (str): Identifier of the signing algorithm to use.
        kid (str | None): Key identifier for the signing key.
        key_version (int | None): Specific version of the key to use.
        headers (Optional[Dict[str, Any]]): Additional header values.
        lifetime_s (Optional[int]): Lifetime of the token in seconds.
        issuer (Optional[str]): Issuer claim to embed in the token.
        subject (Optional[str]): Subject claim value.
        audience (Optional[str | list[str]]): Intended audience claim.
        scope (Optional[str]): Scope claim for the token.
        RETURNS (str): Serialized token string.
        """
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
        """Verify a token and return its claims.

        token (str): Token string to verify.
        issuer (Optional[str]): Expected issuer claim.
        audience (Optional[str | list[str]]): Expected audience claim.
        leeway_s (int): Allowed clock skew in seconds when validating times.
        RETURNS (Dict[str, Any]): Verified claims payload.
        """
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
        """Retrieve the provider's JSON Web Key Set.

        RETURNS (dict): JWKS dictionary supplied by the key provider.
        """
        return await self._kp.jwks()
