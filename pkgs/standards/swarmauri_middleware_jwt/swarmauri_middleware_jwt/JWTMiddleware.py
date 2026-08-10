"""ASGI middleware adapter for Bearer JWT authentication."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable, Iterable
from typing import Any

from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_core.middlewares.IMiddleware import (
    ASGIApp,
    ReceiveCallable,
    Scope,
    SendCallable,
)
from swarmauri_signing_jws import JwsSignerVerifier
from swarmauri_tokens_jwt import JWTClaimsValidator

from .BearerTokenExtractor import BearerTokenError, BearerTokenExtractor

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "JWTMiddleware")
class JWTMiddleware(MiddlewareBase, ComponentBase):
    """Authenticate compact HMAC JWT Bearer tokens for ASGI applications."""

    def __init__(
        self,
        secret_key: str | bytes,
        algorithm: str = "HS256",
        *,
        issuer: str | Iterable[str] | None = None,
        audience: str | Iterable[str] | None = None,
        required_claims: Iterable[str] = (),
        required_scopes: Iterable[str] = (),
        required_roles: Iterable[str] = (),
        leeway_s: int = 0,
        verify_exp: bool = True,
        state_attribute: str = "jwt_payload",
        claims_validator: JWTClaimsValidator | None = None,
        token_extractor: BearerTokenExtractor | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        secret_length = len(
            secret_key.encode("utf-8")
            if isinstance(secret_key, str)
            else secret_key
        )
        if secret_length < 32:
            raise ValueError(
                "HMAC secret must be at least 256 bits (32 bytes)"
            )
        self.secret_key = secret_key
        self.algorithm = JWAAlg(algorithm)
        if self.algorithm not in {JWAAlg.HS256, JWAAlg.HS384, JWAAlg.HS512}:
            raise ValueError(
                "JWTMiddleware secret_key supports HMAC algorithms only"
            )
        self.state_attribute = state_attribute
        self.claims_validator = claims_validator or JWTClaimsValidator(
            required_claims=required_claims,
            issuer=issuer,
            audience=audience,
            leeway_s=leeway_s,
            verify_exp=verify_exp,
            required_scopes=required_scopes,
            required_roles=required_roles,
        )
        self.token_extractor = token_extractor or BearerTokenExtractor()
        self._jws = JwsSignerVerifier()
        self._asgi_adapter = BaseHTTPMiddleware(
            self.app, dispatch=self.dispatch
        )

    def bind(self, app: ASGIApp) -> None:
        """Bind an ASGI application without requiring FastAPI."""

        super().bind(app)
        self._asgi_adapter = BaseHTTPMiddleware(
            self.app, dispatch=self.dispatch
        )

    async def __call__(
        self,
        scope: Scope,
        receive: ReceiveCallable,
        send: SendCallable,
    ) -> None:
        """Serve the Starlette-compatible ASGI middleware adapter."""

        try:
            await self._asgi_adapter(scope, receive, send)
        except HTTPException as exc:
            response = JSONResponse(
                {"detail": exc.detail}, status_code=exc.status_code
            )
            await response(scope, receive, send)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Any]],
    ) -> Any:
        """Authenticate and attach validated claims to the request state."""

        try:
            token = self.token_extractor.extract(request.headers)
            claims = await self.verify_token_async(token)
        except (
            BearerTokenError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            logger.warning("JWT authentication failed: %s", exc)
            raise HTTPException(
                status_code=401, detail="Invalid JWT credential"
            ) from exc

        setattr(request.state, self.state_attribute, claims)
        return await call_next(request)

    async def verify_token_async(self, token: str) -> dict[str, Any]:
        """Verify a compact JWS and validate its JWT claims asynchronously."""

        result = await self._jws.verify_compact(
            token,
            hmac_keys=[
                {
                    "kind": "raw",
                    "key": self.secret_key,
                    "alg": self.algorithm.value,
                }
            ],
            alg_allowlist=[self.algorithm],
        )
        claims = json.loads(result.payload.decode("utf-8"))
        if not isinstance(claims, dict):
            raise ValueError("JWT payload must be a JSON object")
        return self.claims_validator.validate(claims)

    def verify_token(self, token: str) -> dict[str, Any]:
        """Synchronously verify a token when no event loop is running."""

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.verify_token_async(token))
        raise RuntimeError("Use verify_token_async() from asynchronous code")
