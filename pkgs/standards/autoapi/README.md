# AutoAPI

A high-leverage meta-framework that turns plain SQLAlchemy models into a fully-featured REST+RPC surface with near zero boiler plate.

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
- `_apply_row_filters` / _RowBound hook providers
- Automated route creation: rest paths or nested rest paths, rpc gateway, healthz, methodz
- Support for AuthNProvider extensions
