# settings.py

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

# ─── Load environment variables from a .env file (if present) ─────────────────────
load_dotenv()


class Settings(BaseSettings):
    # ─────── Redis connection ───────
    redis_url_env: Optional[str] = Field(default=os.environ.get("REDIS_URL"))
    redis_host: Optional[str] = Field(default=os.environ.get("REDIS_HOST"))
    redis_port: int = Field(default=int(os.environ.get("REDIS_PORT", "6379")))
    redis_db: int = Field(default=int(os.environ.get("REDIS_DB", "0")))
    redis_password: Optional[str] = Field(default=os.environ.get("REDIS_PASSWORD"))

    @property
    def redis_url(self) -> str:
        """Return a valid Redis connection URL."""
        if self.redis_url_env:
            return self.redis_url_env
        host = self.redis_host or "localhost"
        cred = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{cred}{host}:{self.redis_port}/{self.redis_db}"

    # ─────── Postgres results-backend ───────
    pg_dsn_env: Optional[str] = Field(
        default=os.environ.get("POSTGRES_URL") or os.environ.get("PG_DSN")
    )
    pg_host: Optional[str] = Field(default=os.environ.get("PG_HOST"))
    pg_port: int = Field(default=int(os.environ.get("PG_PORT", "5432")))
    pg_db: Optional[str] = Field(default=os.environ.get("PG_DB"))
    pg_user: Optional[str] = Field(default=os.environ.get("PG_USER"))
    pg_pass: Optional[str] = Field(default=os.environ.get("PG_PASS"))
    async_fallback_db: Optional[str] = Field(
        default=os.environ.get("ASYNC_FALLBACK_DB")
    )

    @property
    def pg_dsn(self) -> str:
        if self.pg_dsn_env:
            return self.pg_dsn_env
        if self.pg_host and self.pg_db and self.pg_user:
            return (
                f"postgresql://{self.pg_user}:{self.pg_pass}"
                f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
            )
        return ""

    @property
    def apg_dsn(self) -> str:
        dsn = self.pg_dsn
        if dsn.startswith("postgresql://"):
            return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
        if not dsn and self.async_fallback_db:
            return self.async_fallback_db
        return dsn

    # ─────── Other global settings ───────
    jwt_secret: str = Field(os.environ.get("JWT_SECRET", "insecure-dev-secret"))
    log_level: str = Field(os.environ.get("LOG_LEVEL", "INFO"))
    rfc8707_enabled: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8707", "0") == "1"
    )
    enable_rfc8705: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8705", "false").lower()
        in {"1", "true", "yes"}
    )
    enable_rfc7636: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7636", "true").lower()
        in {"1", "true", "yes"},
        description="Enable Proof Key for Code Exchange per RFC 7636",
    )
    enforce_rfc8252: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENFORCE_RFC8252", "true").lower()
        in {"1", "true", "yes"},
        description="Validate redirect URIs according to RFC 8252",
    )
    enable_rfc7662: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7662", "false").lower()
        in {"1", "true", "yes"}
    )
    enable_dpop: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_DPOP", "0") in {"1", "true", "True"}
    )
    enable_rfc9396: bool = Field(default=os.environ.get("ENABLE_RFC9396", "0") == "1")
    enable_rfc7009: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7009", "false").lower()
        in {"1", "true", "yes"}
    )
    enable_rfc8414: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8414", "true").lower()
        in {"1", "true", "yes"},
        description="Enable OAuth 2.0 Authorization Server Metadata per RFC 8414",
    )
    enable_rfc6750: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC6750", "true").lower()
        in {"1", "true", "yes"},
        description="Enable Bearer Token Usage per RFC 6750",
    )
    enable_rfc6750_query: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC6750_QUERY", "false").lower()
        in {"1", "true", "yes"},
        description="Allow access_token as URI query parameter per RFC 6750 §2.3",
    )
    enable_rfc6750_form: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC6750_FORM", "false").lower()
        in {"1", "true", "yes"},
        description=(
            "Allow access_token in application/x-www-form-urlencoded bodies per RFC 6750 §2.2"
        ),
    )
    enable_rfc6749: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC6749", "true").lower()
        in {"1", "true", "yes"},
        description="Enforce core OAuth 2.0 error handling per RFC 6749",
    )
    enable_rfc8628: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8628", "true").lower()
        in {"1", "true", "yes"},
        description="Enable Device Authorization Grant per RFC 8628",
    )

    model_config = SettingsConfigDict(env_file=None)


settings = Settings()
