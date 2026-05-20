![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_inmemcache/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_inmemcache/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_inmemcache/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_inmemcache.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemcache/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemcache/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_inmemcache" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemcache/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_inmemcache?label=tigrbl_engine_inmemcache&color=green" alt="PyPI - tigrbl_engine_inmemcache"/></a>
</p>
---

# tigrbl_engine_inmemcache

![Tigrbl](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

![PyPI - Downloads](https://static.pepy.tech/badge/tigrbl_engine_inmemcache/month)
![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
![License](https://img.shields.io/pypi/l/tigrbl_engine_inmemcache)
![Version](https://img.shields.io/pypi/v/tigrbl_engine_inmemcache)

Pure-stdlib, process-local TTL/LRU cache engine plugin for Tigrbl.

## Features

- Basic key/value session API: `get`, `set`, `delete`, `clear`.
- TTL support per-key and default TTL per engine instance.
- LRU eviction using `OrderedDict` when `max_items` is exceeded.
- Thread-safe cache operations for in-process concurrent access.
- Entry-point registration under `tigrbl.engine` with `kind="inmemcache"`.

## Installation

### uv

```bash
uv add tigrbl_engine_inmemcache
```

### pip

```bash
pip install tigrbl_engine_inmemcache
```

## Usage

```python
from tigrbl import engine_ctx

@engine_ctx({"kind": "inmemcache", "max_items": 200_000, "default_ttl_s": 60})
def handler(db, user_id: str):
    key = f"user:{user_id}"
    cached = db.get(key)
    if cached is not None:
        return cached
    payload = {"user_id": user_id, "computed": True}
    db.set(key, payload, ttl_s=30)
    return payload
```
