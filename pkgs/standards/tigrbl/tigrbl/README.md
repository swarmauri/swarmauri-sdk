# Tigrbl v3 Engine Conformance

Applications built on Tigrbl v3 **must** create database engines and sessions
through the `tigrbl.engine` package. Direct imports from
`sqlalchemy.ext.asyncio`—such as `AsyncSession`, `create_async_engine`, or
`async_sessionmaker`—are **not permitted**.

Instead, construct an engine via `Engine` or the helper `engine()` function:

```python
from tigrbl.engine import engine

DB = engine("sqlite+aiosqlite:///./app.db")
app = TigrblApp(engine=DB)
```

Use `DB.get_db` as the FastAPI dependency for acquiring sessions and avoid
exporting custom `get_async_db` helpers.

These rules apply to all first-party applications, including
`tigrbl_kms`, `tigrbl_auth`, and the `peagen` gateway.

## Column-Level Configuration

Tigrbl v3 models declare their database and API behavior through
`ColumnSpec` helpers exposed in `tigrbl.column`.  Use `acol` for
persisted columns and `vcol` for wire-only virtual values.  Each column
can combine three optional specs:

- `S` (`StorageSpec`) – database shape such as types, keys, indexes, and
  other SQLAlchemy column arguments.
- `F` (`FieldSpec`) – Python and schema metadata including validation
  constraints or example values.
- `IO` (`IOSpec`) – inbound/outbound exposure settings, aliases,
  sensitivity flags, and filtering/sorting capabilities.

For a deeper look at these helpers, see [column/README.md](column/README.md).

Example:

```python
from tigrbl.column import acol, vcol, F, S, IO

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

## 🧩 First-Class Object Pattern

Tigrbl v3 organizes its core building blocks with a common structure:

- 📄 **Spec** – declarative metadata describing behavior.
- 🏛️ **Class** – runtime implementation of the object.
- 🎀 **Decorators** – syntactic sugar for declaring features.
- ⚡️ **Shortcuts** – handy constructors for common setups.

Some objects also expose optional helpers:

- 🫺 **Collect** – gathers declarations from a class hierarchy.
- 🧩 **Resolver** – finalizes configuration from specs.
- 🎧 **Builder** – assembles complex runtime resources.

| Object | 📄 Spec | 🏛️ Class | 🎀 Decorators | ⚡️ Shortcuts | 🫺 Collect | 🧩 Resolver | 🎧 Builder |
|--------|----------|-----------|----------------|----------------|----------------|----------------|----------------|
| Column | `column_spec.py` | `_column.py` | — | `shortcuts.py` | `collect.py` | — | — |
| Engine | `engine_spec.py` | `_engine.py` | `decorators.py` | `shortcuts.py` | `collect.py` | `resolver.py` | `builders.py` |
| Op | `types.py` | `_op.py` | `decorators.py` | — | `collect.py` | — | — |
| API | `api_spec.py` | `_api.py` | — | `shortcuts.py` | — | — | — |
| App | `app_spec.py` | `_app.py` | — | `shortcuts.py` | — | — | — |
| Table | `table_spec.py` | `_table.py` | — | `shortcuts.py` | — | — | — |

This pattern keeps the system modular and predictable, making it easy to
discover related modules for any given concept.
