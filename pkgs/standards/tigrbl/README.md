![Tigrbl Logo](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/dm/tigrbl" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl.svg"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/l/tigrbl" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/v/tigrbl?label=tigrbl&color=green" alt="PyPI - tigrbl"/></a>
</p>

---

# Tigrbl 🐅🐂
A high-leverage ASGI meta-framework that turns plain SQLAlchemy models into a fully-featured REST+RPC surface with near-zero boilerplate. 🚀

## Features ✨

- ⚡ Zero-boilerplate CRUD for SQLAlchemy models
- 🔌 Unified REST and RPC endpoints from a single definition
- 🪝 Hookable phase system for deep customization
- 🧩 Pluggable engine and provider abstractions
- 🚀 Built as an ASGI-native framework with Pydantic-powered schema generation

## Terminology 📚

- **Tenant** 🏢 – a namespace used to group related resources.
- **Principal** 👤 – an owner of resources, such as an individual user or an organization.
- **Resource** 📦 – a logical collection of data or functionality exposed by the API.
- **Engine** ⚙️ – the database connection and transaction manager backing a resource.
- **Model / Table** 🧱 – the ORM or database representation of a resource's records.
- **Column** 📏 – a field on a model that maps to a table column.
- **Operation** 🛠️ – a verb-driven action executed against a resource.
- **Hook** 🪝 – a callback that runs during a phase to customize behavior.
- **Phase** ⏱️ – a step in the request lifecycle where hooks may run.
- **Verb** 🔤 – the canonical name of an operation such as create or read.
- **Runtime** 🧠 – orchestrates phases and hooks while processing a request.
- **Kernel** 🧩 – the core dispatcher invoked by the runtime to handle operations.
- **Schema** 🧬 – the structured shape of request or response data.
- **Request** 📥 – inbound data and context provided to an operation.
- **Response** 📤 – outbound result returned after an operation completes.

## Built-in Verbs 🧰

Tigrbl exposes a canonical set of operations that surface as both REST
and RPC endpoints. The table below summarizes the default REST routes,
RPC methods, arity, and the expected input and output shapes for each
verb. `{resource}` stands for the collection path and `{id}` is the
primary key placeholder.

| Verb | REST route | RPC method | Arity | Input type | Output type |
|------|------------|------------|-------|------------|-------------|
| `create` ➕ | `POST /{resource}` | `Model.create` | collection | dict | dict |
| `read` 🔍 | `GET /{resource}/__/{id}` | `Model.read` | member | – | dict |
| `update` ✏️ | `PATCH /{resource}/__/{id}` | `Model.update` | member | dict | dict |
| `replace` ♻️ | `PUT /{resource}/__/{id}` | `Model.replace` | member | dict | dict |
| `merge` 🧬 | `PATCH /{resource}/__/{id}` | `Model.merge` | member | dict | dict |
| `delete` 🗑️ | `DELETE /{resource}/__/{id}` | `Model.delete` | member | – | dict |
| `list` 📃 | `GET /{resource}` | `Model.list` | collection | dict | array |
| `clear` 🧹 | `DELETE /{resource}` | `Model.clear` | collection | dict | dict |
| `bulk_create` 📦➕ | `POST /{resource}` | `Model.bulk_create` | collection | array | array |
| `bulk_update` 📦✏️ | `PATCH /{resource}` | `Model.bulk_update` | collection | array | array |
| `bulk_replace` 📦♻️ | `PUT /{resource}` | `Model.bulk_replace` | collection | array | array |
| `bulk_merge` 📦🧬 | `PATCH /{resource}` | `Model.bulk_merge` | collection | array | array |
| `bulk_delete` 📦🗑️ | `DELETE /{resource}` | `Model.bulk_delete` | collection | dict | dict |
| `bulk_read` – | – | – | – | – | – |

### Update, Merge, and Replace 🔄

`update` applies a shallow PATCH: only the supplied fields change and
missing fields are left untouched. `merge` performs a deep merge with
upsert semantics—if the target row is absent it is created, and nested
mapping fields are merged rather than replaced. `replace` follows PUT
semantics, overwriting the entire record and nulling any omitted
attributes.

### Verb Overrides 🧭

Because `create` and `bulk_create` share the same collection `POST`
route, enabling `bulk_create` removes the REST `create` endpoint; the
`Model.create` RPC method remains available. Likewise, `bulk_delete`
supersedes `clear` by claiming the collection `DELETE` route. Only one
of each conflicting pair can be exposed at a time. Other verbs coexist
without conflict because they operate on distinct paths or HTTP
methods.

## Phase Lifecycle ⛓️

Tigrbl operations execute through a fixed sequence of phases. Hook chains can
attach handlers at any phase to customize behavior or enforce policy.

| Phase | Description |
|-------|-------------|
| `PRE_TX_BEGIN` ⏳ | Pre-transaction checks before a database session is used. |
| `START_TX` 🚦 | Open a new transaction when one is not already active. |
| `PRE_HANDLER` 🧹 | Validate the request and prepare resources for the handler. |
| `HANDLER` ▶️ | Execute the core operation logic within the transaction. |
| `POST_HANDLER` 🔧 | Post-processing while still inside the transaction. |
| `PRE_COMMIT` ✅ | Final verification before committing; writes are frozen. |
| `END_TX` 🧾 | Commit and close the transaction. |
| `POST_COMMIT` 📌 | Steps that run after commit but before the response is returned. |
| `POST_RESPONSE` 📮 | Fire-and-forget work after the response has been sent. |
| `ON_ERROR` 🛑 | Fallback error handler when no phase-specific chain matches. |
| `ON_PRE_TX_BEGIN_ERROR` 🧯 | Handle errors raised during `PRE_TX_BEGIN`. |
| `ON_START_TX_ERROR` 🧯 | Handle errors raised during `START_TX`. |
| `ON_PRE_HANDLER_ERROR` 🧯 | Handle errors raised during `PRE_HANDLER`. |
| `ON_HANDLER_ERROR` 🧯 | Handle errors raised during `HANDLER`. |
| `ON_POST_HANDLER_ERROR` 🧯 | Handle errors raised during `POST_HANDLER`. |
| `ON_PRE_COMMIT_ERROR` 🧯 | Handle errors raised during `PRE_COMMIT`. |
| `ON_END_TX_ERROR` 🧯 | Handle errors raised during `END_TX`. |
| `ON_POST_COMMIT_ERROR` 🧯 | Handle errors raised during `POST_COMMIT`. |
| `ON_POST_RESPONSE_ERROR` 🧯 | Handle errors raised during `POST_RESPONSE`. |
| `ON_ROLLBACK` ↩️ | Run when the transaction rolls back to perform cleanup. |

### Happy-path flow

```

PRE\_TX\_BEGIN
|
START\_TX
|
PRE\_HANDLER
|
HANDLER
|
POST\_HANDLER
|
PRE\_COMMIT
|
END\_TX
|
POST\_COMMIT
|
POST\_RESPONSE

```

If a phase raises an exception, control transfers to the matching
`ON_<PHASE>_ERROR` chain or falls back to `ON_ERROR`, with `ON_ROLLBACK`
executing when the transaction is rolled back.

## Request → Response Flow Examples 🔀

### REST example

```

Client
|
v
HTTP Request
|
v
ASGI Router
|
v
Tigrbl Runtime
|
v
Operation Handler
|
v
HTTP Response

```

### RPC example

```

Client
|
v
JSON-RPC Request
|
v
RPC Dispatcher
|
v
Tigrbl Runtime
|
v
Operation Handler
|
v
JSON-RPC Response

````

## Hooks 🪝

Hooks allow you to plug custom logic into any phase of a verb. Use the
`hook_ctx` decorator to declare context-only hooks:

```python
from tigrbl import Base, hook_ctx

class Item(Base):
    __tablename__ = "items"

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def validate(cls, ctx):
        if ctx["request"].payload.get("name") == "bad":
            raise ValueError("invalid name")
````

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
hooks. 📋

## Step Types 🧱

Tigrbl orders work into labeled steps that control how phases run:

* **secdeps** 🔐 – security dependencies executed before other checks. Downstream
  applications declare these to enforce auth or policy.
* **deps** 🧩 – general dependencies resolved ahead of phase handlers. Downstream
  code provides these to inject request context or resources.
* **sys** 🏗️ – system steps bundled with Tigrbl that drive core behavior.
  Maintainers own these and downstream packages should not modify them.
* **atoms** ⚛️ – built-in runtime units such as schema collectors or wire
  validators. These are maintained by the core team.
* **hooks** 🪝 – extension points that downstream packages register to customize
  phase behavior.

Only `secdeps`, `deps`, and `hooks` are expected to be configured downstream;
`sys` and `atom` steps are maintained by the Tigrbl maintainers.

## Kernelz Labeling 🔎

Running apps expose a `/system/kernelz` diagnostics endpoint that returns the
kernel's phase plan for each model and operation. Every entry is prefixed by
its phase and a descriptive label, for example:

```
PRE_TX:secdep:myapp.auth.require_user
HANDLER:hook:wire:myapp.handlers.audit@HANDLER
END_TX:hook:sys:txn:commit@END_TX
POST_HANDLER:atom:wire:dump@POST_HANDLER
```

The token after the phase identifies the step type:

* `secdep` and `dep` – security and general dependencies as
  `PRE_TX:secdep:<callable>` and `PRE_TX:dep:<callable>`.
* `hook:sys` – built-in system hooks shipped with Tigrbl.
* `hook:wire` – default label for user hooks including module/function name + phase.
* `atom:{domain}:{subject}` – runtime atoms, e.g. `atom:wire:dump`.

These labels allow downstream services to inspect execution order and debug how
work is scheduled. 🧭

## Configuration Overview ⚙️

### Operation Config Precedence 🧮

When merging configuration for a given operation, Tigrbl layers settings in
increasing order of precedence:

1. defaults
2. app config
3. API config
4. table config
5. column `.cfg` entries
6. operation spec
7. per-request overrides

Later entries override earlier ones, so request overrides win over all other
sources. This can be summarized as
`overrides > opspec > colspecs > tabspec > apispec > appspec > defaults`.

### Schema Config Precedence 🧬

Tigrbl merges schema configuration from several scopes.
Later layers override earlier ones, with the precedence order:

1. defaults (lowest)
2. app configuration
3. API configuration
4. table configuration
5. column-level `cfg` values
6. op-specific `cfg`
7. per-request overrides (highest)

This hierarchy ensures that the most specific settings always win. 🥇

### Table-Level 🧾

* `__tigrbl_request_extras__` – verb-scoped virtual request fields.
* `__tigrbl_response_extras__` – verb-scoped virtual response fields.
* `__tigrbl_register_hooks__` – hook registration entry point.
* `__tigrbl_nested_paths__` – nested REST path segments.
* `__tigrbl_allow_anon__` – verbs permitted without auth.
* `__tigrbl_owner_policy__` / `__tigrbl_tenant_policy__` – server vs client field injection.
* `__tigrbl_verb_aliases__` & `__tigrbl_verb_alias_policy__` – custom verb names.

### Routing 🧭

* `__tigrbl_nested_paths__` for hierarchical routing.
* `__tigrbl_verb_aliases__` for custom verbs.
* `__tigrbl_verb_alias_policy__` to scope alias application.

### Persistence 💾

* Mixins such as `Upsertable`, `Bootstrappable`, `GUIDPk`, `Timestamped`.
* Policies `__tigrbl_owner_policy__` and `__tigrbl_tenant_policy__`.
* `transactional` decorator for atomic RPC + REST endpoints.

### Security 🔐

* Pluggable `AuthNProvider` interface.
* `__tigrbl_allow_anon__` to permit anonymous access.

### Default Precedence 🔧

When assembling values for persistence, defaults are resolved in this order:

1. Client-supplied value
2. API `default_factory`
3. ORM default
4. Database `server_default`
5. HTTP 422 if the field is required and still missing

### Database Guards 🛡️

Tigrbl executes each phase under database guards that temporarily replace
`commit` and `flush` on the SQLAlchemy session. Guards prevent writes or
commits outside their allowed phases and only permit commits when Tigrbl
owns the transaction. See the
[runtime documentation](tigrbl/v3/runtime/README.md#db-guards) for the full
matrix of phase policies.

The `START_TX` phase opens a transaction and disables `session.flush`,
allowing validation and hooks to run before any statements hit the
database. Once the transaction exists, `PRE_HANDLER`, `HANDLER`, and
`POST_HANDLER` phases permit flushes so pending writes reach the database
without committing. The workflow concludes in `END_TX`, which performs a
final flush and commits the transaction when the runtime owns it. ✅

### Response and Template Specs 📑

Customize outbound responses with `ResponseSpec` and `TemplateSpec`. These dataclasses
control headers, status codes, and optional template rendering. See
[tigrbl/v3/response/README.md](tigrbl/v3/response/README.md) for field descriptions and examples.

### Dependencies 📦

* SQLAlchemy for ORM integration.
* Pydantic for schema generation.
* ASGI-native routing and dependency injection.

## Best Design Practices ✅

The following practices are the canonical, production-ready patterns for
building on Tigrbl. Each rule is explained and demonstrated with
approved usage. These are not optional—adhering to them keeps the runtime
predictable, preserves hook lifecycle guarantees, and ensures schema
consistency across REST and RPC surfaces.

### 1) Never import SQLAlchemy directly or bypass Tigrbl APIs

**Why:** Direct imports bypass Tigrbl's compatibility layer and make it
harder to evolve internal dependencies. Use the Tigrbl exports so your
code stays aligned with the framework’s versioned ASGI API.

✅ **Preferred:**
```python
from tigrbl import Base, TigrblApp, TigrblApi
from tigrbl.types import Integer, String, Mapped
from tigrbl.types import Depends, HTTPException, Request
```

🚫 **Avoid:**
```python
from sqlalchemy import Integer, String
from some_framework import Depends
```

### 2) Do not coerce UUIDs manually

**Why:** Tigrbl schemas and types already normalize UUIDs. Manual coercion
creates inconsistent behavior across engines and breaks schema-level
validation.

✅ **Preferred:**
```python
from tigrbl.types import PgUUID, uuid4, Mapped

class Item(Table):
    __tablename__ = "items"
    id: Mapped[PgUUID] = acol(primary_key=True, default=uuid4)
```

🚫 **Avoid:**
```python
from uuid import UUID

item_id = UUID(str(payload["id"]))
```

### 3) Use engine specs for persistence, not ad-hoc engines

**Why:** Engine specs make persistence declarative, testable, and
compatible with engine resolution across app, API, table, and op scopes.

✅ **Preferred:**
```python
from tigrbl.engine.shortcuts import engine_spec
from tigrbl.engine.decorators import engine_ctx

spec = engine_spec(kind="postgres", async_=True, host="db", name="app_db")

@engine_ctx(spec)
class App:
    ...
```

🚫 **Avoid:**
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://...")
```

### 4) Never call DB session methods directly

**Why:** Direct calls bypass the hook lifecycle and the database guards.
Use model handlers or `app.<Model>.handlers.<op>` so hooks, policies, and
schema enforcement run consistently.

✅ **Preferred:**
```python
result = await Item.handlers.create(payload, ctx=request_ctx)
# or from a Tigrbl app instance:
result = await app.Item.handlers.create(payload, ctx=request_ctx)
```

🚫 **Avoid:**
```python
db.add(item)
await db.execute(statement)
```

### 5) Always use encapsulated payloads as inputs and outputs

**Why:** Tigrbl expects request/response envelopes to preserve metadata,
support policy enforcement, and keep REST/RPC in lockstep.

✅ **Preferred:**
```python
from tigrbl import get_schema

CreateIn = get_schema(Item, "create", "in")
CreateOut = get_schema(Item, "create", "out")

payload = CreateIn(name="Widget")
result = await Item.handlers.create(payload, ctx=request_ctx)
response = CreateOut(result=result)
```

🚫 **Avoid:**
```python
payload = {"name": "Widget"}
result = await Item.handlers.create(payload)
```

### 6) Encapsulation must use `get_schema(...)`

**Why:** `get_schema` guarantees the envelope is aligned to the configured
schema and respects schema overrides, request extras, and response extras.

✅ **Preferred:**
```python
ListIn = get_schema(Item, "list", "in")
ListOut = get_schema(Item, "list", "out")
```

🚫 **Avoid:**
```python
from pydantic import BaseModel

class ListIn(BaseModel):
    payload: dict
```

### 7) `Table` must be the first inherited class for all models

**Why:** Tigrbl inspects base classes for lifecycle and configuration.
Putting `Table` first preserves deterministic MRO behavior.

✅ **Preferred:**
```python
from tigrbl.orm.tables import Table
from tigrbl.orm.mixins import Timestamped

class Item(Table, Timestamped):
    __tablename__ = "items"
```

🚫 **Avoid:**
```python
class Item(Timestamped, Table):
    __tablename__ = "items"
```

### 8) Never call `db.flush()` or `db.commit()`

**Why:** The hook lifecycle owns transactional boundaries. Manual flush or
commit short-circuits phase guards and can corrupt the request lifecycle.

✅ **Preferred:**
```python
@hook_ctx(ops="create", phase="HANDLER")
async def handler(ctx):
    await Item.handlers.create(ctx["request"].payload, ctx=ctx)
```

🚫 **Avoid:**
```python
db.flush()
db.commit()
```

### 9) Use ops for new REST/RPC methods—never add ad-hoc framework routes

**Why:** Ops keep routing, schemas, hooks, and policies unified. Custom
custom framework routes bypass these guarantees.

✅ **Preferred:**
```python
from tigrbl import op_ctx

@op_ctx(name="rotate_keys", method="POST", path="/keys/rotate")
async def rotate_keys(payload, *, ctx):
    return await Key.handlers.rotate(payload, ctx=ctx)
```

🚫 **Avoid:**
```python
from some_framework import APIRouter

router = APIRouter()

@router.post("/keys/rotate")
async def rotate_keys(payload):
    ...
```

### 10) Use context decorators where appropriate

**Why:** Context decorators (`engine_ctx`, `schema_ctx`, `op_ctx`,
`hook_ctx`) provide explicit, declarative binding of behavior and are
resolved deterministically by the runtime.

✅ **Preferred:**
```python
from tigrbl import hook_ctx, op_ctx, schema_ctx
from tigrbl.engine.decorators import engine_ctx

@engine_ctx(kind="sqlite", mode="memory")
class Item(Table):
    __tablename__ = "items"

@schema_ctx(ops="create", cfg={"exclude": {"id"}})
class ItemCreateSchema:
    model = Item

@op_ctx(name="export", method="GET", path="/items/export")
async def export_items(payload, *, ctx):
    return await Item.handlers.list(payload, ctx=ctx)

@hook_ctx(ops="create", phase="PRE_HANDLER")
async def validate(ctx):
    ...
```

### Engine & Provider examples 🛠️

```python
from tigrbl.engine.shortcuts import engine_spec, prov
from tigrbl.engine._engine import Engine, Provider

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

### Attaching engine contexts 🔌

`engine_ctx` binds database configuration to different layers. It accepts a
DSN string, a mapping, an `EngineSpec`, a `Provider`, or an `Engine`. The
resolver chooses the most specific binding in the order
`op > table > api > app`.

#### Engine precedence 🥇

When engine contexts are declared at multiple scopes, Tigrbl resolves them
with strict precedence:

1. **Op level** – bindings attached directly to an operation take highest priority.
2. **Table/Model level** – definitions on a model or table override API and app defaults.
3. **API level** – bindings on the API class apply when no model-specific context exists.
4. **App level** – the default engine supplied to the application is used last.

This ordering ensures that the most specific engine context always wins.

#### Declarative bindings 📝

```python
from types import SimpleNamespace
from tigrbl.engine.shortcuts import prov, engine

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

#### Decorative bindings 🎛️

```python
from tigrbl.engine.decorators import engine_ctx
from tigrbl.engine.shortcuts import prov, engine

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

### Swarmauri class + Tigrbl lifecycle integration 🧬

If you need to run concrete Swarmauri classes inside Tigrbl's runtime, see:

* [`examples/swarmauri_tigrbl_bridge.py`](./examples/swarmauri_tigrbl_bridge.py)
* [`examples/swarmauri_tigrbl_bridge_smooth.py`](./examples/swarmauri_tigrbl_bridge_smooth.py)

The bridge examples cover two integration styles:

* **Factory + schema-rich envelope** (`swarmauri_tigrbl_bridge.py`)
  * Swarmauri Pydantic JSON workflows (`model_validate_json`, `model_dump_json`,
    `model_json_schema`) with `HumanMessage`.
  * A Swarmauri `Factory` invocation during `PRE_HANDLER` via `hook_ctx`.
  * Tigrbl default verbs (`create`, `get`, `list`, `update`, `delete`) plus a custom op.
  * `engine_ctx` at model and operation scope.
  * Generated OpenAPI and OpenRPC documents mounted from the same model bindings.

* **Smoother direct-model flow** (`swarmauri_tigrbl_bridge_smooth.py`)
  * Uses hooks + default `create` persistence to normalize Swarmauri payloads.
  * Adds a `Conversation` table with a persisted one-to-many relationship to messages.
  * Avoids extra `json_schema` fields in request/response payload contracts.
  * Returns `HumanMessage.model_validate_json(...)` directly from a custom op.
  * Uses the concrete model classes themselves to derive input/output schema docs.

## Glossary 📖

1. Tables
2. Schemas
3. Schema Overlays (Request Extras)
4. Phases
5. Phase Lifecycle
6. Request
7. Request Ctx
8. Default Flush
9. Core
10. Core\_Raw
