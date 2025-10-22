# Packaging Plan for Catalogs & Wrappers

This document captures where new modules will live as we split the atom catalog
into framework-specific sets and add thin UI wrappers.

## Repository layout (target)

```
pkgs/experimental/layout_engine_atoms/
├── src/layout_engine_atoms/
│   ├── __init__.py
│   ├── base.py
│   ├── spec.py
│   ├── shortcuts.py
│   ├── catalog/
│   │   ├── __init__.py
│   │   ├── roles.py
│   │   ├── vue.py
│   │   ├── react.py
│   │   └── svelte.py
│   └── runtime/
│       ├── __init__.py
│       ├── vue/
│       │   ├── __init__.py
│       │   └── client/        # JS/Vue assets bundled with the runtime
│       ├── react/
│       └── svelte/
├── docs/
│   ├── catalog_interface.md
│   └── packaging_plan.md
└── examples/
    └── vue/                   # Optional demo, mirrors runtime API
```

### Catalog package

- `layout_engine_atoms.catalog` becomes a namespace package.
- `roles.py` stores shared role identifiers + metadata so Vue/React/Svelte stay
  in sync.
- Each framework module (`vue.py`, `react.py`, `svelte.py`) exports the symbols
  defined in `catalog_interface.md`.
- `__init__.py` exposes `SUPPORTED_CATALOGS`, `load_catalog(name)`, and
  `build_registry(name, **kwargs)`.

Migration steps:

1. Move the current `catalog.py` contents into `catalog/vue.py`.
2. Introduce `catalog/__init__.py` with dispatcher utilities.
3. Update `layout_engine_atoms/__init__.py` and any imports to follow the new
   structure.

### Runtime packages

Each runtime (Vue, React, Svelte) gets its own Python package under
`layout_engine_atoms.runtime.<framework>`. These packages will:

- Provide Python helpers for serving manifests + static assets.
- Bundle the corresponding thin client wrapper (e.g., Vue entry bundle) inside a
  `client/` subfolder.
- Offer an ASGI app or FastAPI router that can be mounted by downstream users.

For the first iteration we will focus on Vue:

- Python API sketch:

  ```python
  from layout_engine_atoms.runtime.vue import create_layout_app

  vue_app = create_layout_app(
      manifest_builder=...,              # callable returning Manifest or dict
      mount_path="/dashboard",           # where to serve the Vue bundle
  )

  app = vue_app.asgi_app()
  ```

- Bundle layout: `runtime/vue/client/` will host the pre-built JS/CSS assets for
  the thin wrapper. We can use Vite or plain ESM to produce the distributable,
  but the repository will store the generated assets to avoid build tooling
  requirements during install.

### Examples

- The ad-hoc dashboard demo now lives at `examples/vue/`. Once the runtime is in
  place it should be pared down to show wrapper configuration only (no manual
  grid math).

## Naming & distribution

- Python package names (for `pyproject.toml`) will follow
  `layout-engine-atoms-vue` for the runtime if we decide to ship separately.
  Initially we can publish everything from the same project as optional extras:

  ```
  [project.optional-dependencies]
  vue = ["fastapi>=0.115", "uvicorn>=0.30"]
  react = [...]
  svelte = [...]
  ```

- Module import paths stay under `layout_engine_atoms` so downstream code can
  share them without juggling distribution names.

## Open questions

1. Do we bundle the Vue runtime assets directly in the wheel or fetch them at
   runtime? (Default plan: bundle in wheel for offline compatibility.)
2. Should the runtime expose both ASGI routers and CLI commands
   (`le-atoms-vue serve`)? (Decision pending.)
3. What build tool do we use for the Vue client bundle (Vite vs. Rollup vs.
   esbuild)? (Needs alignment with the broader SDK tooling.)

Feedback on this structure will guide the refactor that migrates existing code
into the new layout.
