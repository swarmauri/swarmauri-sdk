# tigrbl_engine_pgsqli_wal

**Tigrbl engine plugin providing two engines:**

- `postgres_wal` — PostgreSQL via SQLAlchemy + psycopg3
- `sqlite_wal` — SQLite with WAL mode enabled via connection PRAGMAs

The package **auto-registers** with Tigrbl through the `tigrbl.engine` entry-point group.

## Install

```bash
pip install -e .
```

## Usage (inside Tigrbl)

```python
from tigrbl.engine import Engine
from tigrbl.engine.engine_spec import EngineSpec

# PostgreSQL (DSN or mapping)
spec = EngineSpec(kind="postgres_wal", dsn="postgresql+psycopg://user:pwd@host:5432/db?application_name=tigrbl")

# Or with mapping (the plugin builds the URL)
spec = EngineSpec(kind="postgres_wal", mapping={
  "host": "127.0.0.1", "port": 5432, "user": "user", "pwd": "pwd", "db": "db",
  "application_name": "tigrbl", "pool_size": 10, "max_overflow": 20
})

# SQLite (file path required for WAL)
spec = EngineSpec(kind="sqlite_wal", mapping={"path": "/path/to/db.sqlite", "pool_size": 5})

engine = Engine(spec)
with engine.session() as s:
    s.execute("select 1").all()
```

> Notes:
> - PostgreSQL WAL is a server feature; this plugin tunes connection/session parameters only.
> - SQLite WAL is enabled via `PRAGMA journal_mode=WAL` on each new connection.
