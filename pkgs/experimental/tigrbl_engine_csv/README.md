![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_engine_csv/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_csv?label=tigrbl_engine_csv&color=green" alt="PyPI - tigrbl_engine_csv"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_csv/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_engine_csv" alt="PyPI - Downloads"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_csv/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_csv" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_csv/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_csv" alt="PyPI - License"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_csv/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_csv.svg"/>
    </a>
</p>

# tigrbl_engine_csv

A tigrbl engine plugin that registers `kind="csv"` where each CSV is a single-table database-like object.

## Features

- Registers a `csv` engine through the `tigrbl.engine` entry-point group.
- Treats one CSV file as one database-like table.
- Provides a first-class `CsvSession` (subclass of `TigrblSessionBase`) backed by transactional DataFrame semantics.

## Installation

### uv

```bash
uv add tigrbl_engine_csv
```

### pip

```bash
pip install tigrbl_engine_csv
```

## Usage

```python
from tigrbl.engine import EngineSpec

spec = EngineSpec(
    kind="csv",
    mapping={"path": "./users.csv", "table": "users", "pk": "id"},
)
provider = spec.provider()
engine, session_factory = provider.build()

session = session_factory()
print(session.table())
print(session.query("age >= 21"))
session.close()
```
