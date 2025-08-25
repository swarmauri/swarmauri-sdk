"""JWT minting and verification via swarmauri token plugins."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict, Iterable, Optional, Tuple

from jwt.exceptions import InvalidKeyError, InvalidTokenError

from .deps import (
    ExportPolicy,
    FileKeyProvider,
    JWTTokenService,
    LocalKeyProvider,
    JWAAlg,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
)
from .runtime_cfg import settings
from .rfc8705 import validate_certificate_binding
from .crypto import _DEFAULT_KEY_PATH, _provider

_ACCESS_TTL = timedelta(minutes=60)
_REFRESH_TTL = timedelta(days=7)
_ALG = JWAAlg.EDDSA.value


@lru_cache(maxsize=1)
def _svc() -> Tuple[JWTTokenService, str]:
    kp: FileKeyProvider = _provider()
    if _DEFAULT_KEY_PATH.exists():
        kid = _DEFAULT_KEY_PATH.read_text().strip()
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
        _DEFAULT_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        _DEFAULT_KEY_PATH.write_text(kid)
    service = JWTTokenService(kp)
    return service, kid


class JWTCoder:
    """Stateless JWT helper backed by ``JWTTokenService``.

    ``JWTCoder`` historically accepted a private/public key pair and
    constructed its own :class:`JWTTokenService`.  Recent refactoring switched
    the constructor to require an already configured service instance.  The
    tests for RFC 9068 still rely on the original behaviour, so the
    initializer now supports both invocation styles:

    ``JWTCoder(service, kid)`` -- use the provided service directly.

    ``JWTCoder(private_key_pem, public_key_pem)`` -- build an ephemeral
    service from the PEM encoded Ed25519 key pair.
    """

    __slots__ = ("_svc", "_kid")

    def __init__(self, arg1: JWTTokenService | bytes, arg2: str | bytes):
        if isinstance(arg1, JWTTokenService) and isinstance(arg2, str):
            self._svc = arg1
            self._kid = arg2
            return

        if isinstance(arg1, (bytes, bytearray)) and isinstance(
            arg2, (bytes, bytearray)
        ):
            kp = LocalKeyProvider()
            spec = KeySpec(
                klass=KeyClass.asymmetric,
                alg=KeyAlg.ED25519,
                uses=(KeyUse.SIGN, KeyUse.VERIFY),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                label="jwt_ed25519",
            )
            ref = asyncio.run(kp.import_key(spec, arg1, public=arg2))
            self._svc = JWTTokenService(kp)
            self._kid = ref.kid
            return

        raise TypeError(
            "JWTCoder requires (JWTTokenService, kid) or (private_pem, public_pem)"
        )

    @classmethod
    def default(cls) -> "JWTCoder":
        svc, kid = _svc()
        return cls(svc, kid)

    # -----------------------------------------------------------------
    async def async_sign(
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
                    "cert_thumbprint required when RFC 8705 support is enabled",
                )
            payload["cnf"] = {"x5t#S256": cert_thumbprint}
        if settings.enable_rfc9068:
            if issuer is None or audience is None:
                raise ValueError(
                    "issuer and audience required when RFC 9068 support is enabled",
                )
            from .rfc9068 import add_rfc9068_claims

            payload = add_rfc9068_claims(payload, issuer=issuer, audience=audience)
        token = await self._svc.mint(
            payload,
            alg=JWAAlg.EDDSA,
            kid=self._kid,
            lifetime_s=int(ttl.total_seconds()),
            subject=sub,
            issuer=issuer,
            audience=audience,
        )
        return token

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
        return asyncio.run(
            self.async_sign(
                sub=sub,
                tid=tid,
                ttl=ttl,
                typ=typ,
                issuer=issuer,
                audience=audience,
                cert_thumbprint=cert_thumbprint,
                **extra,
            ),
        )

    async def async_sign_pair(
        self, *, sub: str, tid: str, cert_thumbprint: Optional[str] = None, **extra: Any
    ) -> Tuple[str, str]:
        access = await self.async_sign(
            sub=sub, tid=tid, cert_thumbprint=cert_thumbprint, **extra
        )
        refresh = await self.async_sign(
            sub=sub,
            tid=tid,
            ttl=_REFRESH_TTL,
            typ="refresh",
            cert_thumbprint=cert_thumbprint,
            **extra,
        )
        return access, refresh

    def sign_pair(
        self, *, sub: str, tid: str, cert_thumbprint: Optional[str] = None, **extra: Any
    ) -> Tuple[str, str]:
        return asyncio.run(
            self.async_sign_pair(
                sub=sub,
                tid=tid,
                cert_thumbprint=cert_thumbprint,
                **extra,
            ),
        )

    async def async_decode(
        self,
        token: str,
        verify_exp: bool = True,
        issuer: Optional[str] = None,
        audience: Optional[Iterable[str] | str] = None,
        cert_thumbprint: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            payload = await self._svc.verify(token, issuer=issuer, audience=audience)
        except InvalidKeyError as exc:
            raise InvalidTokenError("unable to resolve verification key") from exc
        if verify_exp:
            exp = payload.get("exp")
            if exp is not None and int(exp) < int(
                datetime.now(timezone.utc).timestamp()
            ):
                raise InvalidTokenError("token is expired")
        if settings.enable_rfc8705:
            if cert_thumbprint is None:
                raise ValueError(
                    "certificate thumbprint required for mTLS per RFC 8705",
                )
            validate_certificate_binding(payload, cert_thumbprint)
        if settings.enable_rfc9068:
            if issuer is None or audience is None:
                raise ValueError(
                    "issuer and audience required for JWT access tokens per RFC 9068",
                )
            from .rfc9068 import validate_rfc9068_claims

            validate_rfc9068_claims(payload, issuer=issuer, audience=audience)
        return payload

    def decode(
        self,
        token: str,
        verify_exp: bool = True,
        issuer: Optional[str] = None,
        audience: Optional[Iterable[str] | str] = None,
        cert_thumbprint: Optional[str] = None,
    ) -> Dict[str, Any]:
        return asyncio.run(
            self.async_decode(
                token,
                verify_exp=verify_exp,
                issuer=issuer,
                audience=audience,
                cert_thumbprint=cert_thumbprint,
            ),
        )

    def refresh(self, refresh_token: str) -> Tuple[str, str]:
        payload = self.decode(refresh_token)
        if payload.get("typ") != "refresh":
            raise ValueError("token is not a refresh token")
        base_claims = {
            k: v for k, v in payload.items() if k not in {"iat", "exp", "typ"}
        }
        return self.sign_pair(**base_claims)
