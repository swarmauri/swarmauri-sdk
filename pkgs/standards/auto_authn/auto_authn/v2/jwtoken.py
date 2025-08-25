"""
autoapi_authn.jwtoken
=====================

JWT minting and verification via swarmauri token plugins.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict, Iterable, Optional, Tuple

from .deps import (
    ExportPolicy,
    FileKeyProvider,
    JWTTokenService,
    JWAAlg,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
)

from .runtime_cfg import settings
from .rfc8705 import validate_certificate_binding
from .crypto import _KID_PATH, _provider

_ACCESS_TTL = timedelta(minutes=60)
_REFRESH_TTL = timedelta(days=7)


@lru_cache(maxsize=1)
def _svc() -> Tuple[JWTTokenService, str]:
    kp: FileKeyProvider = _provider()
    if _KID_PATH.exists():
        kid = _KID_PATH.read_text().strip()
    else:
        spec = KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.ED25519,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            label="jwt_ed25519",
        )
        ref = asyncio.run(kp.create_key(spec))
        kid = ref.kid
        _KID_PATH.parent.mkdir(parents=True, exist_ok=True)
        _KID_PATH.write_text(kid)
    service = JWTTokenService(kp)
    return service, kid


class JWTCoder:
    """Stateless JWT helper backed by ``JWTTokenService``."""

    __slots__ = ("_svc", "_kid")

    def __init__(self, service: JWTTokenService, kid: str):
        self._svc = service
        self._kid = kid

    @classmethod
    def default(cls) -> "JWTCoder":
        svc, kid = _svc()
        return cls(svc, kid)

    # -----------------------------------------------------------------
    def sign(
        self,
        *,
        sub: str,
        tid: str,
        ttl: timedelta = _ACCESS_TTL,
        typ: str = "access",
        issuer: Optional[str] = None,
        audience: Optional[Iterable[str] | str] = None,
        cert_thumbprint: Optional[str] = None,
        **extra: Any,
    ) -> str:
        now = datetime.now(timezone.utc)
        payload: Dict[str, Any] = {
            "sub": sub,
            "tid": tid,
            "typ": typ,
            "iat": int(now.timestamp()),
            "exp": int((now + ttl).timestamp()),
            **extra,
        }
        if settings.enable_rfc8705:
            if cert_thumbprint is None:
                raise ValueError(
                    "cert_thumbprint required when RFC 8705 support is enabled"
                )
            payload["cnf"] = {"x5t#S256": cert_thumbprint}
        if settings.enable_rfc9068:
            if issuer is None or audience is None:
                raise ValueError(
                    "issuer and audience required when RFC 9068 support is enabled"
                )
            from .rfc9068 import add_rfc9068_claims

            payload = add_rfc9068_claims(payload, issuer=issuer, audience=audience)
        token = asyncio.run(
            self._svc.mint(
                payload,
                alg=JWAAlg.EDDSA,
                kid=self._kid,
                lifetime_s=int(ttl.total_seconds()),
                subject=sub,
                issuer=issuer,
                audience=audience,
            )
        )
        return token

    def sign_pair(
        self, *, sub: str, tid: str, cert_thumbprint: Optional[str] = None, **extra: Any
    ) -> Tuple[str, str]:
        access = self.sign(sub=sub, tid=tid, cert_thumbprint=cert_thumbprint, **extra)
        refresh = self.sign(
            sub=sub,
            tid=tid,
            ttl=_REFRESH_TTL,
            typ="refresh",
            cert_thumbprint=cert_thumbprint,
            **extra,
        )
        return access, refresh

    def decode(
        self,
        token: str,
        verify_exp: bool = True,
        issuer: Optional[str] = None,
        audience: Optional[Iterable[str] | str] = None,
        cert_thumbprint: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = asyncio.run(self._svc.verify(token, issuer=issuer, audience=audience))
        if verify_exp:
            exp = payload.get("exp")
            if exp is not None and int(exp) < int(
                datetime.now(timezone.utc).timestamp()
            ):
                raise ValueError("token is expired")
        if settings.enable_rfc8705:
            if cert_thumbprint is None:
                raise ValueError(
                    "certificate thumbprint required for mTLS per RFC 8705"
                )
            validate_certificate_binding(payload, cert_thumbprint)
        if settings.enable_rfc9068:
            if issuer is None or audience is None:
                raise ValueError(
                    "issuer and audience required for JWT access tokens per RFC 9068"
                )
            from .rfc9068 import validate_rfc9068_claims

            validate_rfc9068_claims(payload, issuer=issuer, audience=audience)
        return payload

    def refresh(self, refresh_token: str) -> Tuple[str, str]:
        payload = self.decode(refresh_token)
        if payload.get("typ") != "refresh":
            raise ValueError("token is not a refresh token")
        base_claims = {
            k: v for k, v in payload.items() if k not in {"iat", "exp", "typ"}
        }
        return self.sign_pair(**base_claims)
