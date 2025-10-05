# tigrbl_engine_rediscachethrough

A Redis/Postgres **cache-through** engine plugin for **tigrbl**.

- Uses Postgres (via tigrbl's built-in SQLAlchemy builders) for persistence.
- Uses Redis for read-through/write-through caching of simple lookups.
- Auto-discovers via entry point group `tigrbl.engine`.

## Install

```bash
pip install -e .
```

## Usage

```python
from tigrbl.engine import EngineSpec

spec = EngineSpec(kind="rediscachethrough", url="postgresql://user:pwd@host:5432/db",
                  extras={"redis_url": "redis://localhost:6379/0", "cache_ttl_sec": 60})
provider = spec.to_provider()
engine_handles, session_factory = provider.build()

sess = session_factory()  # CacheThroughSession (subclass of TigrblSessionBase)
# e.g., await sess.execute(text("SELECT 1"))
```

