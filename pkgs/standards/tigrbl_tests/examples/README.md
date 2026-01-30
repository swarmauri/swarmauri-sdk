# Tigrbl Tests Examples Curriculum

This directory contains **downstream-focused** pytest lessons that demonstrate
how to implement Tigrbl in real services. The examples are intentionally written
for implementers (application builders), not for core maintainers. Every lesson
is a pytest file that can be read top-to-bottom to learn a single concept and
run as a working example.

## Usage

Run the examples from the monorepo `pkgs` directory:

```bash
cd /workspace/swarmauri-sdk/pkgs
uv run --package tigrbl-tests --directory standards/tigrbl_tests pytest standards/tigrbl_tests/examples
```

## Curriculum Overview

The curriculum is organized into **15 modules** (beginner → intermediate →
advanced). Each module has four lessons, and each lesson maps to a single
pytest file. The lesson files are indexed to preserve ordering when browsing.

### Beginner Modules (01-05)

1. **01_beginner_fundamentals**
   - 01_class_creation: Define a Base model and verify table/columns.
   - 02_instantiation: Instantiate a model and inspect attributes.
   - 03_types_exports: Explore core column types via `tigrbl.types`.
   - 04_table_args: Apply table constraints via `__table_args__`.
2. **02_beginner_models**
   - 01_mixin_usage: Use mixins like `GUIDPk` for IDs.
   - 02_mapped_vs_nonmapped: Compare mapped vs non-mapped columns.
   - 03_column_specs: Use column specs to drive IO behavior.
   - 04_indexed_table: Add indexes through `__table_args__`.
3. **03_beginner_specs**
   - 01_field_spec_f: Configure `F` field specs for types/metadata.
   - 02_io_spec: Configure `IO` spec verb visibility.
   - 03_storage_spec_s: Configure `S` storage spec settings.
   - 04_acol_shortcut: Use `acol` shortcut for columns.
4. **04_beginner_tables_columns**
   - 01_supported_types: Inspect all supported `tigrbl.types` column types.
   - 02_column_defaults: Review column defaults at the table level.
   - 03_table_args_constraints: Validate constraints in metadata.
   - 04_column_indexes: Inspect indexes in table metadata.
5. **05_beginner_app_api**
   - 01_tigrbl_app_init: Initialize `TigrblApp` with a model.
   - 02_app_router: Include the API router in a FastAPI app.
   - 03_jsonrpc_mount: Mount JSON-RPC routes.
   - 04_default_ops: Confirm default ops are registered.

### Intermediate Modules (06-10)

6. **06_intermediate_ops**
   - 01_op_ctx: Create custom ops with `@op_ctx`.
   - 02_op_alias: Alias core ops with `@alias_ctx`.
   - 03_op_payloads: Inspect op handlers and payloads.
   - 04_ops_defaults: Verify default ops in the registry.
7. **07_intermediate_hooks**
   - 01_hook_ctx: Declare hooks with `@hook_ctx`.
   - 02_model_hook_binding: Bind hooks to models.
   - 03_hook_order: Verify hook ordering per op.
   - 04_hook_scopes: Scope hooks to specific ops.
8. **08_intermediate_bindings**
   - 01_bind_rebind: Use `bind` and `rebind` on models.
   - 02_build_schemas: Build schema artifacts for ops.
   - 03_build_handlers: Build handlers for bound ops.
   - 04_register_rpc: Register JSON-RPC routes.
9. **09_intermediate_config**
   - 01_app_spec_mro: Understand configuration precedence (MRO).
   - 02_table_config_provider: Register table config providers.
   - 03_op_config_provider: Configure op defaults.
   - 04_request_response_extras: Register request/response extras.
10. **10_intermediate_clients**
    - 01_httpx_crud: CRUD via `httpx`.
    - 02_tigrbl_client_parity: Match `httpx` with `tigrbl_client`.
    - 03_openapi_schema: Validate `/openapi.json` output.
    - 04_rpc_calls: Use JSON-RPC via `tigrbl_client`.

### Advanced Modules (11-15)

11. **11_advanced_mapped_vs_nonmapped**
    - 01_mapped_columns: Use typed `Mapped` columns.
    - 02_nonmapped_columns: Use SQLAlchemy `Column` directly.
    - 03_mapped_mixins: Combine mapped fields with mixins.
    - 04_mapped_column_specs: Use specs with mapped columns.
12. **12_advanced_mro_precedence**
    - 01_engine_precedence: Resolve engine settings in MRO.
    - 02_prefix_precedence: Override system prefixes.
    - 03_hooks_mro_merge: Merge hooks across the MRO.
    - 04_ops_mro_merge: Merge ops across the MRO.
13. **13_advanced_custom_ops**
    - 01_custom_op_schema: Configure schema refs for ops.
    - 02_custom_op_rpc: Execute custom ops via JSON-RPC.
    - 03_custom_op_rest: Expose custom ops on REST routes.
    - 04_custom_op_hooks: Attach hooks to custom ops.
14. **14_advanced_uvicorn_e2e**
    - 01_uvicorn_healthz: Validate `/healthz` over uvicorn.
    - 02_uvicorn_kernelz: Validate `/kernelz` over uvicorn.
    - 03_uvicorn_systemz: Validate `/systemz` over uvicorn.
    - 04_uvicorn_rpc_rest_parity: Compare REST/RPC over uvicorn.
15. **15_advanced_diagnostics**
    - 01_diagnostics_openapi: Validate diagnostics in OpenAPI.
    - 02_diagnostics_methodz: Validate `/methodz` output.
    - 03_diagnostics_hookz: Validate `/hookz` output.
    - 04_diagnostics_kernel_payload: Inspect kernel payloads.

### Expert Modules (Planned)

These expert lessons are intentionally placeholders for future expansion:

- **16_expert_scalability** (placeholder)
- **17_expert_multi_tenant** (placeholder)
- **18_expert_extensibility** (placeholder)
- **19_expert_observability** (placeholder)
- **20_expert_security** (placeholder)
