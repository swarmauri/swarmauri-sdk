"""Utilities and endpoint for OAuth 2.0 Dynamic Client Registration.

This module exposes a minimal in-memory client registry together with a
FastAPI router implementing the registration endpoint defined by
`RFC 7591 <https://www.rfc-editor.org/rfc/rfc7591>`_.  The feature can be
enabled or disabled via ``runtime_cfg.Settings.enable_rfc7591`` allowing
deployments to opt in as needed.
"""

from __future__ import annotations

import secrets
from typing import Dict, Final
from urllib.parse import urlparse

from ..deps import (
    APIRouter,
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    FastAPI,
    HTTPException,
    status,
    field_validator,
)

from ..runtime_cfg import settings

# In-memory registry of dynamically registered clients
_CLIENT_REGISTRY: Dict[str, dict] = {}

# FastAPI router for the registration endpoint
router = APIRouter()

# Public URL for the RFC specification
RFC7591_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7591"


class ClientMetadata(BaseModel):
    """Subset of RFC 7591 client metadata required for registration."""

    redirect_uris: list[AnyHttpUrl] = Field(..., min_length=1)
    grant_types: list[str] = Field(default_factory=lambda: ["authorization_code"])
    response_types: list[str] = Field(default_factory=lambda: ["code"])

    model_config = ConfigDict(extra="allow")

    @field_validator("redirect_uris")
    @classmethod
    def _validate_redirect_uris(cls, value: list[AnyHttpUrl]) -> list[AnyHttpUrl]:
        """Ensure redirect URIs use HTTPS except for localhost."""
        for uri in value:
            parsed = urlparse(str(uri))
            if parsed.scheme != "https" and parsed.hostname not in {
                "localhost",
                "127.0.0.1",
                "::1",
            }:
                raise ValueError("redirect URIs must use https scheme")
        return value


def register_client(metadata: dict, *, enabled: bool | None = None) -> dict:
    """Register a new OAuth client as described in RFC 7591.

    Parameters
    ----------
    metadata: dict
        Client metadata defined by RFC 7591 §2.
    enabled: bool | None
        Override global toggle for RFC 7591.

    Returns
    -------
    dict
        The stored client metadata including generated credentials.

    Raises
    ------
    RuntimeError
        If RFC 7591 support is disabled.
    """

    if enabled is None:
        enabled = settings.enable_rfc7591
    if not enabled:
        raise RuntimeError(f"RFC 7591 support is disabled: {RFC7591_SPEC_URL}")

    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)
    data = {"client_id": client_id, "client_secret": client_secret, **metadata}
    _CLIENT_REGISTRY[client_id] = data
    return data


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_client_endpoint(body: ClientMetadata) -> dict:
    """HTTP endpoint implementing OAuth 2.0 Dynamic Client Registration."""

    if not settings.enable_rfc7591:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "client registration disabled")

    return register_client(body.model_dump())


def get_client(client_id: str) -> dict | None:
    """Return metadata for *client_id* or ``None`` if unknown."""

    return _CLIENT_REGISTRY.get(client_id)


def reset_client_registry() -> None:
    """Clear the in-memory client registry (primarily for tests)."""

    _CLIENT_REGISTRY.clear()


def include_rfc7591(app: FastAPI) -> None:
    """Attach the RFC 7591 router to *app* if enabled."""

    if settings.enable_rfc7591 and not any(
        route.path == "/register" for route in app.routes
    ):
        app.include_router(router)


__all__ = [
    "register_client",
    "get_client",
    "reset_client_registry",
    "RFC7591_SPEC_URL",
    "register_client_endpoint",
    "include_rfc7591",
]
