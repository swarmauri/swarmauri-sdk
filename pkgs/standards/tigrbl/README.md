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

## Built-in Verbs

Tigrbl exposes a canonical set of operations that surface as both REST
and RPC endpoints. The table below summarizes the default REST routes,
RPC methods, arity, and the expected input and output shapes for each
verb. `{resource}` stands for the collection path and `{id}` is the
primary key placeholder.

| Verb | REST route | RPC method | Arity | Input type | Output type |
|------|------------|------------|-------|------------|-------------|
| `create` | `POST /{resource}` | `Model.create` | collection | dict | dict |
| `read` | `GET /{resource}/{id}` | `Model.read` | member | – | dict |
| `update` | `PATCH /{resource}/{id}` | `Model.update` | member | dict | dict |
| `replace` | `PUT /{resource}/{id}` | `Model.replace` | member | dict | dict |
| `merge` | `PATCH /{resource}/{id}` | `Model.merge` | member | dict | dict |
| `delete` | `DELETE /{resource}/{id}` | `Model.delete` | member | – | dict |
| `list` | `GET /{resource}` | `Model.list` | collection | dict | array |
| `clear` | `DELETE /{resource}` | `Model.clear` | collection | dict | dict |
| `bulk_create` | `POST /{resource}` | `Model.bulk_create` | collection | array | array |
| `bulk_update` | `PATCH /{resource}` | `Model.bulk_update` | collection | array | array |
| `bulk_replace` | `PUT /{resource}` | `Model.bulk_replace` | collection | array | array |
| `bulk_merge` | `PATCH /{resource}` | `Model.bulk_merge` | collection | array | array |
| `bulk_delete` | `DELETE /{resource}` | `Model.bulk_delete` | collection | dict | dict |
| `bulk_read` | – | – | – | – | – |

### Update, Merge, and Replace

`update` applies a shallow PATCH: only the supplied fields change and
missing fields are left untouched. `merge` performs a deep merge with
upsert semantics—if the target row is absent it is created, and nested
mapping fields are merged rather than replaced. `replace` follows PUT
semantics, overwriting the entire record and nulling any omitted
attributes.

### Verb Overrides

Because `create` and `bulk_create` share the same collection `POST`
route, enabling `bulk_create` removes the REST `create` endpoint; the
`Model.create` RPC method remains available. Likewise, `bulk_delete`
supersedes `clear` by claiming the collection `DELETE` route. Only one
of each conflicting pair can be exposed at a time. Other verbs coexist
without conflict because they operate on distinct paths or HTTP
methods.

## Phase Lifecycle

Tigrbl operations execute through a fixed sequence of phases. Hook chains can
attach handlers at any phase to customize behavior or enforce policy.

| Phase | Description |
|-------|-------------|
| `PRE_TX_BEGIN` | Pre-transaction checks before a database session is used. |
| `START_TX` | Open a new transaction when one is not already active. |
| `PRE_HANDLER` | Validate the request and prepare resources for the handler. |
| `HANDLER` | Execute the core operation logic within the transaction. |
| `POST_HANDLER` | Post-processing while still inside the transaction. |
| `PRE_COMMIT` | Final verification before committing; writes are frozen. |
| `END_TX` | Commit and close the transaction. |
| `POST_COMMIT` | Steps that run after commit but before the response is returned. |
| `POST_RESPONSE` | Fire-and-forget work after the response has been sent. |
| `ON_ERROR` | Fallback error handler when no phase-specific chain matches. |
| `ON_PRE_TX_BEGIN_ERROR` | Handle errors raised during `PRE_TX_BEGIN`. |
| `ON_START_TX_ERROR` | Handle errors raised during `START_TX`. |
| `ON_PRE_HANDLER_ERROR` | Handle errors raised during `PRE_HANDLER`. |
| `ON_HANDLER_ERROR` | Handle errors raised during `HANDLER`. |
| `ON_POST_HANDLER_ERROR` | Handle errors raised during `POST_HANDLER`. |
| `ON_PRE_COMMIT_ERROR` | Handle errors raised during `PRE_COMMIT`. |
| `ON_END_TX_ERROR` | Handle errors raised during `END_TX`. |
| `ON_POST_COMMIT_ERROR` | Handle errors raised during `POST_COMMIT`. |
| `ON_POST_RESPONSE_ERROR` | Handle errors raised during `POST_RESPONSE`. |
| `ON_ROLLBACK` | Run when the transaction rolls back to perform cleanup. |

## Hooks

Hooks allow you to plug custom logic into any phase of a verb. Use the
`hook_ctx` decorator to declare context-only hooks:

```python
from tigrbl.v3 import Base, hook_ctx

class Item(Base):
    __tablename__ = "items"

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def validate(cls, ctx):
        if ctx["request"].payload.get("name") == "bad":
            raise ValueError("invalid name")
```

The function runs during the `PRE_HANDLER` phase of `create`. The
`ctx` mapping provides request and response objects, a database session,
and values from earlier hooks.

Hooks can also be registered imperatively:

```python
async def audit(ctx):
    ...

class Item(Base):
    __tigrbl_hooks__ = {"delete": {"POST_COMMIT": [audit]}}
```

Running apps expose a `/system/hookz` route that lists all registered
hooks.

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