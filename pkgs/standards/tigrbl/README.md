# Tigrbl

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
- `__tigrbl_request_extras__` – verb-scoped virtual request fields.
- `__tigrbl_response_extras__` – verb-scoped virtual response fields.
- `__tigrbl_register_hooks__` – hook registration entry point.
- `__tigrbl_nested_paths__` – nested REST path segments.
- `__tigrbl_allow_anon__` – verbs permitted without auth.
- `__tigrbl_owner_policy__` / `__tigrbl_tenant_policy__` – server vs client field injection.
- `__tigrbl_verb_aliases__` & `__tigrbl_verb_alias_policy__` – custom verb names.

### Routing
- `__tigrbl_nested_paths__` for hierarchical routing.
- `__tigrbl_verb_aliases__` for custom verbs.
- `__tigrbl_verb_alias_policy__` to scope alias application.

### Persistence
- Mixins such as `Upsertable`, `Bootstrappable`, `GUIDPk`, `Timestamped`.
- Policies `__tigrbl_owner_policy__` and `__tigrbl_tenant_policy__`.
- `transactional` decorator for atomic RPC + REST endpoints.

### Security
- Pluggable `AuthNProvider` interface.
- `__tigrbl_allow_anon__` to permit anonymous access.

### Database Guards
Tigrbl executes each phase under database guards that temporarily replace
`commit` and `flush` on the SQLAlchemy session. Guards prevent writes or
commits outside their allowed phases and only permit commits when Tigrbl
owns the transaction. See the
[runtime documentation](tigrbl/v3/runtime/README.md#db-guards) for the full
matrix of phase policies.

### Dependencies
- SQLAlchemy for ORM integration.
- Pydantic for schema generation.
- FastAPI for routing and dependency injection.

### Engine & Provider examples

```python
from tigrbl.v3.engine.shortcuts import engine_spec, prov
from tigrbl.v3.engine._engine import Engine, Provider

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

### Attaching engine contexts

`engine_ctx` binds database configuration to different layers. It accepts a
DSN string, a mapping, an `EngineSpec`, a `Provider`, or an `Engine`. The
resolver chooses the most specific binding in the order
`op > table > api > app`.

#### Declarative bindings

```python
from types import SimpleNamespace
from tigrbl.v3.engine.shortcuts import prov, engine

app = SimpleNamespace(db=prov(kind="sqlite", mode="memory"))
alt = SimpleNamespace(db=engine(kind="sqlite", mode="memory"))

class API:
    db = {"kind": "sqlite", "memory": True}

class Item:
    __tablename__ = "items"
    table_config = {"db": {"kind": "sqlite", "memory": True}}

async def create(payload, *, db=None):
    ...

create.__tigrbl_engine_ctx__ = {
    "kind": "postgres",
    "async": True,
    "host": "db",
    "name": "op_db",
}
```

#### Decorative bindings

```python
from tigrbl.v3.engine.decorators import engine_ctx
from tigrbl.v3.engine.shortcuts import prov, engine

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