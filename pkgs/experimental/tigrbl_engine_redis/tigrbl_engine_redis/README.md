![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_redis/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_redis/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_redis/tigrbl_engine_redis/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_redis/tigrbl_engine_redis.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_redis/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_redis/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_redis" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_redis/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_redis?label=tigrbl_engine_redis&color=green" alt="PyPI - tigrbl_engine_redis"/></a>
</p>
---

# tigrbl_engine_redis

A Redis engine plugin for **tigrbl**. This package registers a new engine kind
`"redis"` that tigrbl auto-discovers via the `tigrbl.engine` entry-point group.

> The engine handle and session class in this package are implemented as
> **subclasses of tigrbl's first-class objects** (see notes below).

## Installation

```bash
pip install tigrbl_engine_redis
```

## Usage

Once installed, refer to `kind="redis"` in your engine spec:

```python
from tigrbl.engine.engine_spec import EngineSpec

spec = EngineSpec(kind="redis", mapping={"url": "redis://localhost:6379/0"})
eng, make_session = spec.build()  # resolved through entry-points
s = make_session()                # returns a RedisSession (TigrblSessionBase subclass)
```

### What this package provides

- `RedisEngine` — a thin subclass of `tigrbl.engine.Engine` to satisfy the
  "first‑class engine" requirement. It stores connection parameters for
  inspection; tigrbl keeps it as the provider's engine handle.
- `RedisSession` — a concrete subclass of `tigrbl.session.TigrblSessionBase`
  that wraps a `redis.asyncio.Redis` client and implements the async
  transaction‑aware Tigrbl Session ABC.
- `redis_engine()` — the entry‑point builder used by tigrbl to materialize
  `(engine_handle, session_factory)`.

> tigrbl auto‑loads engine plugins on import (idempotent). See:
> `tigrbl.engine.__init__` (calls `load_engine_plugins()`), and
> `tigrbl.engine.plugins.load_engine_plugins()` which enumerates the `tigrbl.engine`
> entry‑point group and invokes each package's `register()` function.
