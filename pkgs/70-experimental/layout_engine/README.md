# layout_engine

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>layout_engine</strong></p>
<p align="center">Swiss-grid inspired, format-agnostic layout engine with SSR+SSG, atom &amp; MFE registries.</p>
<p align="center">
<a href="https://pypi.org/project/layout_engine/"><img alt="pypi: layout_engine unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=layout_engine%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/pyproject.toml"><img alt="Source version: 0.1.1.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.1.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/pyproject.toml"><img alt="Layer: experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/layout_engine/"><img alt="pypi downloads: layout_engine: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=layout_engine%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/README.md"><img alt="README hits: layout_engine" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/70-experimental/layout_engine/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`layout-engine` is a Swiss Grid design inspired, format-agnostic rendering engine that powers Server-Side Rendering (SSR), Static Site Generation (SSG), and offline exports from a unified atom model. The package provides strongly-typed contracts for sites, pages, grids, tiles, and atom registries so downstream applications can orchestrate layouts without being tied to a specific UI framework.

> **Python compatibility:** officially supports Python 3.10, 3.11, and 3.12.

### Why This Package

`layout_engine` isolates this responsibility: Swiss-grid inspired, format-agnostic layout engine with SSR+SSG, atom & MFE registries. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/src/layout_engine/__init__.py) exposes `AtomRegistry`, `AtomSpec`, `Block`, `ChannelManifest`, `CodeExporter`, `Column`, `DEFAULT_BASELINE_MULTIPLIER`, `DEFAULT_TOKEN_WEIGHTS`, `EventEnvelope`, `EventRouter`, `ExplicitGridResolver`, `Frame`, `Framework`, `GridBuilder`, `GridSpec`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `layout_engine` when your integration needs swiss-grid inspired, format-agnostic layout engine with SSR+SSG, atom & MFE registries. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Contract-driven architecture** ? abstract base classes define the interfaces for rendering, exporting, and serving layout primitives.
- **Atom & micro-frontend registries** ? manage SSR-ready atoms and remote module manifests with predictable defaults.
- **Format agnostic targets** ? render HTML, SVG, PDF, and code artifacts using interchangeable exporters.
- **Extensible site composition** ? compose grids, tiles, and slots declaratively with Pydantic specs for validation and serialization.
- **Optional realtime bridge** ? opt into Starlette, Uvicorn, and WebSocket extras for live preview or event streaming.

### Non-Goals

`layout_engine` owns swiss-grid inspired, format-agnostic layout engine with SSR+SSG, atom & MFE registries. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/pyproject.toml) declares runtime dependencies including `jinja2`, `pydantic`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the workflow that matches your tooling. Extras are available for realtime server capabilities (`server`) and PDF generation (`pdf`).

```bash
# uv
uv add layout-engine
uv add layout-engine[server]  # for Starlette/WebSocket extras
uv add layout-engine[pdf]     # for Playwright-powered exports

# pip
pip install layout-engine
pip install "layout-engine[server]"
pip install "layout-engine[pdf]"
```

#### uv

<!-- readme-standards:begin installation.uv -->
`layout_engine` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`layout_engine` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`layout_engine` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/layout_engine
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

The manifest merges atom defaults with any props provided on `TileSpec`
instances, so runtime atoms receive fully-prepared payloads.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/docs/readme/quick_start.py).

```python
from layout_engine import (
    AtomRegistry,
    AtomSpec,
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    quick_manifest_from_table,
    row,
    table,
)
from layout_engine.targets.media import HtmlExporter

atoms = AtomRegistry()
atoms.register(AtomSpec(role="stat", module="@demo/metric"))

tiles = [
    TileSpec(
        id="stat_revenue",
        role="stat",
        props={"label": "Revenue", "value": "$1.2M"},
    ),
    TileSpec(
        id="stat_growth",
        role="stat",
        props={"label": "Growth", "value": "18%"},
    ),
]

layout = table(
    row(
        col(block("stat_revenue"), size=SizeToken.m),
        col(block("stat_growth"), size=SizeToken.m),
    )
)

manifest = quick_manifest_from_table(
    layout,
    Viewport(width=960, height=540),
    tiles,
    atoms_registry=atoms,
)

HtmlExporter(title="Stats Overview").export(manifest, out="stats.html")
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `layout_engine` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/docs/readme/usage.py).

```python
from layout_engine import (
    AtomRegistry,
    AtomSpec,
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    quick_manifest_from_table,
    row,
    table,
)
from layout_engine.targets.media import HtmlExporter

atoms = AtomRegistry()
atoms.register(AtomSpec(role="stat", module="@demo/metric"))

tiles = [
    TileSpec(
        id="stat_revenue",
        role="stat",
        props={"label": "Revenue", "value": "$1.2M"},
    ),
    TileSpec(
        id="stat_growth",
        role="stat",
        props={"label": "Growth", "value": "18%"},
    ),
]

layout = table(
    row(
        col(block("stat_revenue"), size=SizeToken.m),
        col(block("stat_growth"), size=SizeToken.m),
    )
)

manifest = quick_manifest_from_table(
    layout,
    Viewport(width=960, height=540),
    tiles,
    atoms_registry=atoms,
)

HtmlExporter(title="Stats Overview").export(manifest, out="stats.html")
```
<!-- readme-standards:end example.usage -->

- [`examples/basic_usage.py`](./examples/basic_usage.py) ? minimal quick-start
  script that writes a manifest JSON file and exports an HTML preview.
- [`examples/dashboard.py`](./examples/dashboard.py) ? larger end-to-end demo
  showcasing multiple roles and a custom theme.

Run either script with:

```bash
uv run --directory experimental/layout_engine --package layout-engine python examples/basic_usage.py
uv run --directory experimental/layout_engine --package layout-engine python examples/dashboard.py
```

Both scripts print their output locations so you can open the generated
artifacts directly from the repository.

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/src/layout_engine/__init__.py) references configuration keys `PATH_INFO`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `layout_engine` source raises `KeyError`, `RuntimeError`, `TypeError`, `ValidationError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `layout_engine` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AtomRegistry`, `AtomSpec`, `Block`, `ChannelManifest`, `CodeExporter`, `Column`, `DEFAULT_BASELINE_MULTIPLIER`, `DEFAULT_TOKEN_WEIGHTS`, `EventEnvelope`, `EventRouter`, `ExplicitGridResolver`, `Frame`, `Framework`, `GridBuilder`, `GridSpec`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`layout_engine` is located in `experimental` and owns swiss-grid inspired, format-agnostic layout engine with SSR+SSG, atom & MFE registries. Source-declared APIs include `AtomRegistry`, `AtomSpec`, `Block`, `ChannelManifest`, `CodeExporter`, `Column`, `DEFAULT_BASELINE_MULTIPLIER`, `DEFAULT_TOKEN_WEIGHTS`, `EventEnvelope`, `EventRouter`, `ExplicitGridResolver`, `Frame`, `Framework`, `GridBuilder`, `GridSpec`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `layout_engine`.

Source-declared exports or types: `AtomRegistry`, `AtomSpec`, `Block`, `ChannelManifest`, `CodeExporter`, `Column`, `DEFAULT_BASELINE_MULTIPLIER`, `DEFAULT_TOKEN_WEIGHTS`, `EventEnvelope`, `EventRouter`, `ExplicitGridResolver`, `Frame`, `Framework`, `GridBuilder`, `GridSpec`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/src/layout_engine/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `layout_engine` are `jinja2`, `pydantic`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/src/layout_engine/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `layout_engine_atoms`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `layout_engine`, use the source-declared public interfaces (`AtomRegistry`, `AtomSpec`, `Block`, `ChannelManifest`, `CodeExporter`, `Column`, `DEFAULT_BASELINE_MULTIPLIER`, `DEFAULT_TOKEN_WEIGHTS`, `EventEnvelope`, `EventRouter`, `ExplicitGridResolver`, `Frame`, `Framework`, `GridBuilder`, `GridSpec`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `layout_engine` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `layout_engine`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/src/layout_engine/__init__.py). The `layout_engine` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `layout_engine` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `layout_engine` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_atoms_registry.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/tests/test_atoms_registry.py)
- [tests/test_authoring_helpers.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/tests/test_authoring_helpers.py)
- [tests/test_events_channels.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/tests/test_events_channels.py)
- [tests/test_grid_tokens.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/tests/test_grid_tokens.py)
- [tests/test_manifest_contract.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/tests/test_manifest_contract.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `layout_engine` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/src/layout_engine/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `layout_engine` provides swiss-grid inspired, format-agnostic layout engine with SSR+SSG, atom & MFE registries; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `layout_engine`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/src/layout_engine/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `layout_engine` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/src/layout_engine/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/pyproject.toml) provide the supporting context for `layout_engine`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

No direct local dependency was identified for `layout_engine` in this checkout. External dependency names are listed under Prerequisites; packages in the same directory layer are not automatically dependencies.

### Project Links

<!-- readme-standards:begin project-links -->
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Repository](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/70-experimental/layout_engine)
- [pypi: layout_engine](https://pypi.org/project/layout_engine/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `layout_engine`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/70-experimental/layout_engine` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

```bash
uv sync --all-extras
uv run --directory experimental/layout_engine --package layout-engine ruff check .
uv run --directory experimental/layout_engine --package layout-engine pytest -q
```

### Notes for Maintainers

**Core Concepts**

- **First-class objects** ? `site`, `page`, `slot`, `grid`, `tile`, `atom`, and `remote` provide the building blocks for any layout.
- **Contracts** ? objects expose `.render(...)`, `.export(...)`, and optional `.server(...)` methods to support SSR, SSG, and service endpoints.
- **Registries** ? manage atom defaults and micro-frontend remotes with predictable merge semantics.
- **Site-aware routing helpers** ? `layout_engine.targets.SiteRouter` produces SSR HTML shells, manifest JSON payloads, and ESM
  import maps you can bind directly to Starlette or other HTTP framework route handlers.

**Unified manifest schema**

Every manifest emitted by Layout Engine adheres to the following structure:

```json
{
  "kind": "layout_manifest",
  "version": "2025.10",
  "viewport": {"width": 1280, "height": 720},
  "grid": {
    "row_height": 160,
    "gap_x": 24,
    "gap_y": 24,
    "columns": [{"size": {"value": 1, "unit": "fr", "min_px": 72}}],
    "baseline_unit": 12,
    "tokens": {"columns": "sgd:columns:12", "baseline": "sgd:baseline:12"}
  },
  "tiles": [
    {
      "id": "hero",
      "role": "swarmakit:vue:hero-card",
      "frame": {"x": 0, "y": 0, "w": 1280, "h": 320},
      "props": {"title": "Quarterly Highlights", "accent": "indigo", "size": "lg"},
      "atom": {
        "role": "swarmakit:vue:hero-card",
        "module": "@swarmakit/vue",
        "export": "HeroCard",
        "framework": "vue",
        "package": "@swarmakit/vue",
        "family": "swarmakit",
        "version": "0.0.22",
        "defaults": {"size": "md"},
        "tokens": {"variant": "hero"},
        "registry": {
          "name": "swarmakit",
          "framework": "vue",
          "version": "0.0.22"
        }
      }
    }
  ],
  "site": {
    "active_page": "dashboard",
    "navigation": {"base_path": "/"},
    "pages": [
      {"id": "dashboard", "route": "/", "title": "Dashboard"},
      {"id": "catalog", "route": "/catalog", "title": "Catalog"}
    ]
  },
  "channels": [
    {
      "id": "ui.events",
      "scope": "page",
      "topic": "page:{page_id}:ui",
      "description": "UI event bus",
      "payload_schema": {"type": "object"},
      "meta": {"transport": "ws"}
    }
  ],
  "ws_routes": [
    {"path": "/ws/ui", "channels": ["ui.events"], "description": "Multiplexed UI events"}
  ],
  "etag": "61d6d0d0b6f3c5f5..."
}
```

Key highlights:

- **Grid tokens** capture Swiss-grid presets so wrappers can align columns/gaps/baselines without recomputing measurements.
- **Atom metadata** preserves registry origin and package details, enabling thin wrappers (Vue, Svelte, React) to auto-import `@swarmakit/{framework}` modules with no bespoke glue.
- **Site block** embeds page navigation so multi-page experiences hydrate from a single manifest.
- **Channels & websocket routes** describe mux topics so runtime shells subscribe automatically.

**Serving manifests and import maps**

`SiteRouter` centralizes the endpoints required by single-page and multi-page applications. Use
`SiteRouter.manifest_json(...)` to return the manifest for a page, and
`SiteRouter.import_map(...)` to build an import map from a `RemoteRegistry`. Because the router is
framework-agnostic, you can wire these helpers into whichever ASGI/WSGI stack you prefer without
additional adapters.

**End-to-end Vue SPA + MPA integration**

The following walkthrough shows how to create a Vue codebase that consumes both single-page and
multi-page manifests generated by `layout-engine`, serves an import-map aware shell, reacts to query
parameters, and streams tile-level events over a multiplexed WebSocket transport.

**1. Compose registries and site metadata**

Start by defining the atom registry (for local role ? module mappings) and the remote registry
that powers the import map consumed by Vue's module loader. Defaults defined on each atom are
merged with tile props every time a manifest is built, so downstream atoms always receive a
complete prop payload.

**Registering SwarmaKit atoms**

`layout-engine` does not automatically install SwarmaKit presets. When `layout_engine_atoms` is
available you can populate an `AtomRegistry` using the helper introduced in v0.1.0:

```python
from layout_engine import AtomRegistry, register_swarma_atoms

atoms = register_swarma_atoms(AtomRegistry(), catalog="vue")

# optional overrides ? merged instead of replaced
atoms.override("swarmakit:vue:button", defaults={"size": "lg"})
```

The helper lazily imports `layout_engine_atoms.catalog` so projects without SwarmaKit remain
functional. Overrides use additive merges (defaults/tokens/registry) to avoid clobbering preset
values.

```python
from layout_engine import AtomRegistry, AtomSpec
from layout_engine.mfe.default import RemoteRegistry
from layout_engine.mfe.spec import Remote
from layout_engine.site.spec import PageSpec, SiteSpec, SlotSpec

atoms = AtomRegistry()
atoms.register(
    AtomSpec(
        role="dashboard.hero",
        module="@layout-app/atoms",
        export="HeroCard",
        version="2.1.0",
        defaults={"accent": "indigo", "density": "comfortable"},
    )
)
atoms.register(
    AtomSpec(
        role="catalog.item",
        module="@layout-app/atoms",
        export="CatalogTile",
        defaults={"showPrice": True, "badgeStyle": "pill"},
    )
)

remotes = RemoteRegistry(
    (
        Remote(
            id="spa-shell",
            framework="vue",
            entry="https://cdn.example.com/spa/entry.js",
            exposed="./App",
        ),
        Remote(
            id="mpa-shell",
            framework="vue",
            entry="https://cdn.example.com/mpa/entry.js",
            exposed="./Page",
        ),
    )
)

site = SiteSpec(
    base_path="/",
    pages=(
        PageSpec(
            id="spa-dashboard",
            route="/",
            title="Realtime Dashboard",
            slots=(SlotSpec(name="root", role="dashboard.hero", remote="spa-shell"),),
            page_vm={"state": {"filters": {"status": "active"}}},
        ),
        PageSpec(
            id="catalog-list",
            route="/catalog",
            title="Product Catalog",
            slots=(SlotSpec(name="root", role="catalog.item", remote="mpa-shell"),),
        ),
        PageSpec(
            id="catalog-detail",
            route="/catalog/:item_id",
            title="Product Detail",
            slots=(SlotSpec(name="root", role="catalog.item", remote="mpa-shell"),),
        ),
    ),
)
```

**2. Build manifests that react to SPA and MPA context**

Use the authoring DSL to convert structured layouts into manifests. The manifest builder receives a
`PageSpec` plus a context assembled by `SiteRouter`, which includes route params, query parameters,
and any `page_vm` defaults. This is the hook for computing stateful props (selected items, applied
filters, etc.) before merging with the registry defaults.

```python
from typing import Mapping, Any

from layout_engine import (
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    quick_manifest_from_table,
    row,
    table,
)
from layout_engine.manifest.spec import Manifest

catalog_source = {
    "items": [
        {"id": "sku-001", "name": "Synthwave Jacket", "price": 180},
        {"id": "sku-002", "name": "Neon Sneakers", "price": 120},
        {"id": "sku-003", "name": "Retro Shades", "price": 60},
    ]
}


def build_manifest(page: PageSpec, ctx: Mapping[str, Any]) -> Manifest:
    route = ctx["route"]
    query = route.get("query", {})
    params = route.get("params", {})
    base_state = dict(ctx.get("state", {}))
    # Merge defaults with incoming query params to derive view state
    active_filters = {
        **base_state.get("filters", {}),
        **{k: v for k, v in query.items() if k in {"status", "search", "page"}},
    }

    if page.id == "spa-dashboard":
        tiles = [
            TileSpec(
                id="hero",
                role="dashboard.hero",
                props={
                    "filters": active_filters,
                    "headline": "Realtime sales",
                    "kpi": {"value": "$1.8M", "trend": +12},
                },
            ),
        ]
    elif page.id == "catalog-list":
        # Apply search filter from query params for list rendering
        search_term = (query.get("search") or "").lower()
        filtered = [
            item
            for item in catalog_source["items"]
            if search_term in item["name"].lower()
        ]
        tiles = [
            TileSpec(
                id=item["id"],
                role="catalog.item",
                props={
                    "itemId": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "isActive": False,
                },
            )
            for item in filtered
        ]
    else:
        # Detail view resolves the selected item id from params
        item_id = params.get("item_id")
        item = next(
            (item for item in catalog_source["items"] if item["id"] == item_id),
            None,
        )
        tiles = [
            TileSpec(
                id="detail",
                role="catalog.item",
                props={
                    "itemId": item_id,
                    "name": item.get("name") if item else "Missing",
                    "price": item.get("price") if item else 0,
                    "isActive": True,
                },
            )
        ]

    layout = table(
        row(
            *(col(block(tile.id), size=SizeToken.l) for tile in tiles)
        )
    )
    manifest = quick_manifest_from_table(
        layout,
        Viewport(width=1440, height=900),
        tiles,
        atoms_registry=atoms,
    )
    return manifest
```

The snippet shows how atom defaults (`showPrice`, `badgeStyle`) are merged with dynamic props
(`isActive`, `filters`) before the manifest reaches the client. State changes (for example selecting
an item or refining a search query) happen entirely in the context step?no Vue-specific logic is
required on the server to keep props synchronized.

**3. Serve shells, manifests, and import maps with SiteRouter**

Bind the manifest builder to a `SiteRouter` so both SPA and MPA routes can be served from the same
Starlette application. The SPA fetches a single manifest keyed by `PageSpec`, whereas
the MPA endpoints use `manifest_json_for_path` so each HTML page can request its own manifest.

```python
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from layout_engine.site.default import bind_page_builder
from layout_engine.targets.webgui.router import SiteRouter

router = SiteRouter(site=site, page_manifest_fn=bind_page_builder(build_manifest))

async def spa_shell(_request: Request) -> HTMLResponse:
    return HTMLResponse(router.render_shell(site.pages[0]))


async def spa_manifest(request: Request) -> JSONResponse:
    data = router.manifest_json(
        site.pages[0],
        query=dict(request.query_params),
    )
    return JSONResponse(content=data)


async def catalog_shell(_request: Request) -> HTMLResponse:
    page = site.pages[1]
    return HTMLResponse(router.render_shell(page))


async def catalog_manifest(request: Request) -> JSONResponse:
    data = router.manifest_json_for_path(
        "/catalog",
        query=dict(request.query_params),
    )
    return JSONResponse(content=data)


async def catalog_detail_shell(request: Request) -> HTMLResponse:
    page = site.pages[2]
    return HTMLResponse(router.render_shell(page, params=request.path_params))


async def catalog_detail_manifest(request: Request) -> JSONResponse:
    item_id = request.path_params["item_id"]
    data = router.manifest_json_for_path(
        f"/catalog/{item_id}",
        query=dict(request.query_params),
    )
    return JSONResponse(content=data)


async def import_map(_request: Request) -> JSONResponse:
    return JSONResponse(router.import_map(remotes))


app = Starlette(
    routes=[
        Route("/", spa_shell),
        Route("/spa/manifest.json", spa_manifest),
        Route("/catalog", catalog_shell),
        Route("/catalog/manifest.json", catalog_manifest),
        Route("/catalog/{item_id}", catalog_detail_shell),
        Route("/catalog/{item_id}/manifest.json", catalog_detail_manifest),
        Route("/import-map.json", import_map),
    ]
)
```

This wiring enables:

- **SPA manifest** ? `GET /spa/manifest.json?status=paused` updates dashboard props while keeping a
  single HTML shell.
- **MPA manifests** ? each catalog page calls `/catalog/.../manifest.json` so static HTML routes can
  hydrate independently, while still sharing atom defaults from the registry.
- **Import maps** ? Vue clients can consume the generated map before calling `createApp` to ensure
  micro-frontend remotes resolve correctly.

**4. Vue client consumption with query params and navigation**

In the Vue SPA entry point, request the manifest and import map, register slots, and watch the URL's
query parameters to re-fetch manifests whenever filters change. For the MPA flows, the same manifest
loader runs on each page load, so a full navigation to `/catalog/sku-001` will resolve the detail
manifest that already includes the requested item.

```ts
// spa/main.ts
import { createApp, ref } from "vue";
import App from "./App.vue";

async function loadManifest(endpoint: string, query: URLSearchParams) {
  const res = await fetch(`${endpoint}?${query.toString()}`);
  return res.json();
}

async function bootstrap() {
  const importMap = await (await fetch("/import-map.json")).json();
  const script = document.createElement("script");
  script.type = "importmap";
  script.textContent = JSON.stringify(importMap);
  document.head.appendChild(script);

  const query = new URLSearchParams(window.location.search);
  const manifest = ref(await loadManifest("/spa/manifest.json", query));

  const app = createApp(App, { manifest });
  app.mount("#app");

  window.addEventListener("popstate", async () => {
    const nextQuery = new URLSearchParams(window.location.search);
    manifest.value = await loadManifest("/spa/manifest.json", nextQuery);
  });
}

bootstrap();
```

MPA pages perform the same fetch using their page-specific manifest endpoint, so the detail view can
call `loadManifest(`/catalog/${itemId}/manifest.json`, new URLSearchParams(location.search))` and the
server will deliver props for the requested `itemId`.

Thin wrappers for React or Svelte follow identical steps: fetch the manifest, honour `manifest.grid.tokens`
when computing breakpoints, and import atoms using the `module`/`export` values stored in each tile's
`atom` block. Because registry metadata travels with the manifest, no framework-specific glue or
per-role switch statements are necessary.

**5. Event handling with multiplexed WebSockets**

Install the optional server extras (`layout-engine[server]`) plus the WebSocket JSON-RPC transport
(`swarmauri-transport-wsjsonrpcmux`). The transport acts as the mux that fans events in/out of the
`layout_engine.events` router, giving Vue atoms a consistent channel for publishing or
subscribing to tile state changes.

```python
import asyncio
from swarmauri_transport_wsjsonrpcmux import WsJsonrpcMuxTransport
from layout_engine.events.ws import EventRouter, InProcEventBus

event_bus = InProcEventBus()
events = EventRouter(event_bus)


async def rpc_handler(method: str, params: dict):
    if method == "layout.publish":
        topic, delivered = events.dispatch(params)
        return {"topic": topic, "delivered": delivered}
    if method == "layout.subscribe":
        # In a production system forward the subscription request to a broker.
        # Here we eagerly replay the last event if available.
        topic = params["topic"]
        last = event_bus.last(topic)
        return {"topic": topic, "last": last}
    raise ValueError(f"Unknown method: {method}")


async def start_mux():
    transport = WsJsonrpcMuxTransport()
    transport.set_rpc_handler(rpc_handler)
    async with transport.server(host="0.0.0.0", port=8765):
        await asyncio.Future()


# Start the mux task in the Starlette lifespan and cancel it on shutdown.
```

Vue clients connect using the matching mux client:

```ts
// spa/events.ts
const socket = new WebSocket("ws://localhost:8765");

socket.addEventListener("open", () => {
  socket.send(
    JSON.stringify({
      jsonrpc: "2.0",
      id: "init",
      method: "layout.subscribe",
      params: { topic: `site:${window.location.pathname}` },
    })
  );
});

export function publishTileEvent(slot: string, tileId: string, payload: Record<string, any>) {
  socket.send(
    JSON.stringify({
      jsonrpc: "2.0",
      id: crypto.randomUUID(),
      method: "layout.publish",
      params: {
        scope: "site",
        page: window.location.pathname,
        slot,
        tile: tileId,
        event: payload,
      },
    })
  );
}
```

When atoms invoke `publishTileEvent`, the event router validates the envelope, publishes to the
topic derived from `scope/page/slot/tile`, and any subscribed Vue atoms receive real-time
updates. Because `EventRouter.dispatch` accepts the same context that `SiteRouter` uses to build
manifests, the manifest props and WebSocket events stay aligned.

**6. Putting it together**

1. **Render shells** for each SPA/MPA page with `SiteRouter.render_shell(...)`.
2. **Serve manifests** via `manifest_json(...)` (SPA) and `manifest_json_for_path(...)` (MPA) so
   Vue can hydrate tiles with merged defaults, props, and query-derived state.
3. **Distribute import maps** generated from the `RemoteRegistry` so atom modules resolve
   consistently across pages.
4. **Leverage context** (`route.params`, `route.query`, `page_vm`) inside the manifest builder to
   support list filtering, `item_id` lookups, and other state transitions.
5. **Stream events** through the muxed WebSocket transport to coordinate user interactions or live
   telemetry across SPA and MPA boundaries.

With these pieces in place, a Vue frontend can seamlessly navigate between SPA and MPA routes, reuse
the same manifest-driven layout definitions, and react instantly to query parameter changes or
WebSocket events without duplicating atom metadata on the client.

---

## Governance

### Ownership and Decision Making

Changes to `layout_engine` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`layout_engine` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `layout_engine` source version is `0.1.1.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/LICENSE).
<!-- readme-standards:end license -->

Apache License 2.0. See [LICENSE](./LICENSE) for full terms.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/NOTICE) for attribution.
<!-- readme-standards:end notices -->
