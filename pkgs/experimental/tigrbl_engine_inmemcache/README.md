# tigrbl_engine_inmemcache

![Tigrbl](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

![PyPI - Downloads](https://static.pepy.tech/badge/tigrbl_engine_inmemcache/month)
![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)
![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl_engine_inmemcache)
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
