![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_clickhouse/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_clickhouse/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_clickhouse/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_clickhouse.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_clickhouse/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_clickhouse/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_clickhouse" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_clickhouse/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_clickhouse?label=tigrbl_engine_clickhouse&color=green" alt="PyPI - tigrbl_engine_clickhouse"/></a>
</p>
---

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
- `ClickHouseEngine` subclasses `tigrbl._concrete._engine.Engine`.
- `ClickHouseSession` subclasses `tigrbl.session.base.TigrblSessionBase` and uses `clickhouse_connect`.
