"""
auth_authn_idp.config
=====================
Environment-driven configuration for the Auth + AuthN Identity-Provider.

All variables are prefixed **AUTH_AUTHN_*** in the process environment.
"""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import List, Optional

from pydantic import (
    AmqpDsn,
    BaseModel,
    Field,
    HttpUrl,
    PostgresDsn,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# --------------------------------------------------------------------------- #
# Top-level constants used by api_keys.py before Settings is instantiated     #
# --------------------------------------------------------------------------- #
API_KEY_MIN_TTL: int = int(secrets.choice(range(7, 91)))  # default 7-90 days
API_KEY_MAX_TTL: int = int(secrets.choice(range(7, 91)))
API_KEY_HASH_SECRET: str = secrets.token_hex(16)

# --------------------------------------------------------------------------- #
# Optional JWKS file-based config                                             #
# --------------------------------------------------------------------------- #


class _JWKSConfig(BaseModel):
    """
    When running in air-gapped mode you may mount a static JWKS JSON file.
    """

    path: Optional[Path] = Field(
        default=None,
        description="Absolute path to a provider-wide JWKS JSON file.",
    )
    refresh_seconds: int = Field(
        86_400,
        ge=300,
        description="Reload interval for static JWKS on disk.",
    )


# --------------------------------------------------------------------------- #
# Main settings                                                               #
# --------------------------------------------------------------------------- #
class Settings(BaseSettings):
    # --------------------------------------------------------------------- #
    # Core
    # --------------------------------------------------------------------- #
    project_name: str = Field("auth_authn")
    environment: str = Field("dev", description="dev / staging / prod")
    log_level: str = Field("INFO")

    # --------------------------------------------------------------------- #
    # Bind + public URLs
    # --------------------------------------------------------------------- #
    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    public_url: Optional[HttpUrl] = Field(
        default=None,
        description="External base URL (e.g. https://login.example.com). "
        "Required in prod for correct issuer/discovery documents.",
    )

    cors_origins: List[HttpUrl] = Field(
        default_factory=list,
        description="Comma-separated list of browser origins.",
    )

    # --------------------------------------------------------------------- #
    # Persistence
    # --------------------------------------------------------------------- #
    database_url: PostgresDsn | str = Field(
        "sqlite+aiosqlite:///./auth_authn.db", description="SQLAlchemy async URL."
    )
    redis_url: AmqpDsn | str = Field("redis://localhost:6379/0")

    # --------------------------------------------------------------------- #
    # Crypto
    # --------------------------------------------------------------------- #
    jwks: _JWKSConfig = Field(default_factory=_JWKSConfig)
    session_sym_key: str = Field(
        "ChangeMeNow_32chars!", min_length=16, description="AES-key for cookies."
    )
    jwt_audience: Optional[str] = Field(
        default=None,
        description="Expected `aud` in inbound Bearer JWTs. "
        "Unset → audience verification disabled.",
    )

    # --------------------------------------------------------------------- #
    # Security / throttling
    # --------------------------------------------------------------------- #
    rate_limit_per_min: int = Field(120, ge=30)
    allowed_clock_skew: int = Field(120, ge=0)

    # API-key guardrails
    api_key_min_ttl: int = Field(API_KEY_MIN_TTL, ge=1, le=API_KEY_MAX_TTL)
    api_key_max_ttl: int = Field(API_KEY_MAX_TTL, ge=7, le=365)
    api_key_hash_secret: str = Field(API_KEY_HASH_SECRET)

    # --------------------------------------------------------------------- #
    # Pydantic config
    # --------------------------------------------------------------------- #
    model_config = SettingsConfigDict(
        env_prefix="AUTH_AUTHN_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------ #
    # Validators
    # ------------------------------------------------------------------ #
    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v: str | List[str]) -> List[str]:  # noqa: D401
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @field_validator("public_url")
    @classmethod
    def _mandatory_public_url(cls, v: Optional[HttpUrl], info):  # noqa: D401
        if v is None and info.data.get("environment") == "prod":
            raise ValueError("`public_url` is required in prod")
        return v


# --------------------------------------------------------------------------- #
# Singleton – import `settings` everywhere                                    #
# --------------------------------------------------------------------------- #
settings = Settings()
