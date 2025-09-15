from tigrbl_auth.deps import build_engine
from .runtime_cfg import settings

if settings.pg_dsn_env or (settings.pg_host and settings.pg_db and settings.pg_user):
    dsn = settings.apg_dsn
else:
    dsn = "sqlite+aiosqlite:///./authn.db"

ENGINE = build_engine(dsn)
get_db = ENGINE.get_db

__all__ = ["ENGINE", "get_db", "dsn"]
