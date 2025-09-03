from autoapi.v3.engine import engine as build_engine, engine_spec
from .runtime_cfg import settings

if settings.pg_dsn_env:
    CFG = settings.pg_dsn_env
elif settings.pg_host and settings.pg_db and settings.pg_user:
    CFG = engine_spec(
        kind="postgres",
        async_=True,
        host=settings.pg_host,
        port=settings.pg_port,
        name=settings.pg_db,
        user=settings.pg_user,
        pwd=settings.pg_pass,
    )
else:
    CFG = "sqlite+aiosqlite:///./gateway.db"

ENGINE = build_engine(CFG)
get_db = ENGINE.get_db

__all__ = ["ENGINE", "get_db", "CFG"]
