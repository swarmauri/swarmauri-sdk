# AutoAPI

A high-leverage meta-framework that turns plain SQLAlchemy models into a fully-featured REST+RPC surface with near zero boiler plate.

## Terminology

- **Tenant** – a namespace used to group related resources.
- **Principal** – an owner of resources, such as an individual user or an organization.

## Features
- Unified invocation 
- Automated REST & RPC symmetry and parity
	- table creation instantiates routes and rpc methods
	- `transactional` adds routes and rpc methods
	- REST routes and RPC both invoke the `_runner._invoke()`
- Automated Request and Response schemas
- Default operations: create, read, update, delete, list, clear
- Extended operations: replace (put), bulk create/delete/update
- 6 Phase Hook Lifecycle
- Transactionals
- _RowBound hook providers
- phase-level hooks that can be wildcard or per-verb, per-model
- Automated route creation: rest paths or nested rest paths, rpc dispatch, healthz, methodz, hookz
- Support for AuthNProvider extensions


## Configuration Overview

### Table-Level
- `__autoapi_request_extras__` – verb-scoped virtual request fields.
- `__autoapi_response_extras__` – verb-scoped virtual response fields.
- `__autoapi_register_hooks__` – hook registration entry point.
- `__autoapi_nested_paths__` – nested REST path segments.
- `__autoapi_allow_anon__` – verbs permitted without auth.
- `__autoapi_owner_policy__` / `__autoapi_tenant_policy__` – server vs client field injection.
- `__autoapi_verb_aliases__` & `__autoapi_verb_alias_policy__` – custom verb names.

### Routing
- `__autoapi_nested_paths__` for hierarchical routing.
- `__autoapi_verb_aliases__` for custom verbs.
- `__autoapi_verb_alias_policy__` to scope alias application.

### Persistence
- Mixins such as `Upsertable`, `Bootstrappable`, `GUIDPk`, `Timestamped`.
- Policies `__autoapi_owner_policy__` and `__autoapi_tenant_policy__`.
- `transactional` decorator for atomic RPC + REST endpoints.

### Security
- Pluggable `AuthNProvider` interface.
- `__autoapi_allow_anon__` to permit anonymous access.

### Dependencies
- SQLAlchemy for ORM integration.
- Pydantic for schema generation.
- FastAPI for routing and dependency injection.

### Engine & Provider examples

```python
from autoapi.v3.engine.shortcuts import engine_spec, prov
from autoapi.v3.engine._engine import Engine, Provider

# Build an EngineSpec from a DSN string
spec = engine_spec("sqlite://:memory:")

# Or from keyword arguments
spec_pg = engine_spec(kind="postgres", async_=True, host="db", name="app_db")

# Lazy Provider from the spec
provider = prov(spec)            # same as Provider(spec)
with provider.session() as session:
    session.execute("SELECT 1")

# Engine façade wrapping a Provider
eng = Engine(spec_pg)
async with eng.asession() as session:
    await session.execute("SELECT 1")

# Direct Provider construction is also supported
provider_pg = Provider(spec_pg)
```

### Conformance rules

Downstream services **must** create database connections using
`autoapi.v3.engine.Engine` (or the helpers in
`autoapi.v3.engine.shortcuts`). Direct imports from
`sqlalchemy.ext.asyncio` like `create_async_engine`, `AsyncSession`, or
`async_sessionmaker` and hand-rolled `get_async_db` dependencies are not
allowed. Use the Engine's `get_db` generator for FastAPI dependencies:

```python
from fastapi import Depends
from autoapi.v3.engine import engine

DB_ENGINE = engine("sqlite+aiosqlite:///./app.db")

@app.get("/items")
async def handler(db=Depends(DB_ENGINE.get_db)):
    ...
```

### Attaching engine contexts

`engine_ctx` binds database configuration to different layers. It accepts a
DSN string, a mapping, an `EngineSpec`, a `Provider`, or an `Engine`. The
resolver chooses the most specific binding in the order
`op > table > api > app`.

#### Declarative bindings

```python
from types import SimpleNamespace
from autoapi.v3.engine.shortcuts import prov, engine

app = SimpleNamespace(db=prov(kind="sqlite", mode="memory"))
alt = SimpleNamespace(db=engine(kind="sqlite", mode="memory"))

class API:
    db = {"kind": "sqlite", "memory": True}

class Item:
    __tablename__ = "items"
    table_config = {"db": {"kind": "sqlite", "memory": True}}

async def create(payload, *, db=None):
    ...

create.__autoapi_engine_ctx__ = {
    "kind": "postgres",
    "async": True,
    "host": "db",
    "name": "op_db",
}
```

#### Decorative bindings

```python
from autoapi.v3.engine.decorators import engine_ctx
from autoapi.v3.engine.shortcuts import prov, engine

@engine_ctx(prov(kind="sqlite", mode="memory"))
class App:
    pass

@engine_ctx(engine(kind="sqlite", mode="memory"))
class DecoratedAPI:
    pass

@engine_ctx(kind="sqlite", mode="memory")
class DecoratedItem:
    __tablename__ = "items"

@engine_ctx(kind="postgres", async_=True, host="db", name="op_db")
async def decorated_create(payload, *, db=None):
    ...
```

### Column-level configurations

The following `col.info["autoapi"]` keys are recognized by AutoAPI and related packages:

| Configuration key | Description & examples | Packages using it |
| --- | --- | --- |
| `disable_on` | Excludes a field from specific verbs. The ApiKey digest hides the value on update and replace requests, and mixins such as `Ownable` and `TenantBound` add the same metadata when strict policies are chosen. Peagen's `Repository` model opts into these strict policies. | autoapi, peagen ORM |
| `write_only` | Marks a field so it can be written but never returned. Demonstrated in test models where a `secret` field is write-only. | autoapi (tests) |
| `read_only` | Keeps a field out of write verbs. Used for ApiKey digest and for GUID primary keys generated by `GUIDPk` (read-only on create). Auto-authn models inherit `GUIDPk`, so they inherit this metadata. | autoapi, auto-authn, peagen ORM |
| `default_factory` | Supplies a callable to generate default values. GUID primary keys use `uuid4` as a factory, and Peagen's `User` model exposes the same metadata. | autoapi, auto-authn, peagen ORM |
| `examples` | Provides example values for documentation or schema generation. Used widely in mixins (`tenant_id`, `user_id`, etc.) and explicitly in Peagen's `User.id` column. | autoapi, auto-authn, peagen ORM |
| `hybrid` | Enables hybrid properties in the schema. Demonstrated with a `full_name` hybrid property marked in tests. | autoapi (tests) |
| `py_type` | Specifies Python type for hybrids. Shown in tests where a computed field is declared as an `int`. | autoapi (tests) |


## Glossary
1. Tables
2. Schemas
3. Schema Overlays (Request Extras)
3. Phases
4. Phase Lifecycle
6. Request
7. Request Ctx
8. Default Flush
9. Core
10. Core_Raw