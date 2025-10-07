![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/layout-engine/">
        <img src="https://img.shields.io/pypi/dm/layout-engine" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine.svg"/></a>
    <a href="https://pypi.org/project/layout-engine/">
        <img src="https://img.shields.io/pypi/pyversions/layout-engine" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/layout-engine/">
        <img src="https://img.shields.io/pypi/l/layout-engine" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/layout-engine/">
        <img src="https://img.shields.io/pypi/v/layout-engine?label=layout-engine&color=green" alt="PyPI - layout-engine"/></a>
</p>

---

# Layout Engine (Core)

`layout-engine` is a Swiss Grid design inspired, format-agnostic rendering engine that powers Server-Side Rendering (SSR), Static Site Generation (SSG), and offline exports from a unified component model. The package provides strongly-typed contracts for sites, pages, grids, tiles, and component registries so downstream applications can orchestrate layouts without being tied to a specific UI framework.

> **Python compatibility:** officially supports Python 3.10, 3.11, and 3.12.

## Features

- **Contract-driven architecture** – abstract base classes define the interfaces for rendering, exporting, and serving layout primitives.
- **Atomic component & micro-frontend registries** – manage SSR-ready components and remote module manifests with predictable defaults.
- **Format agnostic targets** – render HTML, SVG, PDF, and code artifacts using interchangeable exporters.
- **Extensible site composition** – compose grids, tiles, and slots declaratively with Pydantic specs for validation and serialization.
- **Optional realtime bridge** – opt into FastAPI, Uvicorn, and WebSocket extras for live preview or event streaming.

## Installation

Choose the workflow that matches your tooling. Extras are available for realtime server capabilities (`server`) and PDF generation (`pdf`).

```bash
# uv
uv add layout-engine
uv add layout-engine[server]  # for FastAPI/WebSocket extras
uv add layout-engine[pdf]     # for Playwright-powered exports

# pip
pip install layout-engine
pip install "layout-engine[server]"
pip install "layout-engine[pdf]"
```

## Quick Start

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
    # ComponentSpec(role="kpi", defaults={...}),
])

# Author the grid
tiles = [TileSpec(id="kpi_revenue", role="kpi", min_w=240)]
grid = GridSpec(cols=12, gap_x=16, gap_y=12, tiles=tiles)
page = Page(id="dashboard", grid=grid)
site = Site(id="marketing", pages=[page])

# Build manifest and render (SSR)
builder = ManifestBuilder(components=components)
manifest = builder.build({"site": site})
html = HtmlExporter().render(manifest)
print(html[:200])
```

## Core Concepts

- **First-class objects** – `site`, `page`, `slot`, `grid`, `tile`, `component`, and `remote` provide the building blocks for any layout.
- **Contracts** – objects expose `.render(...)`, `.export(...)`, and optional `.server(...)` methods to support SSR, SSG, and service endpoints.
- **Registries** – manage atomic component defaults and micro-frontend remotes with predictable merge semantics.

## Development

```bash
uv sync --all-extras
uv run --directory experimental/layout_engine --package layout-engine ruff check .
uv run --directory experimental/layout_engine --package layout-engine pytest -q
```

## License

Apache License 2.0. See [LICENSE](./LICENSE) for full terms.
