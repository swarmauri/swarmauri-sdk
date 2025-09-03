from autoapi.v3.engine import engine as engine_factory

from .runtime_cfg import settings

if settings.pg_dsn_env or (settings.pg_host and settings.pg_db and settings.pg_user):
    dsn = settings.apg_dsn
else:
    dsn = "sqlite+aiosqlite:///./gateway.db"

engine = engine_factory(dsn)
sql_engine, _ = engine.raw()
