# settings.py

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# ─── Load environment variables from a .env file (if present) ─────────────────────────
load_dotenv()


class Settings(BaseSettings):
    # ───────── Redis connection ─────────
    # Default each field to the corresponding os.environ[...] (or fallback literal).
    redis_host: str = Field(os.environ.get("REDIS_HOST"))
    redis_port: int = Field(int(os.environ.get("REDIS_PORT", "6379")))
    redis_db: int = Field(int(os.environ.get("REDIS_DB", "0")))
    redis_password: str = Field(os.environ["REDIS_PASSWORD"])

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # ───────── Postgres results-backend ─────────
    pg_host: str = Field(os.environ.get("PG_HOST"))
    pg_port: int = Field(int(os.environ.get("PG_PORT", "5342")))
    pg_db: str = Field(os.environ["PG_DB"])
    pg_user: str = Field(os.environ["PG_USER"])
    pg_pass: str = Field(os.environ["PG_PASS"])

    @property
    def pg_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.pg_user}:{self.pg_pass}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )

    # ───────── Other global settings ─────────
    jwt_secret: str = Field(os.environ.get("JWT_SECRET", "insecure-dev-secret"))
    log_level: str = Field(os.environ.get("LOG_LEVEL", "INFO"))

    class Config:
        # No env_file needed since we already called load_dotenv().
        pass


settings = Settings()
