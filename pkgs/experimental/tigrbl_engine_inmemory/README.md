# tigrbl_engine_inmemory

![Tigrbl](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

![PyPI - Downloads](https://img.shields.io/pypi/dm/tigrbl_engine_inmemory)
![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)
![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl_engine_inmemory)
![License](https://img.shields.io/pypi/l/tigrbl_engine_inmemory)
![Version](https://img.shields.io/pypi/v/tigrbl_engine_inmemory)

Pure-stdlib, process-local transactional in-memory engine plugin for Tigrbl.

## Features

- Copy-on-write snapshot transactions with `begin`, `commit`, and `rollback`.
- Table-scoped CRUD API (`insert`, `get`, `update`, `delete`, `query`).
- Lightweight per-operation session creation.
- Thread-safe commit path for multi-thread use inside a process.
- Entry-point registration under `tigrbl.engine` with `kind="inmemory"`.

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
    db.ensure_table("books", pk="id")
    row = db.insert("books", {"title": title})
    db.commit()
    return row
```
