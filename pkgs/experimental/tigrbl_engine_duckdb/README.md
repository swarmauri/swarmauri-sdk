# tigrbl_engine_duckdb

DuckDB engine extension for **Tigrbl**. This package registers the `duckdb`
engine kind with Tigrbl’s engine registry via entry points.

## Install

```bash
pip install tigrbl_engine_duckdb
```

## Use

After installing, you can bind DuckDB using `engine_ctx`:

```python
from tigrbl.engine.decorators import engine_ctx
from tigrbl.session.decorators import session_ctx

@engine_ctx({"kind": "duckdb", "path": "./data/app.duckdb",
             "pragmas": {"memory_limit": "2GB"}})
@session_ctx({"isolation": "repeatable_read"})
class AnalyticsAPI:
    pass
```

No import of this package is required in your app; Tigrbl auto-loads the
plugin via entry points on import.
