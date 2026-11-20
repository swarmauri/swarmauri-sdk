# EmbedXMP

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>EmbedXMP</strong></p>
<p align="center">Dynamic XMP embed/read/remove orchestration for Swarmauri handlers.</p>
<p align="center">
<a href="https://pypi.org/project/EmbedXMP/"><img alt="pypi: EmbedXMP" src="https://img.shields.io/pypi/v/EmbedXMP"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml"><img alt="Layer: plugins" src="https://img.shields.io/static/v1?label=Layer&amp;message=plugins&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/EmbedXMP/"><img alt="Monthly PyPI downloads: EmbedXMP" src="https://img.shields.io/pypi/dm/EmbedXMP"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/README.md"><img alt="README hits: EmbedXMP" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/plugins/EmbedXMP/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

EmbedXMP collects every installed `EmbedXmpBase` implementation, discovers them via Swarmauri's dynamic registry, and exposes a unified manager that can embed, read, or remove XMP packets without worrying about container formats.

### Why This Package

`EmbedXMP` isolates this responsibility: Dynamic XMP embed/read/remove orchestration for Swarmauri handlers. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/EmbedXMP/__init__.py) exposes `EmbedXMP`, `embed`, `embed_file`, `read`, `read_file_xmp`, `remove`, `remove_file_xmp`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `EmbedXMP` when your integration needs dynamic XMP embed/read/remove orchestration for Swarmauri handlers. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Dynamic discovery** - lazily imports modules named `swarmauri_xmp_*` and collects subclasses registered under `EmbedXmpBase`.
- **Unified interface** - delegates to the first handler whose `supports` method confirms compatibility with the payload.
- **Convenience wrappers** - module-level helpers (`embed`, `read`, `remove`) keep high-level workflows succinct.
- **Async-friendly APIs** - integrate inside event loops without blocking when calling out to plugin hooks.
- **Media-format coverage** - load handlers for PNG, GIF, JPEG, SVG, WEBP, TIFF, PDF, and MP4 assets through extras.

### Non-Goals

`EmbedXMP` owns dynamic XMP embed/read/remove orchestration for Swarmauri handlers. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-xmp-png`. Read the example’s inputs and service requirements before execution.

### Installation

**Using uv**

```bash
uv add EmbedXMP
```

**Using pip**

```bash
pip install EmbedXMP
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add EmbedXMP
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install EmbedXMP
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add EmbedXMP
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/docs/readme/quick_start.py).

```python
from pathlib import Path

from EmbedXMP import EmbedXMP, embed, embed_file, read, read_file_xmp

manager = EmbedXMP()
image = Path("example.png")
packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Embed into the file in place.
embed_file(image, packet)

# Inspect metadata via the manager API.
xmp_text = manager.read(image.read_bytes(), str(image))
print(xmp_text)

# Remove metadata from the file when it is no longer required.
manager.remove(image.read_bytes(), str(image))
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `EmbedXMP` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/docs/readme/usage.py).

```python
from pathlib import Path

from EmbedXMP import EmbedXMP, embed, embed_file, read, read_file_xmp

manager = EmbedXMP()
image = Path("example.png")
packet = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF>...</rdf:RDF></x:xmpmeta>"""

# Embed into the file in place.
embed_file(image, packet)

# Inspect metadata via the manager API.
xmp_text = manager.read(image.read_bytes(), str(image))
print(xmp_text)

# Remove metadata from the file when it is no longer required.
manager.remove(image.read_bytes(), str(image))
```
<!-- readme-standards:end example.usage -->

> **Note**
> You can provide either a `path` or a `hint` keyword argument when calling
> `embed`, `read`, or `remove` to help the manager pick the correct handler. The
> values are interchangeable as long as they match when both are supplied.

**Async orchestration**

EmbedXMP's manager can be shared inside asynchronous workflows by deferring media-aware work to plugin hooks:

```python
import asyncio
from pathlib import Path

from EmbedXMP import EmbedXMP, embed


async def embed_all(paths: list[str], packet: str) -> None:
    manager = EmbedXMP()
    for path in paths:
        data = Path(path).read_bytes()
        await asyncio.to_thread(embed, data, packet, hint=path)


asyncio.run(embed_all(["one.png", "two.svg"], "<x:xmpmeta>...</x:xmpmeta>"))
```

### Configuration

Configure `EmbedXMP` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/EmbedXMP/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `EmbedXMP` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `EmbedXMP` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `EmbedXMP`, `embed`, `embed_file`, `read`, `read_file_xmp`, `remove`, `remove_file_xmp`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`EmbedXMP` is located in `plugins` and owns dynamic XMP embed/read/remove orchestration for Swarmauri handlers. Source-declared APIs include `EmbedXMP`, `embed`, `embed_file`, `read`, `read_file_xmp`, `remove`, `remove_file_xmp`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `EmbedXMP`.

Source-declared exports or types: `EmbedXMP`, `embed`, `embed_file`, `read`, `read_file_xmp`, `remove`, `remove_file_xmp`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/EmbedXMP/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `EmbedXMP` are `swarmauri-core`, `swarmauri-base`, `swarmauri-xmp-png`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/EmbedXMP/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `EmbeddedSigner`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `EmbedXMP`, use the source-declared public interfaces (`EmbedXMP`, `embed`, `embed_file`, `read`, `read_file_xmp`, `remove`, `remove_file_xmp`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `EmbedXMP` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `EmbedXMP`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/EmbedXMP/__init__.py). The `EmbedXMP` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `EmbedXMP` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `EmbedXMP` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_embed_xmp.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/tests/test_embed_xmp.py)
- [tests/test_plugin_reexports.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/tests/test_plugin_reexports.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `EmbedXMP` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/EmbedXMP/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `EmbedXMP` provides dynamic XMP embed/read/remove orchestration for Swarmauri handlers; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `EmbedXMP`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/EmbedXMP/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `EmbedXMP` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/EmbedXMP/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml) provide the supporting context for `EmbedXMP`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_xmp_png](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_xmp_png/README.md): PNG handler for embedding and extracting XMP packets in Swarmauri runtimes.

### Project Links

<!-- readme-standards:begin project-links -->
- [Changelog](https://github.com/swarmauri/swarmauri-sdk/releases)
- [Discussions](https://github.com/orgs/swarmauri/discussions)
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/EmbedXMP#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Issues](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/EmbedXMP)
- [pypi: EmbedXMP](https://pypi.org/project/EmbedXMP/)
<!-- readme-standards:end project-links -->

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/EmbedXMP>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/EmbedXMP#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
- Discussions: <https://github.com/orgs/swarmauri/discussions>

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `EmbedXMP`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/plugins/EmbedXMP` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `EmbedXMP` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `EmbedXMP` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`EmbedXMP` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `EmbedXMP` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/plugins/EmbedXMP/NOTICE) for attribution.
<!-- readme-standards:end notices -->
