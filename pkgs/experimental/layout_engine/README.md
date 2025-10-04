# Layout Engine (Core)

**Swiss Grid Design–inspired, format‑agnostic layout engine for SSR + SSG with atomic component & MFE registries.**

This is the core package. It is intentionally framework‑agnostic and designed to be extended by downstream consumers.

## Concepts

- **First‑class objects**: `site`, `page`, `slot`, `grid`, `tile`, `component`, `remote`.
- **Contracts**: every first‑class object participates in *one or more* of the following contracts:
  - `.render(...)` — server render (SSR shells for Web GUI / host hydration).
  - `.export(...)` — offline artifact export (PDF/SVG/HTML/code).
  - `.server(...)` — (optional) endpoints/routers (e.g., WS bridge, import maps, `manifest.json` route).
- **Registries**:
  - **Atomic Component Registry** — role → component spec with defaults and prop merging.
  - **MFE Registry** — import‑map aware micro‑frontend remotes.

## Architecture Principles

- **Core vs Implementation** — core stays small, with clear ABCs/specs; downstream projects supply implementations.
- **Format‑agnostic** — targets `svg`, `html`, `pdf`, plus `vue`, `svelte`, `react` shells.
- **SSR websocket** — optional event bridge for in‑browser refreshing.
- **MPA + SPA** supported; SSR shells work for either.
- **No legacy shims** — do not add backwards‑compatibility layers.

## Package Layout

Each first‑class object has its own module folder with at least:
- `spec.py`, `default.py`, `base.py`, `shortcuts.py`, `decorators.py`
- Some also include: `bindings.py`, `resolver.py`

## Minimal Example (downstream consumer)

```python
from layout_engine.site import Site, Page
from layout_engine.grid import GridSpec
from layout_engine.tiles import TileSpec, make_tile
from layout_engine.components import ComponentRegistry
from layout_engine.manifest import ManifestBuilder
from layout_engine.targets.media import HtmlExporter

# Configure components
components = ComponentRegistry()
components.register_many([
    # ComponentSpec(role="kpi", defaults={...}), ...
])

# Author
tiles = [TileSpec(id="kpi_revenue", role="kpi", min_w=240)]
grid = GridSpec(cols=12, gap_x=16, gap_y=12, tiles=[...])
page = Page(id="dashboard", grid=grid)

# Build manifest and render (SSR)
builder = ManifestBuilder(components=components)
manifest = builder.build({"page": page})
html = HtmlExporter().render(manifest)
```

## Contracts in Code

- **ABCs** in `*/base.py` define the interfaces (`@abstractmethod`) used across the engine.
- **Defaults** in `*/default.py` provide concrete, production‑ready implementations with low boilerplate.
- **Specs** are Pydantic models — serializable, easy to validate, and stable over the wire.

## Development

```bash
uv sync --all-extras
uv run ruff check .
uv run pytest -q
```

## License

Apache 2.0 — see `LICENSE`.
