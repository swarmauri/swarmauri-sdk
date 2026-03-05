# Phased Plan: Tigrbl Split Conformance, Facade Exports, and Test Expansion

## Summary
This plan executes the refactor in controlled phases across the **core split surface**: `tigrbl_core` (spec), `tigrbl_base` (base), `tigrbl_concrete` (concrete), and `tigrbl` (facade), with compatibility checks against `tigrbl_tests`.
Primary goals are:
1. Enforce strict layering (`spec -> base -> concrete` direction only, no reverse violations).
2. Ensure `tigrbl` re-exports all first-class objects required by compatibility tests.
3. Add package-local pytest coverage for split packages, with fixtures + parameterization and no mocks/monkeypatch/unittest.
4. Produce a conformance report (hanging objects, cycles, fixes, PR traceability).

## Phase 0: Baseline and Inventory (Read-only + Baseline Run)
### Objectives
- Establish current passing/failing state.
- Build a concrete inventory of objects and imports by package layer.

### Tasks
1. Run baseline tests for compatibility suite:
   - `uv run --package tigrbl_tests --directory pkgs/standards/tigrbl_tests pytest`
2. Run smoke/unit baselines for split packages:
   - `uv run --package tigrbl_core --directory pkgs/standards/tigrbl_core pytest`
   - `uv run --package tigrbl_base --directory pkgs/standards/tigrbl_base pytest`
   - `uv run --package tigrbl_concrete --directory pkgs/standards/tigrbl_concrete pytest`
   - `uv run --package tigrbl --directory pkgs/standards/tigrbl pytest`
3. Generate import maps:
   - Identify all imports from spec/base/concrete/facade modules.
   - Tag each symbol as `spec`, `base`, `concrete`, `facade-only`, or `unknown`.
4. Capture unresolved symbols/import errors and group by root cause.

### Exit Criteria
- Baseline failures documented with stack traces grouped by category.
- Initial symbol inventory exists for all four packages.

## Phase 1: Enforce Layering Boundaries
### Objectives
- Remove violations:
  - Spec implementing base/concrete behavior.
  - Base importing/depending on concrete behavior.

### Tasks
1. Scan for violations:
   - `tigrbl_core._spec` importing `tigrbl_base` or `tigrbl_concrete`.
   - `tigrbl_base._base` importing `tigrbl_concrete`.
2. For each violation:
   - If behavior is contract/interface: keep in `spec`.
   - If behavior is reusable abstract implementation: move to `base`.
   - If behavior requires concrete details/runtime integration: move to `concrete`.
3. Refactor call paths so:
   - `spec` exposes contracts/types only.
   - `base` depends on `spec` only.
   - `concrete` depends on `base` + `spec`.
4. Add/adjust minimal package tests that assert layering expectations (import-level and behavior-level).

### Exit Criteria
- Zero spec->base/concrete and base->concrete violations in split surface.
- Refactors preserve existing behavior for compatibility tests.

## Phase 2: Facade Compatibility and Re-exports (`tigrbl`)
### Objectives
- Ensure `tigrbl` exposes all first-class API symbols expected by `tigrbl_tests`.

### Tasks
1. Build expected symbol list from:
   - Failing `tigrbl_tests` imports.
   - Existing legacy import paths in repository tests/docs.
2. Reconcile facade exports:
   - Update `tigrbl/__init__.py` alias modules and `__all__`.
   - Ensure lazy/optional imports avoid circular startup issues.
3. Validate backward compatibility:
   - Legacy paths like `tigrbl._spec.*`, `tigrbl._base.*`, `tigrbl._concrete.*`.
   - Top-level symbols (`AppSpec`, `TableBase`, `Op`, responses, decorators, etc.).
4. Re-run `tigrbl_tests` and iterate until green.

### Exit Criteria
- `tigrbl_tests` pass from their current location unchanged.
- All required first-class symbols import from `tigrbl` successfully.

## Phase 3: Split-Package Test Expansion (Pytest-only)
### Objectives
- Add focused, domain-specific tests in each split package.
- Cover contracts, base defaults, concrete behavior, and facade compatibility seams.

### Test Design Rules (enforced)
- Only `pytest`.
- No `mock`, no `monkeypatch`, no `unittest`.
- Use fixtures, `@pytest.mark.parametrize`, and combinatorial parameterization.
- One test file = one responsibility/domain.

### Package Test Additions
1. `tigrbl_core/tests`
   - Spec contract validation tests (`Spec` datamodel/typing invariants).
   - Parameterized schema/op/storage/session spec acceptance/rejection cases.
2. `tigrbl_base/tests`
   - Base-class abstract/default behavior tests against minimal concrete subclasses defined inline in tests.
   - Parameterized tests for edge input classes (empty/None/invalid typed inputs where relevant).
3. `tigrbl_concrete/tests`
   - Concrete object behavior and integration tests (responses, routing, request/session/storage wiring).
   - Combinatorial tests over response types/status/body/content-type combinations.
4. `tigrbl/tests`
   - Facade import/export tests and alias compatibility tests.
   - Parameterized symbol resolution tests validating expected API surface.

### Exit Criteria
- New tests are package-local, domain-specific, and deterministic.
- No forbidden testing patterns are introduced.
- Coverage meaningfully expands across split-surface responsibilities.

## Phase 4: Conformance Audit and Cycle Report
### Objectives
- Deliver required notes/report for boss + PR reviewers.

### Tasks
1. Produce report file (recommended path):
   - `pkgs/standards/tigrbl/REFRACTOR_CONFORMANCE_REPORT.md`
2. Report sections:
   - Hanging objects (unknown placement; left in place with rationale).
   - Detected cycles (package/module A <-> B) with impact notes.
   - Layer violations found and resolved.
   - Remaining deferred items with reason/risk.
   - PR traceability: file paths + commit references + “why/how” per fix.
3. Mirror concise summary in PR description.

### Exit Criteria
- Report is complete and references exact files/changes for every resolved issue.
- Unresolved items are explicit and justified.

## Phase 5: Quality Gates and Final Validation
### Objectives
- Satisfy repository contribution requirements for changed packages.

### Tasks
For each changed package under `pkgs/` run:
1. Format:
   - `uv run --directory <member> --package <name> ruff format .`
2. Lint fix:
   - `uv run --directory <member> --package <name> ruff check . --fix`
3. Tests:
   - `uv run --package <name> --directory <member> pytest`

Then run final compatibility sweep:
- `uv run --package tigrbl_tests --directory pkgs/standards/tigrbl_tests pytest`

### Exit Criteria
- Lint/format clean for all changed packages.
- All targeted test suites pass, including `tigrbl_tests`.

## Important API / Interface Changes to Control
1. `tigrbl` facade exports (`__all__`, alias modules, lazy imports) may be expanded but must remain backward-compatible.
2. Split-layer module boundaries:
   - `tigrbl_core._spec`: contracts/types only.
   - `tigrbl_base._base`: abstract/default implementations only.
   - `tigrbl_concrete._concrete`: concrete runtime implementations only.
3. Any moved symbol must keep stable import path via facade aliasing/re-export unless explicitly deprecated.

## Test Scenarios (Minimum Required Matrix)
1. Import compatibility:
   - `from tigrbl import <symbol>` for all first-class exports.
   - `import tigrbl._spec`, `tigrbl._base`, `tigrbl._concrete`.
2. Layer guardrails:
   - Parameterized static import tests asserting forbidden dependency edges are absent.
3. Spec validation:
   - Valid/invalid payload matrices for core spec models and helpers.
4. Base behavior:
   - Abstract method enforcement + default behavior under multiple subclass shapes.
5. Concrete behavior:
   - Response/rendering/routing/session scenarios across varied inputs.
6. Regression:
   - Full `tigrbl_tests` suite green.

## Assumptions and Defaults
1. Scope is limited to **core split surface** (`tigrbl_core`, `tigrbl_base`, `tigrbl_concrete`, `tigrbl`) plus direct dependencies only when required by failing compatibility tests.
2. Reporting format is **PR description + dedicated markdown report file**.
3. If object ownership is unclear, object remains in place and is logged as hanging (not force-moved).
4. No API-breaking removals; compatibility is preserved through re-exports/aliases.
5. Test additions prioritize deterministic local behavior and avoid external service/network coupling.
