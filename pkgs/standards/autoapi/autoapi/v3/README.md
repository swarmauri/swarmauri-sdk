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

## Column-Level Configuration

AutoAPI v3 models declare their database and API behavior through
`ColumnSpec` helpers exposed in `autoapi.v3.column`.  Use `acol` for
persisted columns and `vcol` for wire-only virtual values.  Each column
can combine three optional specs:

- `S` (`StorageSpec`) – database shape such as types, keys, indexes, and
  other SQLAlchemy column arguments.
- `F` (`FieldSpec`) – Python and schema metadata including validation
  constraints or example values.
- `IO` (`IOSpec`) – inbound/outbound exposure settings, aliases,
  sensitivity flags, and filtering/sorting capabilities.

Example:

```python
from autoapi.v3.column import acol, vcol, F, S, IO

class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = acol(storage=S(primary_key=True))
    name: Mapped[str] = acol(
        field=F(constraints={"max_length": 50}),
        storage=S(nullable=False, index=True),
        io=IO(
            in_verbs=("create", "update"),
            out_verbs=("read", "list"),
            sortable=True,
        ),
    )
    checksum: Mapped[str] = vcol(
        field=F(),
        io=IO(out_verbs=("read",)),
        read_producer=lambda obj, ctx: f"{obj.name}:{obj.id}",
    )
```

Virtual columns like `checksum` use a `read_producer` (or `producer`)
function to compute values on the fly.  Leveraging these specs keeps
column behavior declarative and consistent across the ORM, schema
generation, and runtime I/O.
