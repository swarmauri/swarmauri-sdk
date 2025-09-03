# AutoAPI v3 Engine Conformance

Services that rely on AutoAPI v3 must construct database engines via the
`autoapi.v3.engine` helpers rather than importing SQLAlchemy's async engine
utilities directly. In particular, applications **must not** import
`create_async_engine`, `AsyncSession`, or `async_sessionmaker` from
`sqlalchemy.ext.asyncio`.

Instead, build an engine using the `engine()` shortcut or the `Engine` class
and obtain sessions from the returned instance:

```python
from autoapi.v3.engine import engine

eng = engine("sqlite+aiosqlite:///./app.db")
app = AutoApp(engine=eng)
```

FastAPI dependencies should consume `eng.get_db` directly and should **not**
define custom `get_async_db` helpers.
