# tigrbl_engine_inmemcache

![Tigrbl Branding](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

![PyPI - Downloads](https://img.shields.io/pypi/dm/tigrbl_engine_inmemcache)
![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg?label=hits)
![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl_engine_inmemcache)
![License](https://img.shields.io/pypi/l/tigrbl_engine_inmemcache)
![Version](https://img.shields.io/pypi/v/tigrbl_engine_inmemcache)

Process-local in-memory cache engine for Tigrbl with configurable max size, TTL support, and LRU eviction.

## Features

- Engine registration as `kind="inmemcache"` via plugin entry point.
- Fast in-memory key/value reads and writes.
- Optional TTL expiration and lazy cleanup.
- LRU-style eviction when max item count is exceeded.
- Sync and async session wrappers for provider lifecycle compatibility.

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

@engine_ctx({"kind": "inmemcache", "max_items": 250_000, "default_ttl_s": 60})
def handler(db, user_id: str):
    key = f"user:{user_id}"
    cached = db.get(key)
    if cached is not None:
        return cached
    value = {"user_id": user_id, "computed": True}
    db.set(key, value, ttl_s=30)
    return value
```
