# peagen/runtime_cfg.py
from __future__ import annotations
import os, functools
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field, PostgresDsn, RedisDsn
from peagen._utils.config_loader import load_peagen_toml

class RuntimeSettings(BaseModel):
    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    # Postgres
    pg_dsn: PostgresDsn = Field(default="postgresql://user:pass@localhost:5342/db")

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
    if "REDIS_URL" in os.environ:
        raw["redis_url"] = os.environ["REDIS_URL"]
    if "PG_DSN" in os.environ:
        raw["pg_dsn"] = os.environ["PG_DSN"]

    return RuntimeSettings(**raw)
