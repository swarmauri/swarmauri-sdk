# tigrbl_engine_clickhouse

A ClickHouse engine plugin for **tigrbl**. This package registers a new engine
kind `"clickhouse"` that tigrbl auto‑discovers via the `tigrbl.engine` entry‑point group.

> Both classes in this package are **subclasses of tigrbl's first‑class objects**.

## Installation

```bash
pip install tigrbl_engine_clickhouse
```

## Usage

```python
from tigrbl.engine.engine_spec import EngineSpec

spec = EngineSpec(kind="clickhouse", mapping={
    "host": "localhost",
    "port": 8123,
    "username": "default",
    "password": "",
    "database": "default",
    "secure": False,
})
eng, make_session = spec.build()   # resolved via entry-points
s = make_session()                 # returns a ClickHouseSession (TigrblSessionBase subclass)

# Example query
rows = await s._execute_impl("SELECT 1 AS x")
print(rows)
await s.close()
```

### How it’s wired

- `pyproject.toml` declares the entry‑point:
  ```toml
  [project.entry-points."tigrbl.engine"]
  clickhouse = "tigrbl_engine_clickhouse:register"
  ```
- `register()` (in `__init__.py`) calls `tigrbl.engine.registry.register_engine("clickhouse", clickhouse_engine)`.
- `ClickHouseEngine` subclasses `tigrbl.engine._engine.Engine`.
- `ClickHouseSession` subclasses `tigrbl.session.base.TigrblSessionBase` and uses `clickhouse_connect`.
