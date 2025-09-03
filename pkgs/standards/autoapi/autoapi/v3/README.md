# AutoAPI v3 Engine Conformance

Applications built on AutoAPI v3 **must** create database engines and sessions
through the `autoapi.v3.engine` package. Direct imports from
`sqlalchemy.ext.asyncio`—such as `AsyncSession`, `create_async_engine`, or
`async_sessionmaker`—are **not permitted**.

Instead, construct an engine via `Engine` or the helper `engine()` function:

```python
from autoapi.v3.engine import engine

DB = engine("sqlite+aiosqlite:///./app.db")
app = AutoApp(engine=DB)
```

Use `DB.get_db` as the FastAPI dependency for acquiring sessions and avoid
exporting custom `get_async_db` helpers.

These rules apply to all first-party applications, including
`auto_kms`, `auto_authn`, and the `peagen` gateway.
