# tigrbl_engine_snowflake

**Tigrbl engine plugin for Snowflake**, auto-registered via the `tigrbl.engine` entry-point group.

## Install

```bash
pip install -e .
```

## Usage (inside Tigrbl)

```python
from tigrbl.engine import Engine
from tigrbl.engine.engine_spec import EngineSpec

# DSN (Snowflake SQLAlchemy URL)
spec = EngineSpec(kind="snowflake", dsn="snowflake://USER:PWD@ACCOUNT/DB/SCHEMA?warehouse=WH&role=ROLE")

# Or provide a mapping; the plugin builds the DSN
spec = EngineSpec(kind="snowflake", mapping={
    "account": "myacct-xy123",
    "user": "USER",
    "pwd": "PWD",
    "db": "DB",
    "schema": "PUBLIC",
    "warehouse": "COMPUTE_WH",
    "role": "SYSADMIN",
    "pool_size": 10,
    "max_overflow": 20
})

engine = Engine(spec)
with engine.session() as s:
    s.execute("SELECT CURRENT_ROLE()").all()
```

## Entry-point

Declared in `pyproject.toml`:

```toml
[project.entry-points."tigrbl.engine"]
snowflake = "tigrbl_engine_snowflake:register"
```
