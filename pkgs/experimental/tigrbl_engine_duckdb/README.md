![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_duckdb/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_duckdb/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_duckdb/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_duckdb.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_duckdb/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_duckdb" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_duckdb/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_duckdb" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_duckdb/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_duckdb?label=tigrbl_engine_duckdb&color=green" alt="PyPI - tigrbl_engine_duckdb"/></a>
</p>
---

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
