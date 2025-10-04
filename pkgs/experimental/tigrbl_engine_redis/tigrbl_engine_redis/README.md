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
