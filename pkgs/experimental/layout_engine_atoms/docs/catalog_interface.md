# Atom Catalog Interface Blueprint

This note captures the API surface we will publish for framework-specific atom
catalogs (`layout_engine_atoms.catalog.vue`, `layout_engine_atoms.catalog.react`,
`layout_engine_atoms.catalog.svelte`). Documenting it up front keeps the Vue,
React, and Svelte runtimes aligned and prevents ad-hoc exports from leaking out
of the package over time.

## Module layout

```
layout_engine_atoms/
    catalog/
        __init__.py          # helpers + registry loader
        vue.py               # Vue-specific presets
        react.py             # React-specific presets (placeholder until filled)
        svelte.py            # Svelte-specific presets (placeholder until filled)
```

- `layout_engine_atoms.catalog` (package) exposes shared helpers and a
  `load_catalog(name: str)` dispatcher.
- Each framework-specific module exports a catalog that targets a single UI
  runtime. Submodules may import shared role definitions but must not mutate
  globals owned by another catalog.

## Naming and exports

Every catalog module MUST export the following symbols:

| Symbol | Type | Purpose |
| ------ | ---- | ------- |
| `CatalogName` | `AtomPresetCatalog` subclass or alias | Declarative presets container |
| `DEFAULT_PRESETS` | `dict[str, AtomPreset]` | Canonical role → preset mapping |
| `DEFAULT_ATOMS` | `dict[str, AtomSpec]` | Precomputed specs for the registry |
| `build_default_registry()` | `AtomRegistry` factory | Ready-to-use registry with defaults |
| `build_registry(presets=None)` | callable | Allows overrides/extension before building |
| `PRESET_VERSION` | `str` | Semantic version of the preset set |

Additional helpers are allowed so long as they do not break compat for the
baseline exports above.

### Aggregator exports

The package-level `layout_engine_atoms.catalog` must expose:

```python
# canonical lookup
def load_catalog(name: str = "vue") -> AtomPresetCatalog: ...

# convenience registries
def build_registry(name: str = "vue", *, overrides=None) -> AtomRegistry: ...

# discoverability
SUPPORTED_CATALOGS = ("vue", "react", "svelte")
```

Calling `load_catalog()` or `build_registry()` SHOULD raise `KeyError` for
unknown catalog names to keep error handling explicit.

## Catalog contract

Each catalog must satisfy the base `AtomPresetCatalog` interface:

- `presets()` returns an iterable of `AtomPreset`.
- `as_specs()` mirrors `DEFAULT_ATOMS`.
- `build_registry()` returns an `AtomRegistry` that registers all presets.

Presets MUST use the same semantic roles across frameworks even if the module
specifier/export names differ (e.g., `"viz:metric:kpi"` exists everywhere).
Framework-specific module strings (`module`, `export`) are free to vary, but
defaults (props) should remain semantically equivalent.

### Versioning

`PRESET_VERSION` tracks the catalog release. Bump the version when the shipped
set of presets changes (add/remove role, update defaults). Wrappers can surface
the version for telemetry.

## Multi-catalog strategy

- Keep shared role definitions in a neutral location (e.g.,
  `layout_engine_atoms.catalog.roles`) to avoid drift.
- Use thin adapters in each catalog module if the framework requires special
  props (e.g., Vue `props` vs. React `props`). Where possible, favour pure data
  so wrappers can stay agnostic.
- The future Vue/React/Svelte wrappers should import only the public symbols in
  this document. Avoid reaching into private module internals.

## Extension hooks

The `build_registry` helper should accept either:

```python
def build_registry(
    *, extra_presets: Iterable[AtomPreset] | Mapping[str, AtomPreset] | None = None,
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
) -> AtomRegistry:
    ...
```

This lets downstream packages add roles or tweak defaults without mutating
`DEFAULT_PRESETS`.

## Next steps

- Implement the package structure above (split current `catalog.py` into
  `catalog/vue.py`).
- Update `layout_engine_atoms/__init__.py` and downstream imports to reflect the
  new layout.
- Add unit tests that load each catalog and confirm the required exports exist.
