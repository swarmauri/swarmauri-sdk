![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_inmemory/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_inmemory/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_inmemory/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_inmemory.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemory/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemory/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_inmemory" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemory/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_inmemory?label=tigrbl_engine_inmemory&color=green" alt="PyPI - tigrbl_engine_inmemory"/></a>
</p>
---

# tigrbl_engine_inmemory

![Tigrbl](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

![PyPI - Downloads](https://static.pepy.tech/badge/tigrbl_engine_inmemory/month)
![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
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
