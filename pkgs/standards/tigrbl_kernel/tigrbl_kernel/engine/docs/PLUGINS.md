
# Tigrbl Engine Plugins

Tigrbl supports external engine kinds via an entry-point group: `tigrbl.engine`.

An external package registers itself by exposing a `register()` function and
declaring an entry point:

```toml
[project.entry-points."tigrbl.engine"]
duckdb = "tigrbl_engine_duckdb.plugin:register"
```

Inside `register()` call:

```python
from tigrbl.engine.registry import register_engine
from .builder import duckdb_engine, duckdb_capabilities

def register():
    register_engine("duckdb", duckdb_engine, duckdb_capabilities)
```

At runtime, `EngineSpec(kind="duckdb")` will look up the registration and use
the external builder or raise a helpful `RuntimeError` if the plugin is not
installed.


## Capabilities / supports()

External engines should expose a capabilities callable when registering:

```python
from tigrbl.engine.registry import register_engine

def my_engine_builder(...): ...
def my_engine_capabilities(**kw):
    # Return a dict describing what the engine supports
    return {
        "transactional": True,
        "isolation_levels": {"read_committed","serializable"},
        "read_only_enforced": True,
        "async_native": False,
        "engine": "myengine",
    }

def register():
    register_engine("myengine", my_engine_builder, capabilities=my_engine_capabilities)
```
