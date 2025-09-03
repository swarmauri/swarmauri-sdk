from autoapi.v3.engine import engine as make_engine

from .runtime_cfg import settings


if settings.pg_dsn_env or (settings.pg_host and settings.pg_db and settings.pg_user):
    dsn = settings.apg_dsn
else:
    # Fallback to a local SQLite database when Postgres settings are missing
    dsn = "sqlite+aiosqlite:///./authn.db"

ENGINE = make_engine(dsn)
