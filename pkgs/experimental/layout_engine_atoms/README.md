![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/layout-engine-atoms/">
        <img src="https://img.shields.io/pypi/dm/layout-engine-atoms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine_atoms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine_atoms.svg"/></a>
    <a href="https://pypi.org/project/layout-engine-atoms/">
        <img src="https://img.shields.io/pypi/pyversions/layout-engine-atoms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/layout-engine-atoms/">
        <img src="https://img.shields.io/pypi/l/layout-engine-atoms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/layout-engine-atoms/">
        <img src="https://img.shields.io/pypi/v/layout-engine-atoms?label=layout-engine-atoms&color=green" alt="PyPI - layout-engine-atoms"/></a>
</p>

---

# Layout Engine Atoms & Vue Runtime

`layout-engine-atoms` packages Swarmauri's canonical UI atoms **and** ships the
official Vue thin wrapper for [`layout-engine`](../layout_engine). With this
package you can:

- prime manifest builders with curated atom presets, and
- mount a production-ready Vue dashboard that renders multi-page manifests, theme
  tokens, and websocket event streams without writing custom front-end plumbing.

> **Python compatibility**: Python 3.10–3.12

## Highlights

- **Curated atom registry** – every semantic role maps to an importable module,
  default props, and version metadata so manifests can stay declarative.
- **Vue thin wrapper** – packaged `mount_layout_app` helper mounts a drop-in
  dashboard with grid layout, shared theme tokens, plugin hooks, and optional
  realtime updates straight from FastAPI.
- **Swiss grid defaults** – spacing, typography, and layout tokens follow Swiss
  graphic design ratios for consistent output across HTML, PDF, or SVG targets.
- **Realtime ready** – websocket bridge understands `manifest.replace`,
  `manifest.patch`, and `manifest.refresh` payloads and can broadcast custom
  messages to connected clients.

---

## Installation

```bash
# uv
uv add layout-engine-atoms

# pip
pip install layout-engine-atoms
```

SwarmaKit Vue components are loaded from unpkg.com CDN at runtime.
An internet connection is required when the dashboard loads.
To use a different CDN or self-hosted assets, use `import_map_overrides` in `LayoutOptions`.

---

## Python: Working with Atom Presets

```python
from layout_engine_atoms import DEFAULT_ATOMS, build_registry

# Inspect the shipped presets
for role, spec in DEFAULT_ATOMS.items():
    print(role, spec.module, spec.export)

# Create a registry that layout-engine can consume
registry = build_registry()

# Override a role before passing it to layout_engine
registry.override(
    "viz:metric:kpi",
    module="@layout-app/atoms",
    defaults={"accent": "violet"},
)
```

The registry output can be fed directly into `layout-engine` manifest pipelines
when composing payloads for the runtime. See
[`examples/basic_usage.py`](../layout_engine/examples/basic_usage.py) for a
complete manifest construction flow.

### Quick manifest builder

To skip the lower-level layout primitives entirely, use the bundled helpers:

```python
from layout_engine_atoms.manifest import create_registry, quick_manifest, tile

registry = create_registry()
manifest = quick_manifest(
    [
        tile("hero", "swarmakit:vue:cardbased-list", span="full", props={"cards": [...]}),
        tile("summary", "swarmakit:vue:data-summary", span="half", props={"data": [...]}),
        tile("activity", "swarmakit:vue:activity-indicators", span="half", props={"type": "success"}),
    ],
    registry=registry,
)

manifest_json = manifest.model_dump()
```

Tiles auto-place into a responsive grid (`full`, `half`, or explicit spans), the
viewport is inferred, and registry defaults merge into each tile's props.

If you prefer the authoring DSL, build a `table`/`row`/`col` structure and call
`quick_manifest_from_table(layout, tiles, ...)` for the same result.

---

## Vue Thin Wrapper

The Vue runtime lives under `layout_engine_atoms.runtime.vue` and ships both the
server-side helper and the browser bundle.

### One-line FastAPI mount

```python
from fastapi import FastAPI
from layout_engine_atoms.runtime.vue import mount_layout_app
from my_manifests import build_manifest

app = FastAPI()

mount_layout_app(
    app,
    manifest_builder=build_manifest,
    base_path="/dashboard",
    title="My Layout Engine Dashboard",
)
```

The helper ships the HTML shell, import map, and static bundles. Once mounted,
opening `/dashboard/` loads the packaged Vue runtime which automatically
fetches `/dashboard/manifest.json`.

---

## Examples

- **Simple manifest** – minimal script that builds a SwarmaKit manifest with
  layout-engine (`pkgs/experimental/layout_engine_atoms/examples/simple_demo`).
- **UiEvent Counter Demo** – showcases a single button triggering a Python
  handler and realtime counter patches
  (`pkgs/experimental/layout_engine_atoms/examples/events_demo`).
- **UiEvents Command Center** – richer control deck with multiple UiEvents,
  realtime bindings, and action logs
  (`pkgs/experimental/layout_engine_atoms/examples/event_hub_demo`).
- **Customer Success Command Center** – demonstrates multi-page manifests and
  realtime incident streaming via websocket patches
  (`pkgs/experimental/layout_engine_atoms/examples/customer_success`).
- **Hybrid SPA/MPA Demo** – mounts both a single-page and multi-page runtime in
  one FastAPI app, showcasing realtime updates
  (`pkgs/experimental/layout_engine_atoms/examples/hybrid_demo`).
- **Revenue Ops Command Center** – richer stream routing and manifest patches
  (`pkgs/experimental/layout_engine_atoms/examples/revenue_ops`).

You can run any example directly with `uvicorn`:

```bash
uv run --directory pkgs/experimental/layout_engine_atoms \
  --package layout-engine-atoms \
  uvicorn layout_engine_atoms.examples.simple_demo.server:app --reload
```

This demo mounts the packaged Vue shell and manifest under `/`. Run it with
`uvicorn layout_engine_atoms.examples.simple_demo.server:app --reload` and visit
`http://127.0.0.1:8000/` to view the dashboard.

```bash
uv run --directory pkgs/experimental/layout_engine_atoms \
  --package layout-engine-atoms \
  uvicorn examples.customer_success.server:app --reload
```

---

## Documentation

- [Embedding guide](docs/vue_embedding_guide.md)
- [Runtime README](src/layout_engine_atoms/runtime/vue/README.md)
- [Swiss grid theme tokens](docs/swiss_grid_theme.md)
- [Bundle guide](docs/vue_client_bundle.md)

---

## Development

```bash
uv sync --all-extras
# Python quality gates
uv run --directory pkgs/experimental/layout_engine_atoms --package layout-engine-atoms ruff check .
uv run --directory pkgs/experimental/layout_engine_atoms --package layout-engine-atoms pytest
```

**Note**: SwarmaKit components are loaded from CDN. No build step required for Vue assets.

---

## License

Apache License 2.0. See [LICENSE](./LICENSE) for full terms.
