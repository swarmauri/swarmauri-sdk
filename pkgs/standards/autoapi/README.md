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
- `_apply_row_filters` (deprecating)
- _RowBound hook providers
- phase-level hooks that can be wildcard or per-verb, per-model
- Automated route creation: rest paths or nested rest paths, rpc dispatch, healthz, methodz, hookz
- Support for AuthNProvider extensions


## Configuration Overview

### Column-Level (`Column.info["autoapi"]`)
- `disable_on` – omit a field on specified verbs.
- `write_only` – exclude from `read` responses.
- `read_only` – exclude from write verbs.
- `default_factory` – callable that supplies a default value.
- `examples` – example values for documentation.
- `hybrid` – expose `@hybrid_property` fields.
- `py_type` – override the Python type.

### Table-Level
- `__autoapi_request_extras__` – verb-scoped virtual fields.
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