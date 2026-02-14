# tigrbl_engine_dataframe

A Tigrbl engine plugin that provides a **DataFrame-backed** engine/session.

- **Native transactions** (`begin/commit/rollback`).
- **MVCC-style snapshots** for reads.
- Works with Tigrbl **core CRUD** via the small session surface.

## Install

```bash
pip install tigrbl_engine_dataframe
```

The plugin **auto-registers** via entry points under the group `tigrbl.engine`.

## Usage

```python
from tigrbl.engine.decorators import engine_ctx

# Bind by kind using the plugin's engine
@engine_ctx({"kind": "dataframe", "async": True, "tables": {"widgets": df}, "pks": {"widgets": "id"}})
class API:
    pass
```
