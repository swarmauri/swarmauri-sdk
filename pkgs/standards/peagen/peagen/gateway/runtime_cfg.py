# peagen/runtime_cfg.py
from __future__ import annotations
import os, functools
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field
from peagen._utils.config_loader import load_peagen_toml

class RuntimeSettings(BaseModel):
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    # Postgres
    pg_dsn: str = Field(default="postgresql://user:pass@localhost:5342/db")
    # Async Postgres
    apg_dsn: str = Field(default="postgresql+asyncpg://user:pass@localhost:5342/db")

    class Config:
        extra = "ignore"

@functools.lru_cache(maxsize=1)
def get_settings() -> RuntimeSettings:
    """
    Lazy-load `.peagen.toml`, overlay with env vars, validate.
    """
    cfg_path = Path.cwd() / ".peagen.toml"
    raw: Dict[str, Any] = {}
    if cfg_path.exists():
        raw = load_peagen_toml(cfg_path).get("runtime", {})   # e.g. [runtime.redis_url="…"]
    
    # ---- ENV overrides (if defined) ----

    # ───────── Redis connection ─────────
    # Default each field to the corresponding os.environ[...] (or fallback literal).
    redis_host: Optional[str] = Field(default=os.environ.get("REDIS_HOST"))
    redis_port: int = Field(default=int(os.environ.get("REDIS_PORT", "6379")))
    redis_db: int = Field(default=int(os.environ.get("REDIS_DB", "0")))
    redis_password: Optional[str] = Field(default=os.environ.get("REDIS_PASSWORD"))


    # ───────── Postgres results-backend ─────────
    pg_host: Optional[str] = Field(default=os.environ.get("PG_HOST"))
    pg_port: int = Field(default=int(os.environ.get("PG_PORT", "5342")))
    pg_db: Optional[str] = Field(default=os.environ.get("PG_DB"))
    pg_user: Optional[str] = Field(default=os.environ.get("PG_USER"))
    pg_pass: Optional[str] = Field(default=os.environ.get("PG_PASS"))


    
    raw["redis_url"] = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

    raw["pg_dsn"] = (
            f"postgresql://{pg_user}:{pg_pass}"
            f"@{pg_host}:{pg_port}/{pg_db}"
        )

    raw["apg_dsn"] = (
            f"postgresql+asyncpg://{pg_user}:{pg_pass}"
            f"@{pg_host}:{pg_port}/{pg_db}"
        )

    return RuntimeSettings(**raw)
