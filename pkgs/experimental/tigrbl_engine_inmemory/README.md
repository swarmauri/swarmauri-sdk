# tigrbl_engine_inmemory

![Tigrbl Branding](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

![PyPI - Downloads](https://img.shields.io/pypi/dm/tigrbl_engine_inmemory)
![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg?label=hits)
![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl_engine_inmemory)
![License](https://img.shields.io/pypi/l/tigrbl_engine_inmemory)
![Version](https://img.shields.io/pypi/v/tigrbl_engine_inmemory)

Process-local in-memory Tigrbl engine plugin with copy-on-write transaction sessions and relational-ish table APIs.

## Features

- Engine registration as `kind="inmemory"` via `tigrbl.engine` entry point.
- Snapshot-style transactional sessions (`begin`, `commit`, `rollback`).
- CRUD helper methods for table-based workflows.
- Sync and async session wrappers.
- Useful for local development, deterministic tests, and dependency-free demos.

## Installation

### uv

```bash
uv add tigrbl_engine_inmemory
```

### pip

```bash
pip install tigrbl_engine_inmemory
```

## Usage

```python
from tigrbl import engine_ctx

@engine_ctx({"kind": "inmemory", "namespace": "dev"})
def create_book(db, title: str):
    db.ensure_table("book", pk="id")
    return db.insert("book", {"title": title})
```
