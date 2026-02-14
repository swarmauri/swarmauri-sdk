# Tigrbl Examples for Implementers

The `examples/` tree is a lesson-oriented test curriculum for implementers.
Each module demonstrates practical usage patterns you can apply in production
Tigrbl services.

Most lessons are written as pytest tests so each concept is both documented and
executable.

## How to run

From `/workspace/swarmauri-sdk/pkgs`:

```bash
uv run --package tigrbl-tests --directory standards/tigrbl_tests pytest examples
```

## How to read the curriculum

The folder names reflect the lesson sequence. Hyphenated and underscored module
families coexist because they capture different generations of example tracks.
Both are useful for implementers.

## Module families and lesson intent

### Beginner lessons

- `01-beginner-foundations` / `01_beginner_fundamentals`
  - class/model basics, app setup fundamentals.
- `02-beginner-columns` / `02_beginner_models`
  - storage, field, and IO basics with mapped model columns.
- `03-beginner-mixins` / `03_beginner_specs`
  - common mixins and reusable column specification patterns.
- `04-beginner-app-api` / `04_beginner_tables_columns`
  - app/table specification and model inclusion in API routers.
- `05-beginner-usage` / `05_beginner_app_api`
  - first REST and JSON-RPC usage flows.

### Intermediate lessons

- `06-intermediate-bindings` / `06_intermediate_ops`
  - operation binding and API behavior customization.
- `07-intermediate-decorators` / `07_intermediate_hooks`
  - schema/op/hook decorators and execution flow.
- `08-intermediate-config` / `08_intermediate_bindings`
  - configuration precedence and inheritance behavior.
- `09-intermediate-ops-io` / `09_intermediate_config`
  - operation contracts and request/response shaping.
- `10-intermediate-system` / `10_intermediate_clients`
  - diagnostics and client interaction patterns.
- `17_intermediate_relationships`
  - relationship-focused lessons, including one-to-one, one-to-many,
    many-to-many, and self-referential patterns using REST and JSON-RPC.

### Advanced lessons

- `11-advanced-uvicorn` / `11_advanced_mapped_vs_nonmapped`
  - deeper runtime and model semantics under real server execution.
- `12-advanced-parity` / `12_advanced_mro_precedence`
  - protocol parity and inheritance precedence behavior.
- `13-advanced-hooks` / `13_advanced_custom_ops`
  - advanced hook orchestration and custom operations.
- `14-advanced-column-types` / `14_advanced_uvicorn_e2e`
  - richer types and full end-to-end API interaction.
- `15-advanced-table-design` / `15_advanced_diagnostics`
  - robust table design and diagnostics-driven validation.

### Expert lessons

- `16_expert_table_bindings`
- `17_expert_column_bindings`
- `18_expert_api_bindings`
- `19_expert_app_bindings`
- `20_expert_hook_op_engine_bindings` / `20_expert_mounts`
- `21_expert_security`
- `22_expert_document_versioning`

These modules combine multiple concepts (bindings, hooks, mounts, security,
versioning) for advanced implementation scenarios.

## Maintainer notes

For maintainer-facing expectations on style, pedagogical structure, and
relationship lesson requirements, see `MAINTAINERS_GUIDE.md`.
