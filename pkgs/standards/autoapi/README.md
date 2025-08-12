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
- Table level configurations: __autoapi_nested_paths__, __autoapi_allow_anon__, & __autoapi_register_hooks__
- Column level configurations: info_schema ( disable_on, write_only, read_only, default_factory, examples, hybrid (hybrid properties), py_type)
- `_apply_row_filters` (deprecating)
- _RowBound hook providers
- phase-level hooks that can be wildcard or per-verb, per-model
- Automated route creation: rest paths or nested rest paths, rpc dispatch, healthz, methodz, hookz
- Support for AuthNProvider extensions


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