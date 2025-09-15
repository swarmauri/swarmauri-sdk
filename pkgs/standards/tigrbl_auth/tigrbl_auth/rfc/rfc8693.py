"""RFC 8693 - OAuth 2.0 Token Exchange.

This module provides functionality for OAuth 2.0 Token Exchange as defined
in RFC 8693. Token exchange allows clients to exchange one type of token
for another, enabling scenarios like impersonation, delegation, and
token format conversion.
See RFC 8693: https://www.rfc-editor.org/rfc/rfc8693
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from fastapi import APIRouter, FastAPI, Form, HTTPException, Request, Header, status

from .. import runtime_cfg
from .rfc7519 import decode_jwt
from ..jwtoken import JWTCoder
from .rfc9449_dpop import verify_proof

RFC8693_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8693"

# Token Exchange Grant Type
TOKEN_EXCHANGE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"

router = APIRouter()


def include_rfc8693(app: FastAPI) -> None:
    """Attach the RFC 8693 router to *app* if enabled."""

    if runtime_cfg.settings.enable_rfc8693 and not any(
        route.path == "/token/exchange" for route in app.routes
    ):
        app.include_router(router)


# Standard Token Type URIs per RFC 8693 Section 3
class TokenType(Enum):
    """Standard token type URIs for token exchange."""

    ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"
    REFRESH_TOKEN = "urn:ietf:params:oauth:token-type:refresh_token"
    ID_TOKEN = "urn:ietf:params:oauth:token-type:id_token"
    SAML1 = "urn:ietf:params:oauth:token-type:saml1"
    SAML2 = "urn:ietf:params:oauth:token-type:saml2"
    JWT = "urn:ietf:params:oauth:token-type:jwt"


class TokenExchangeRequest:
    """Represents a token exchange request per RFC 8693."""

    def __init__(
        self,
        grant_type: str,
        subject_token: str,
        subject_token_type: str,
        *,
        actor_token: Optional[str] = None,
        actor_token_type: Optional[str] = None,
        resource: Optional[Union[str, List[str]]] = None,
        audience: Optional[Union[str, List[str]]] = None,
        scope: Optional[str] = None,
        requested_token_type: Optional[str] = None,
    ):
        """Initialize a token exchange request.

        Args:
            grant_type: Must be TOKEN_EXCHANGE_GRANT_TYPE
            subject_token: The token representing the subject
            subject_token_type: Type URI of the subject token
            actor_token: Optional token representing the actor
            actor_token_type: Type URI of the actor token (required if actor_token provided)
            resource: Optional target resource(s)
            audience: Optional target audience(s)
            scope: Optional requested scope
            requested_token_type: Optional requested token type
        """
        self.grant_type = grant_type
        self.subject_token = subject_token
        self.subject_token_type = subject_token_type
        self.actor_token = actor_token
        self.actor_token_type = actor_token_type
        self.resource = resource
        self.audience = audience
        self.scope = scope
        self.requested_token_type = requested_token_type

    def validate(self) -> None:
        """Validate the token exchange request per RFC 8693."""
        if self.grant_type != TOKEN_EXCHANGE_GRANT_TYPE:
            raise ValueError(f"Invalid grant_type: {self.grant_type}")

        if not self.subject_token:
            raise ValueError("subject_token is required")

        if not self.subject_token_type:
            raise ValueError("subject_token_type is required")

        if self.actor_token and not self.actor_token_type:
            raise ValueError(
                "actor_token_type is required when actor_token is provided"
            )

        if self.actor_token_type and not self.actor_token:
            raise ValueError(
                "actor_token is required when actor_token_type is provided"
            )


class TokenExchangeResponse:
    """Represents a token exchange response per RFC 8693."""

    def __init__(
        self,
        access_token: str,
        token_type: str = "Bearer",
        *,
        expires_in: Optional[int] = None,
        refresh_token: Optional[str] = None,
        scope: Optional[str] = None,
        issued_token_type: Optional[str] = None,
    ):
        """Initialize a token exchange response.

        Args:
            access_token: The issued access token
            token_type: Token type (typically "Bearer")
            expires_in: Token lifetime in seconds
            refresh_token: Optional refresh token
            scope: Granted scope
            issued_token_type: Type of the issued token
        """
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.scope = scope
        self.issued_token_type = issued_token_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for JSON serialization."""
        result = {
            "access_token": self.access_token,
            "token_type": self.token_type,
        }

        if self.expires_in is not None:
            result["expires_in"] = self.expires_in
        if self.refresh_token:
            result["refresh_token"] = self.refresh_token
        if self.scope:
            result["scope"] = self.scope
        if self.issued_token_type:
            result["issued_token_type"] = self.issued_token_type

        return result


def validate_token_exchange_request(
    grant_type: str, subject_token: str, subject_token_type: str, **kwargs
) -> TokenExchangeRequest:
    """Validate and create a TokenExchangeRequest.

    Args:
        grant_type: The grant type
        subject_token: The subject token
        subject_token_type: The subject token type
        **kwargs: Additional optional parameters

    Returns:
        Validated TokenExchangeRequest instance

    Raises:
        RuntimeError: If RFC 8693 support is disabled
        ValueError: If validation fails
    """
    if not runtime_cfg.settings.enable_rfc8693:
        raise RuntimeError("RFC 8693 support disabled")

    request = TokenExchangeRequest(
        grant_type=grant_type,
        subject_token=subject_token,
        subject_token_type=subject_token_type,
        **kwargs,
    )

    request.validate()
    return request


def validate_subject_token(token: str, token_type: str) -> Dict[str, Any]:
    """Validate a subject token based on its type.

    Args:
        token: The token to validate
        token_type: The token type URI

    Returns:
        Token claims/metadata

    Raises:
        ValueError: If token validation fails
    """
    if token_type in (TokenType.ACCESS_TOKEN.value, TokenType.JWT.value):
        try:
            return decode_jwt(token)
        except Exception as e:
            raise ValueError(f"Invalid JWT token: {e}")
    elif token_type == TokenType.REFRESH_TOKEN.value:
        # For refresh tokens, we might need different validation
        # This is a placeholder - implement based on your token format
        return {"token_type": "refresh_token", "value": token}
    else:
        # For other token types, basic validation
        if not token.strip():
            raise ValueError("Empty token")
        return {"token_type": token_type, "value": token}


def exchange_token(
    request: TokenExchangeRequest,
    *,
    issuer: str,
    client_id: Optional[str] = None,
    jkt: str | None = None,
) -> TokenExchangeResponse:
    """Perform token exchange per RFC 8693.

    Args:
        request: Validated token exchange request
        issuer: Token issuer
        client_id: Optional client identifier

    Returns:
        TokenExchangeResponse with the new token

    Raises:
        RuntimeError: If RFC 8693 support is disabled
        ValueError: If token exchange fails
    """
    if not runtime_cfg.settings.enable_rfc8693:
        raise RuntimeError("RFC 8693 support disabled")

    # Validate subject token
    subject_claims = validate_subject_token(
        request.subject_token, request.subject_token_type
    )

    # Validate actor token if provided
    if request.actor_token and request.actor_token_type:
        validate_subject_token(request.actor_token, request.actor_token_type)

    # Create new token based on request
    jwt_coder = JWTCoder.default()

    # Extract subject from original token
    subject_id = subject_claims.get("sub", "unknown")
    tenant_id = subject_claims.get("tid", "default")

    # Determine scope - use requested scope or inherit from subject token
    scope = request.scope or subject_claims.get("scope", "")

    # Create new access token
    extra_claims: Dict[str, Any] = {}
    if jkt:
        extra_claims["cnf"] = {"jkt": jkt}
    access_token = jwt_coder.sign(
        sub=subject_id,
        tid=tenant_id,
        scopes=scope.split() if scope else [],
        aud=request.audience,
        **extra_claims,
    )

    # Determine issued token type
    issued_token_type = request.requested_token_type or TokenType.ACCESS_TOKEN.value

    return TokenExchangeResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=3600,  # 1 hour default
        scope=scope,
        issued_token_type=issued_token_type,
    )


@router.post("/token/exchange")
async def token_exchange_endpoint(
    request: Request,
    grant_type: str = Form(...),
    subject_token: str = Form(...),
    subject_token_type: str = Form(...),
    actor_token: str | None = Form(None),
    actor_token_type: str | None = Form(None),
    audience: str | None = Form(None),
    scope: str | None = Form(None),
    dpop: str | None = Header(None, alias="DPoP"),
):
    """RFC 8693 token exchange endpoint."""

    if not runtime_cfg.settings.enable_rfc8693:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "token exchange disabled")

    jkt: str | None = None
    if dpop:
        try:
            jkt = verify_proof(dpop, request.method, str(request.url))
        except ValueError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    token_request = validate_token_exchange_request(
        grant_type=grant_type,
        subject_token=subject_token,
        subject_token_type=subject_token_type,
        actor_token=actor_token,
        actor_token_type=actor_token_type,
        audience=audience,
        scope=scope,
    )
    response = exchange_token(token_request, issuer="token-exchange", jkt=jkt)
    return response.to_dict()


def create_impersonation_token(
    subject_token: str,
    actor_token: str,
    *,
    audience: Optional[str] = None,
    scope: Optional[str] = None,
) -> TokenExchangeResponse:
    """Create an impersonation token per RFC 8693 Section 2.1.

    Args:
        subject_token: Token of the user being impersonated
        actor_token: Token of the user performing impersonation
        audience: Target audience for the token
        scope: Requested scope

    Returns:
        TokenExchangeResponse with impersonation token
    """
    if not runtime_cfg.settings.enable_rfc8693:
        raise RuntimeError("RFC 8693 support disabled")

    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token=subject_token,
        subject_token_type=TokenType.ACCESS_TOKEN.value,
        actor_token=actor_token,
        actor_token_type=TokenType.ACCESS_TOKEN.value,
        audience=audience,
        scope=scope,
    )

    request.validate()
    return exchange_token(request, issuer="impersonation-service")


def create_delegation_token(
    subject_token: str,
    *,
    audience: Optional[str] = None,
    scope: Optional[str] = None,
) -> TokenExchangeResponse:
    """Create a delegation token per RFC 8693 Section 2.2.

    Args:
        subject_token: Token to be delegated
        audience: Target audience for the token
        scope: Requested scope (typically narrower than original)

    Returns:
        TokenExchangeResponse with delegation token
    """
    if not runtime_cfg.settings.enable_rfc8693:
        raise RuntimeError("RFC 8693 support disabled")

    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token=subject_token,
        subject_token_type=TokenType.ACCESS_TOKEN.value,
        audience=audience,
        scope=scope,
    )

    request.validate()
    return exchange_token(request, issuer="delegation-service")


__all__ = [
    "TokenExchangeRequest",
    "TokenExchangeResponse",
    "TokenType",
    "validate_token_exchange_request",
    "validate_subject_token",
    "exchange_token",
    "create_impersonation_token",
    "create_delegation_token",
    "TOKEN_EXCHANGE_GRANT_TYPE",
    "RFC8693_SPEC_URL",
    "include_rfc8693",
    "router",
]
