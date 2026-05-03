![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_snowflake/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_snowflake/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_snowflake/tigrbl_engine_snowflake/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_snowflake/tigrbl_engine_snowflake.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_snowflake/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_snowflake" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_snowflake/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_snowflake" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_snowflake/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_snowflake?label=tigrbl_engine_snowflake&color=green" alt="PyPI - tigrbl_engine_snowflake"/></a>
</p>
---

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
