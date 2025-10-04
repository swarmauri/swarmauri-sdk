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
A high-leverage meta-framework that turns plain SQLAlchemy models into a fully-featured REST+RPC surface with near-zero boilerplate. 🚀

## Features ✨

- ⚡ Zero-boilerplate CRUD for SQLAlchemy models
- 🔌 Unified REST and RPC endpoints from a single definition
- 🪝 Hookable phase system for deep customization
- 🧩 Pluggable engine and provider abstractions
- 🚀 Built on FastAPI and Pydantic for modern Python web apps

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
| `read` 🔍 | `GET /{resource}/{id}` | `Model.read` | member | – | dict |
| `update` ✏️ | `PATCH /{resource}/{id}` | `Model.update` | member | dict | dict |
| `replace` ♻️ | `PUT /{resource}/{id}` | `Model.replace` | member | dict | dict |
| `merge` 🧬 | `PATCH /{resource}/{id}` | `Model.merge` | member | dict | dict |
| `delete` 🗑️ | `DELETE /{resource}/{id}` | `Model.delete` | member | – | dict |
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
FastAPI Router
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
* FastAPI for routing and dependency injection.

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


