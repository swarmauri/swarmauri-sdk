"""Middleware for verifying HTTP signatures."""

import base64
import hashlib
import hmac
import logging
from typing import Any, Callable, Literal, Optional

from fastapi import HTTPException, Request
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "HttpSigMiddleware")
class HttpSigMiddleware(MiddlewareBase, ComponentBase):
    """Verify HTTP signatures on incoming requests.

    This middleware validates an HMAC-SHA256 signature included in request
    headers. The signature is computed over the request body using a shared
    secret key.

    Attributes:
        type: Literal["HttpSigMiddleware"] = "HttpSigMiddleware"
        secret_key: str -- Shared secret used for HMAC calculation
        header_name: str -- Header containing the signature (default ``X-Signature``)
    """

    type: Literal["HttpSigMiddleware"] = "HttpSigMiddleware"
    secret_key: Optional[str] = None
    header_name: Optional[str] = "X-Signature"
    logger: logging.Logger = Field(default_factory=lambda: logger, exclude=True)

    def __init__(self, secret_key: str, header_name: str = "X-Signature", **kwargs: Any) -> None:
        """Initialize the middleware with a secret key and header name."""
        super().__init__(**kwargs)
        self.secret_key = secret_key
        self.header_name = header_name
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Dispatch the request after verifying the signature.

        Args:
            request: The incoming request object.
            call_next: Callable that invokes the next middleware.

        Returns:
            The response returned by the next middleware.

        Raises:
            HTTPException: If the signature header is missing or invalid.
        """
        signature = request.headers.get(self.header_name)
        if not signature:
            self.logger.warning("Missing signature header")
            raise HTTPException(status_code=401, detail="Missing signature")

        body = await request.body()
        expected = base64.b64encode(
            hmac.new(self.secret_key.encode(), body, hashlib.sha256).digest()
        ).decode()

        if not hmac.compare_digest(signature, expected):
            self.logger.warning("Invalid HTTP signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

        return await call_next(request)
