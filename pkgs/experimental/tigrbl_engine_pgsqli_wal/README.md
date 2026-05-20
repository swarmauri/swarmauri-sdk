![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_pgsqli_wal/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_pgsqli_wal/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_pgsqli_wal/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_pgsqli_wal.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pgsqli_wal/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pgsqli_wal/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_pgsqli_wal" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pgsqli_wal/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_pgsqli_wal?label=tigrbl_engine_pgsqli_wal&color=green" alt="PyPI - tigrbl_engine_pgsqli_wal"/></a>
</p>
---

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
