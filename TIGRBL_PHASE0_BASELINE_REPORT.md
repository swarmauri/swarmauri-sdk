# Tigrbl Phase 0 Baseline Report

Date: 2026-03-05

## Scope
- `pkgs/standards/tigrbl_core`
- `pkgs/standards/tigrbl_base`
- `pkgs/standards/tigrbl_concrete`
- `pkgs/standards/tigrbl`
- Compatibility suite: `pkgs/standards/tigrbl_tests`

## Baseline Test Runs
1. `uv run --package tigrbl_core --directory pkgs/standards/tigrbl_core pytest -q`
   - Result: PASS (`4 passed`)
2. `uv run --package tigrbl_base --directory pkgs/standards/tigrbl_base pytest -q`
   - Result: PASS (`1 passed`)
3. `uv run --package tigrbl_concrete --directory pkgs/standards/tigrbl_concrete pytest -q`
   - Result: PASS (`1 passed`)
4. `uv run --package tigrbl_tests --directory pkgs/standards/tigrbl_tests pytest -q`
   - Result: FAIL (ImportError at collection)
5. `uv run --package tigrbl --directory pkgs/standards/tigrbl pytest -q`
   - Result: FAIL (same ImportError via `tigrbl_tests` conftest import path)

## Failure Grouping (Root Cause Categories)
### Category A: Facade import failure from missing mapping implementation in `tigrbl`
- Error:
  - `ImportError: cannot import name 'engine_resolver' from 'tigrbl.mapping' (unknown location)`
- Trigger path:
  - `tigrbl.__init__` -> `tigrbl_concrete._concrete._app` -> `tigrbl.ddl` -> `from ..mapping import engine_resolver`
- Evidence:
  - Directory `pkgs/standards/tigrbl/tigrbl/mapping` has only `__pycache__`, no source modules.
  - `tigrbl_canon.mapping.engine_resolver` exists and imports correctly.

## Import Surface Inventory
1. `tigrbl_core._spec` exports: `44` symbols.
2. `tigrbl_base._base` exports: `11` symbols.
3. `tigrbl_concrete._concrete` exports: `32` symbols.
4. `tigrbl` facade exports (`__all__`): `98` symbols.

## Package Dependency Edges (Observed via static import scan)
- `tigrbl -> tigrbl_base`
- `tigrbl -> tigrbl_concrete`
- `tigrbl -> tigrbl_core`
- `tigrbl_core -> tigrbl`
- `tigrbl_core -> tigrbl_canon`
- `tigrbl_base -> tigrbl_core`
- `tigrbl_concrete -> tigrbl`
- `tigrbl_concrete -> tigrbl_base`
- `tigrbl_concrete -> tigrbl_core`
- `tigrbl_concrete -> tigrbl_canon`
- `tigrbl_canon -> tigrbl_core`
- `tigrbl_canon -> tigrbl_concrete`

## Potential Direct Mutual Cycles (Package-level)
- `tigrbl <-> tigrbl_core`
- `tigrbl <-> tigrbl_concrete`
- `tigrbl_canon <-> tigrbl_core`
- `tigrbl_canon <-> tigrbl_concrete`

Notes:
- This is static edge detection and indicates coupling risk.
- Phase 1/2 will confirm which cycles are architecturally valid vs violations.

## Early Layering-Risk Signals
1. `tigrbl_core._spec.op_spec` imports `tigrbl.schema.types.SchemaArg` (facade dependency from spec layer).
2. `tigrbl_core._spec.app_spec` and `table_spec` reference `..mapping.spec_normalization`, but `tigrbl_core` has no `mapping` package.
3. Multiple concrete modules import from `tigrbl.*` facade paths (`tigrbl.ddl`, `tigrbl.system`, `tigrbl.op`, `tigrbl.schema`), creating reverse coupling.

## Immediate Phase 1/2 Focus
1. Repair facade mapping resolution so `tigrbl.ddl` can resolve `engine_resolver` correctly.
2. Remove `spec -> facade` dependency patterns in `tigrbl_core._spec`.
3. Reduce `concrete -> facade` imports where possible to avoid circular bootstrapping.
4. Re-run `tigrbl_tests` after each focused fix batch.
