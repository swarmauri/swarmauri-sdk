"""
autoapi_authn.jwtoken
=====================

A thin, stateless helper around **PyJWT** that signs and decodes
Ed25519 (`alg = "EdDSA"`) access- and refresh-tokens.

Key material is loaded lazily from *crypto.signing_key()* /
*crypto.public_key()* and memoised in-process.

Typical usage
-------------
>>> from datetime import timedelta
>>> from autoapi_authn.jwtoken import JWTCoder
>>> coder = JWTCoder.default()

# sign
>>> token = coder.sign(sub="user-uuid", tid="tenant-uuid", scopes=["task:write"])

# decode / verify
>>> payload = coder.decode(token)
>>> payload["sub"]
'user-uuid'

Refresh-token pair
------------------
`sign_pair()` returns a tuple **(access, refresh)**.
A refresh-token has a longer TTL and carries a distinct `"typ": "refresh"`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

import jwt
from jwt.exceptions import InvalidTokenError

from .crypto import public_key, signing_key

_ALG = "EdDSA"
_ACCESS_TTL = timedelta(minutes=60)
_REFRESH_TTL = timedelta(days=7)


class JWTCoder:
    """
    Stateless JWT helper bound to a specific Ed25519 key-pair.

    Parameters
    ----------
    private_pem : bytes
    public_pem  : bytes
    """

    __slots__ = ("_priv", "_pub")

    def __init__(self, private_pem: bytes, public_pem: bytes):
        self._priv = private_pem
        self._pub = public_pem

    # -----------------------------------------------------------------
    # Convenience factories
    # -----------------------------------------------------------------
    @classmethod
    def default(cls) -> "JWTCoder":
        """Return a coder bound to the key-pair on disk."""
        return cls(signing_key(), public_key())

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------
    def sign(
        self,
        *,
        sub: str,
        tid: str,
        ttl: timedelta = _ACCESS_TTL,
        typ: str = "access",
        **extra: Any,
    ) -> str:
        """
        Create a JWT.

        Parameters
        ----------
        sub     : Subject (user-id)
        tid     : Tenant-id
        scopes  : List of coarse scopes
        ttl     : Lifetime (default 60 min for access tokens)
        typ     : "access" or "refresh"
        extra   : Arbitrary extra claims
        """
        now = datetime.now(timezone.utc)
        payload: Dict[str, Any] = {
            "sub": sub,
            "tid": tid,
            "typ": typ,
            "iat": now,
            "exp": now + ttl,
            **extra,
        }
        return jwt.encode(payload, self._priv, algorithm=_ALG)

    def sign_pair(self, *, sub: str, tid: str, **extra: Any) -> Tuple[str, str]:
        """Return `(access_token, refresh_token)`."""
        access = self.sign(sub=sub, tid=tid, **extra)
        refresh = self.sign(
            sub=sub,
            tid=tid,
            ttl=_REFRESH_TTL,
            typ="refresh",
            **extra,
        )
        return access, refresh

    def decode(self, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        """
        Verify signature and (optionally) expiration, return payload dict.

        Raises
        ------
        jwt.InvalidTokenError
            If signature is invalid, token is expired, or malformed.
        """
        options = {"verify_exp": verify_exp}
        return jwt.decode(
            token,
            self._pub,
            algorithms=[_ALG],
            options=options,
        )

    # -----------------------------------------------------------------
    # Refresh flow helper (optional)
    # -----------------------------------------------------------------
    def refresh(self, refresh_token: str) -> Tuple[str, str]:
        """
        Validate *refresh_token* and return a **new token pair**.

        Raises
        ------
        jwt.InvalidTokenError
            If token is invalid or not a refresh token.
        """
        payload = self.decode(refresh_token)
        if payload.get("typ") != "refresh":
            raise InvalidTokenError("token is not a refresh token")

        # strip JWT reserved claims before re-signing
        base_claims = {
            k: v for k, v in payload.items() if k not in {"iat", "exp", "typ"}
        }
        return self.sign_pair(**base_claims)
