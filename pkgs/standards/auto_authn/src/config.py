"""
auth_authn_idp.config
~~~~~~~~~~~~~~~~~~~~~
Environment‑driven configuration for the Auth + AuthN OIDC provider.

Usage
-----
    from auth_authn_idp.config import settings

    async_engine = create_async_engine(settings.database_url, pool_size=...)
    redis = redis.asyncio.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List, Optional

from pydantic import (
    AmqpDsn,
    BaseModel,
    Field,
    HttpUrl,
    PostgresDsn,
    ValidationError,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class _JWKSConfig(BaseModel):
    """
    JWKS configuration stored on disk.

    By default we generate one RSA key per tenant at runtime and cache it in the DB,
    but a static path can be supplied for air‑gapped deployments.
    """

    path: Optional[Path] = Field(
        default=None,
        description="Optional path to a *static* JSON file containing the JWKS for the whole provider.",
    )
    refresh_seconds: int = Field(
        default=86_400,
        ge=300,
        description="If `path` is set, reload the JWKS every N seconds to pick up manual rotations.",
    )


class Settings(BaseSettings):
    # --------------------------------------------------------------------- #
    # Core service metadata
    # --------------------------------------------------------------------- #
    project_name: str = Field("auth_authn", description="Name used in logs & metrics.")
    environment: str = Field(
        "dev", description="Deployment environment string (dev / staging / prod)."
    )
    log_level: str = Field("INFO", description="Python logging / structlog level.")

    # --------------------------------------------------------------------- #
    # Network / bind addresses
    # --------------------------------------------------------------------- #
    host: str = Field("0.0.0.0")
    port: int = Field(8000, ge=1, le=65_535)
    public_url: HttpUrl | None = Field(
        default=None,
        description="Fully qualified URL clients see (e.g. https://login.example.com). "
        "If unset we compute it from host+port but HTTPS redirects will be wrong.",
    )

    cors_origins: List[HttpUrl] = Field(
        default_factory=list,
        description="Allowed origins for browser‑based RPs (comma‑separated list in env var).",
    )

    # --------------------------------------------------------------------- #
    # Persistence back‑ends
    # --------------------------------------------------------------------- #
    database_url: PostgresDsn | str = Field(
        "sqlite+aiosqlite:///./auth_authn.db",
        description="Async SQLAlchemy URL.  Prefer Postgres in production.",
    )
    redis_url: AmqpDsn | str = Field(
        "redis://localhost:6379/0", description="Redis URL for pub/sub sessions."
    )

    # --------------------------------------------------------------------- #
    # Crypto / signing
    # --------------------------------------------------------------------- #
    jwks: _JWKSConfig = Field(default_factory=_JWKSConfig)

    # The symmetric key used by pyoidc for session cookies (NOT for tokens!)
    session_sym_key: str = Field(
        "ChangeMeNow123456", min_length=16, description="AES‑128/256 key for cookie crypto."
    )

    # --------------------------------------------------------------------- #
    # Security & throttling
    # --------------------------------------------------------------------- #
    rate_limit_per_min: int = Field(
        120, description="Global unauthenticated request limit per IP."
    )
    allowed_clock_skew: int = Field(
        120,
        ge=0,
        description="How many seconds of skew to tolerate when validating ID‑token `iat/exp`.",
    )

    # --------------------------------------------------------------------- #
    # Pydantic settings
    # --------------------------------------------------------------------- #
    model_config = SettingsConfigDict(
        env_prefix="AUTH_AUTHN_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --------------------------------------------------------------------- #
    # Validators
    # --------------------------------------------------------------------- #

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v: str | List[str]) -> List[str]:
        """
        Allow comma‑separated CORS lists in ENV:
            AUTH_AUTHN_CORS_ORIGINS=https://foo,https://bar
        """
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @field_validator("public_url")
    @classmethod
    def _ensure_public_url(cls, v: HttpUrl | None, info: Any) -> HttpUrl | None:
        """
        If `public_url` is missing but we're in production we *must* abort,
        otherwise OIDC discovery endpoints will advertise wrong host names.
        """
        env = info.data.get("environment", "dev")
        if v is None and env == "prod":
            raise ValueError(
                "`public_url` is mandatory in prod to generate correct issuer URLs."
            )
        return v


# Global singleton – import this instead of re‑parsing all settings repeatedly
try:
    settings = Settings()  # noqa: F401
except ValidationError as exc:  # pragma: no cover
    # Immediate feedback on boot‑time misconfiguration
    print("💥 auth_authn configuration error:\n", exc, file=os.sys.stderr)
    raise
