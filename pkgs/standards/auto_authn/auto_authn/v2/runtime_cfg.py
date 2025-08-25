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
        in {"1", "true", "yes"},
        description=("Enable OAuth 2.0 Mutual-TLS client authentication per RFC 8705"),
    )
    enable_rfc8725: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8725", "false").lower()
        in {"1", "true", "yes"},
        description=("Enable JSON Web Token Best Current Practices per RFC 8725"),
    )
    enable_rfc7636: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7636", "true").lower()
        in {"1", "true", "yes"},
        description="Enable Proof Key for Code Exchange per RFC 7636",
    )
    enable_rfc7638: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7638", "true").lower()
        in {"1", "true", "yes"},
        description="Enable JWK Thumbprint per RFC 7638",
    )
    enable_rfc7800: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7800", "false").lower()
        in {"1", "true", "yes"},
        description="Enable Proof-of-Possession semantics per RFC 7800",
    )
    enforce_rfc8252: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENFORCE_RFC8252", "true").lower()
        in {"1", "true", "yes"},
        description="Validate redirect URIs according to RFC 8252",
    )
    enable_rfc8291: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8291", "false").lower()
        in {"1", "true", "yes"},
        description="Enable Message Encryption for Web Push per RFC 8291",
    )
    enable_rfc8812: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8812", "false").lower()
        in {"1", "true", "yes"},
        description=("Enable WebAuthn algorithm registrations per RFC 8812",),
    )
    enable_rfc8037: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8037", "true").lower()
        in {"1", "true", "yes"},
        description="Enable CFRG EdDSA algorithms per RFC 8037",
    )
    enable_rfc8176: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8176", "true").lower()
        in {"1", "true", "yes"},
        description="Enable Authentication Method Reference validation per RFC 8176",
    )
    enable_rfc7662: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7662", "false").lower()
        in {"1", "true", "yes"}
    )
    enable_rfc9449: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC9449", "true").lower()
        in {"1", "true", "yes"},
        description=(
            "Enable OAuth 2.0 Demonstrating Proof of Possession (DPoP) per RFC 9449"
        ),
    )

    @property
    def enable_dpop(self) -> bool:
        """Alias for backward compatibility."""
        return self.enable_rfc9449

    enable_rfc9396: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC9396", "0").lower()
        in {"1", "true", "yes"},
        description=("Enable OAuth 2.0 Rich Authorization Requests per RFC 9396"),
    )
    enable_rfc9101: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC9101", "false").lower()
        in {"1", "true", "yes"},
        description="Enable JWT-Secured Authorization Request per RFC 9101",
    )
    enable_rfc7009: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7009", "false").lower()
        in {"1", "true", "yes"},
        description="Enable OAuth 2.0 Token Revocation per RFC 7009",
    )
    enable_rfc8414: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8414", "true").lower()
        in {"1", "true", "yes"},
        description="Enable OAuth 2.0 Authorization Server Metadata per RFC 8414",
    )
    enable_rfc9207: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC9207", "false").lower()
        in {"1", "true", "yes"},
        description="Enable Authorization Server Issuer Identification per RFC 9207",
    )
    enable_rfc8523: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8523", "false").lower()
        in {"1", "true", "yes"},
        description="Enable JWT Profile for OAuth 2.0 Client Authentication per RFC 8523",
    )
    enable_rfc7952: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7952", "false").lower()
        in {"1", "true", "yes"},
        description="Enable Security Event Token (SET) per RFC 7952",
    )
    enable_rfc8693: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8693", "false").lower()
        in {"1", "true", "yes"},
        description="Enable OAuth 2.0 Token Exchange per RFC 8693",
    )
    enable_rfc8932: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC8932", "false").lower()
        in {"1", "true", "yes"},
        description="Enable Enhanced Authorization Server Metadata per RFC 8932",
    )
    enable_rfc9126: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC9126", "false").lower()
        in {"1", "true", "yes"},
        description="Enable Pushed Authorization Requests per RFC 9126",
    )
    enable_rfc9068: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC9068", "false").lower()
        in {"1", "true", "yes"},
        description="Enable JWT Profile for OAuth 2.0 Access Tokens per RFC 9068",
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
    enable_rfc7515: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7515", "true").lower()
        in {"1", "true", "yes"},
        description="Enable JSON Web Signature per RFC 7515",
    )
    enable_rfc7516: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7516", "true").lower()
        in {"1", "true", "yes"},
        description="Enable JSON Web Encryption per RFC 7516",
    )
    enable_rfc7517: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7517", "true").lower()
        in {"1", "true", "yes"},
        description="Enable JSON Web Key per RFC 7517",
    )
    enable_rfc7518: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7518", "true").lower()
        in {"1", "true", "yes"},
        description="Enable JSON Web Algorithms per RFC 7518",
    )
    enable_rfc7519: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7519", "true").lower()
        in {"1", "true", "yes"},
        description="Enable JSON Web Token per RFC 7519",
    )
    enable_rfc7520: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7520", "true").lower()
        in {"1", "true", "yes"},
        description="Enable JOSE examples per RFC 7520",
    )
    enable_rfc7591: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7591", "false").lower()
        in {"1", "true", "yes"},
        description="Enable OAuth 2.0 Dynamic Client Registration per RFC 7591",
    )
    enable_rfc7592: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7592", "false").lower()
        in {"1", "true", "yes"},
        description="Enable OAuth 2.0 Client Registration Management per RFC 7592",
    )
    enable_rfc7521: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7521", "true").lower()
        in {"1", "true", "yes"},
        description="Enable Assertion Framework for OAuth 2.0 per RFC 7521",
    )
    enable_rfc7523: bool = Field(
        default=os.environ.get("AUTO_AUTHN_ENABLE_RFC7523", "true").lower()
        in {"1", "true", "yes"},
        description="Enable JWT Profile for OAuth 2.0 per RFC 7523",
    )

    model_config = SettingsConfigDict(env_file=None)


settings = Settings()
