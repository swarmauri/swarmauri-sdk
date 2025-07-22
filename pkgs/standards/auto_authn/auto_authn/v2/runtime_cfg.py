# settings.py

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

# ─── Load environment variables from a .env file (if present) ─────────────────────────
load_dotenv()


class Settings(BaseSettings):
    # ───────── Redis connection ─────────
    # Default each field to the corresponding os.environ[...] (or fallback literal).
    redis_host: Optional[str] = Field(default=os.environ.get("REDIS_HOST"))
    redis_port: int = Field(default=int(os.environ.get("REDIS_PORT", "6379")))
    redis_db: int = Field(default=int(os.environ.get("REDIS_DB", "0")))
    redis_password: Optional[str] = Field(default=os.environ.get("REDIS_PASSWORD"))

    @property
    def redis_url(self) -> str:
        """Return a valid Redis connection URL."""
        host = self.redis_host or "localhost"
        cred = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{cred}{host}:{self.redis_port}/{self.redis_db}"

    # ───────── Postgres results-backend ─────────
    pg_dsn_env: Optional[str] = Field(default=os.environ.get("PG_DSN"))
    pg_host: Optional[str] = Field(default=os.environ.get("PG_HOST"))
    pg_port: int = Field(default=int(os.environ.get("PG_PORT", "5432")))
    pg_db: Optional[str] = Field(default=os.environ.get("PG_DB"))
    pg_user: Optional[str] = Field(default=os.environ.get("PG_USER"))
    pg_pass: Optional[str] = Field(default=os.environ.get("PG_PASS"))

    @property
    def pg_dsn(self) -> str:
        if self.pg_dsn_env:
            return self.pg_dsn_env
        return (
            f"postgresql://{self.pg_user}:{self.pg_pass}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )

    @property
    def apg_dsn(self) -> str:
        dsn = self.pg_dsn
        if dsn.startswith("postgresql://"):
            return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
        return dsn

    # ───────── Other global settings ─────────
    jwt_secret: str = Field(os.environ.get("JWT_SECRET", "insecure-dev-secret"))
    log_level: str = Field(os.environ.get("LOG_LEVEL", "INFO"))

    model_config = SettingsConfigDict(env_file=None)


settings = Settings()
