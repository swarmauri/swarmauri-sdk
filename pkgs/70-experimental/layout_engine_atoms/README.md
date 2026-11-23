# layout_engine_atoms

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>layout_engine_atoms</strong></p>
<p align="center">Curated atom presets and registries for layout-engine.</p>
<p align="center">
<a href="https://pypi.org/project/layout_engine_atoms/"><img alt="pypi: layout_engine_atoms unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=layout_engine_atoms%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/pyproject.toml"><img alt="Source version: 0.1.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/pyproject.toml"><img alt="Layer: experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/layout_engine_atoms/"><img alt="pypi downloads: layout_engine_atoms: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=layout_engine_atoms%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/README.md"><img alt="README hits: layout_engine_atoms" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/70-experimental/layout_engine_atoms/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`layout-engine-atoms` packages Swarmauri's canonical UI atoms **and** ships the
official Vue thin wrapper for [`layout-engine`](../layout_engine). With this
package you can:

- prime manifest builders with curated atom presets, and
- mount a production-ready Vue dashboard that renders multi-page manifests, theme
  tokens, and websocket event streams without writing custom front-end plumbing.

> **Python compatibility**: Python 3.10?3.12

### Why This Package

`layout_engine_atoms` isolates this responsibility: Curated atom presets and registries for layout-engine. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/src/layout_engine_atoms/__init__.py) exposes `AtomPreset`, `AtomPresetCatalog`, `DEFAULT_ATOMS`, `DEFAULT_PRESETS`, `IAtomCatalog`, `LayoutOptions`, `ManifestTile`, `PRESET_VERSION`, `RealtimeBinding`, `RealtimeChannel`, `RealtimeOptions`, `RouterOptions`, `SUPPORTED_CATALOGS`, `ScriptSpec`, `UIHooks`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `layout_engine_atoms` when your integration needs curated atom presets and registries for layout-engine. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Curated atom registry** ? every semantic role maps to an importable module,
  default props, and version metadata so manifests can stay declarative.
- **Vue thin wrapper** ? packaged `mount_layout_app` helper mounts a drop-in
  dashboard with grid layout, shared theme tokens, plugin hooks, and optional
  realtime updates straight from Starlette.
- **Swiss grid defaults** ? spacing, typography, and layout tokens follow Swiss
  graphic design ratios for consistent output across HTML, PDF, or SVG targets.
- **Realtime ready** ? websocket bridge understands `manifest.replace`,
  `manifest.patch`, and `manifest.refresh` payloads and can broadcast custom
  messages to connected clients.

### Non-Goals

`layout_engine_atoms` owns curated atom presets and registries for layout-engine. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/pyproject.toml) declares runtime dependencies including `layout-engine`, `starlette`, `uvicorn`, `httpx`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
# uv
uv add layout-engine-atoms

# pip
pip install layout-engine-atoms
```

SwarmaKit Vue components are loaded from unpkg.com CDN at runtime.
An internet connection is required when the dashboard loads.
To use a different CDN or self-hosted assets, use `import_map_overrides` in `LayoutOptions`.

#### uv

<!-- readme-standards:begin installation.uv -->
`layout_engine_atoms` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`layout_engine_atoms` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`layout_engine_atoms` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/layout_engine_atoms
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.sh](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/docs/readme/quick_start.sh).

```bash
uv run --directory pkgs/70-experimental/layout_engine_atoms \
  --package layout-engine-atoms \
  uvicorn examples.simple_demo.server:app --reload
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `layout_engine_atoms` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.sh](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/docs/readme/usage.sh).

```bash
uv run --directory pkgs/70-experimental/layout_engine_atoms \
  --package layout-engine-atoms \
  uvicorn examples.simple_demo.server:app --reload
```
<!-- readme-standards:end example.usage -->

- **Simple manifest** ? minimal script that builds a SwarmaKit manifest with
  layout-engine (`pkgs/70-experimental/layout_engine_atoms/examples/simple_demo`).
- **UiEvent Counter Demo** ? showcases a single button triggering a Python
  handler and realtime counter patches
  (`pkgs/70-experimental/layout_engine_atoms/examples/events_demo`).
- **UiEvents Command Center** ? richer control deck with multiple UiEvents,
  realtime bindings, and action logs
  (`pkgs/70-experimental/layout_engine_atoms/examples/event_hub_demo`).
- **Customer Success Command Center** ? demonstrates multi-page manifests and
  realtime incident streaming via websocket patches
  (`pkgs/70-experimental/layout_engine_atoms/examples/customer_success`).
- **Hybrid SPA/MPA Demo** ? mounts both a single-page and multi-page runtime in
  one Starlette app, showcasing realtime updates
  (`pkgs/70-experimental/layout_engine_atoms/examples/hybrid_demo`).
- **Revenue Ops Command Center** ? richer stream routing and manifest patches
  (`pkgs/70-experimental/layout_engine_atoms/examples/revenue_ops`).

You can run any example directly with `uvicorn`:


This demo mounts the packaged Vue shell and manifest under `/`. Visit
`http://127.0.0.1:8000/` to view the dashboard.

```bash
uv run --directory pkgs/70-experimental/layout_engine_atoms \
  --package layout-engine-atoms \
  uvicorn examples.events_demo.server:app --reload
```

### Configuration

Configure `layout_engine_atoms` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/src/layout_engine_atoms/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `layout_engine_atoms` source raises `HTTPException`, `KeyError`, `PayloadValidationError`, `RuntimeError`, `TypeError`, `ValueError`, `WebSocketDisconnect`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `layout_engine_atoms` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AtomPreset`, `AtomPresetCatalog`, `DEFAULT_ATOMS`, `DEFAULT_PRESETS`, `IAtomCatalog`, `LayoutOptions`, `ManifestTile`, `PRESET_VERSION`, `RealtimeBinding`, `RealtimeChannel`, `RealtimeOptions`, `RouterOptions`, `SUPPORTED_CATALOGS`, `ScriptSpec`, `UIHooks`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`layout_engine_atoms` is located in `experimental` and owns curated atom presets and registries for layout-engine. Source-declared APIs include `AtomPreset`, `AtomPresetCatalog`, `DEFAULT_ATOMS`, `DEFAULT_PRESETS`, `IAtomCatalog`, `LayoutOptions`, `ManifestTile`, `PRESET_VERSION`, `RealtimeBinding`, `RealtimeChannel`, `RealtimeOptions`, `RouterOptions`, `SUPPORTED_CATALOGS`, `ScriptSpec`, `UIHooks`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `layout_engine_atoms`.

Source-declared exports or types: `AtomPreset`, `AtomPresetCatalog`, `DEFAULT_ATOMS`, `DEFAULT_PRESETS`, `IAtomCatalog`, `LayoutOptions`, `ManifestTile`, `PRESET_VERSION`, `RealtimeBinding`, `RealtimeChannel`, `RealtimeOptions`, `RouterOptions`, `SUPPORTED_CATALOGS`, `ScriptSpec`, `UIHooks`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/src/layout_engine_atoms/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `layout_engine_atoms` are `layout-engine`, `starlette`, `uvicorn`, `httpx`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/src/layout_engine_atoms/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `layout_engine_atoms` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `layout_engine_atoms`, use the source-declared public interfaces (`AtomPreset`, `AtomPresetCatalog`, `DEFAULT_ATOMS`, `DEFAULT_PRESETS`, `IAtomCatalog`, `LayoutOptions`, `ManifestTile`, `PRESET_VERSION`, `RealtimeBinding`, `RealtimeChannel`, `RealtimeOptions`, `RouterOptions`, `SUPPORTED_CATALOGS`, `ScriptSpec`, `UIHooks`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `layout_engine_atoms` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `layout_engine_atoms`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/src/layout_engine_atoms/__init__.py). The `layout_engine_atoms` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `layout_engine_atoms` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `layout_engine_atoms` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_atom_catalogs.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/tests/test_atom_catalogs.py)
- [tests/test_catalog.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/tests/test_catalog.py)
- [tests/test_manifest_helpers.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/tests/test_manifest_helpers.py)
- [tests/test_runtime_events.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/tests/test_runtime_events.py)
- [tests/test_security.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/tests/test_security.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `layout_engine_atoms` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/src/layout_engine_atoms/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `layout_engine_atoms` provides curated atom presets and registries for layout-engine; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `layout_engine_atoms`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/src/layout_engine_atoms/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `layout_engine_atoms` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Embedding guide](docs/vue_embedding_guide.md)
- [Runtime README](src/layout_engine_atoms/runtime/vue/README.md)
- [Swiss grid theme tokens](docs/swiss_grid_theme.md)
- [Bundle guide](docs/vue_client_bundle.md)

### Related Packages

- [layout_engine](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine/README.md): Swiss-grid inspired, format-agnostic layout engine with SSR+SSG, atom & MFE registries.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: layout_engine_atoms](https://pypi.org/project/layout_engine_atoms/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `layout_engine_atoms`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

```bash
uv sync --all-extras
# Python quality gates
uv run --directory pkgs/70-experimental/layout_engine_atoms --package layout-engine-atoms ruff check .
uv run --directory pkgs/70-experimental/layout_engine_atoms --package layout-engine-atoms pytest
```

**Note**: SwarmaKit components are loaded from CDN. No build step required for Vue assets.

### Notes for Maintainers

**Python: Working with Atom Presets**

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

**Quick manifest builder**

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

**Vue Thin Wrapper**

The Vue runtime lives under `layout_engine_atoms.runtime.vue` and ships both the
server-side helper and the browser bundle.

**One-line Starlette mount**

```python
from starlette.applications import Starlette
from layout_engine_atoms.runtime.vue import mount_layout_app
from my_manifests import build_manifest

app = Starlette()

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

## Governance

### Ownership and Decision Making

Changes to `layout_engine_atoms` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`layout_engine_atoms` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `layout_engine_atoms` source version is `0.1.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/LICENSE).
<!-- readme-standards:end license -->

Apache License 2.0. See [LICENSE](./LICENSE) for full terms.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/layout_engine_atoms/NOTICE) for attribution.
<!-- readme-standards:end notices -->
