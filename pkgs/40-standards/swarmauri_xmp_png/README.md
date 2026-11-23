# swarmauri_xmp_png

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_xmp_png</strong></p>
<p align="center">PNG handler for embedding and extracting XMP packets in Swarmauri runtimes.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_xmp_png/"><img alt="pypi: swarmauri_xmp_png" src="https://img.shields.io/pypi/v/swarmauri_xmp_png"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_xmp_png/"><img alt="Monthly PyPI downloads: swarmauri_xmp_png" src="https://img.shields.io/pypi/dm/swarmauri_xmp_png"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/README.md"><img alt="README hits: swarmauri_xmp_png" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_xmp_png/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_xmp_png` packages the production-grade `PNGXMP` handler. It reads, writes, and removes XMP packets stored in uncompressed iTXt chunks that follow Adobe's keyword guidance, making it immediately compatible with downstream asset pipelines.

### Why This Package

- **Dynamic discovery** ? the handler is automatically registered with `DynamicBase` consumers via inheritance.
- **Standards alignment** ? PNG metadata lives in an iTXt chunk per ISO 16684 guidance.
- **Predictable behavior** ? read/write/remove flows mirror each other so pipelines remain idempotent.

### When to Use

Choose `swarmauri_xmp_png` when your integration needs pNG handler for embedding and extracting XMP packets in Swarmauri runtimes. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Registry-ready** ? inherits from `EmbedXmpBase` so Swarmauri's dynamic registry can auto-discover the handler.
- **Spec compliant** ? emits iTXt chunks with the `XML:com.adobe.xmp` keyword and UTF-8 payloads.
- **Safety guards** ? `_ensure_xml` performs a minimal RDF/XML check before embedding metadata.

### Non-Goals

`swarmauri_xmp_png` owns pNG handler for embedding and extracting XMP packets in Swarmauri runtimes. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_xmp_png

# uv
uv add swarmauri_xmp_png
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_xmp_png
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_xmp_png
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_xmp_png
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/docs/readme/quick_start.py).

```python
from pathlib import Path

from swarmauri_xmp_png import PNGXMP

handler = PNGXMP()
image_path = Path("example.png")
xmp_packet = (
    "<x:xmpmeta xmlns:x='adobe:ns:meta/'>"
    "<rdf:RDF>...</rdf:RDF></x:xmpmeta>"
)

# Embed an XMP packet
updated_bytes = handler.write_xmp(image_path.read_bytes(), xmp_packet)
image_path.write_bytes(updated_bytes)

# Verify the packet can be recovered
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Remove XMP if necessary
clean_bytes = handler.remove_xmp(updated_bytes)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_xmp_png` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/docs/readme/usage.py).

```python
from pathlib import Path

from swarmauri_xmp_png import PNGXMP

handler = PNGXMP()
image_path = Path("example.png")
xmp_packet = (
    "<x:xmpmeta xmlns:x='adobe:ns:meta/'>"
    "<rdf:RDF>...</rdf:RDF></x:xmpmeta>"
)

# Embed an XMP packet
updated_bytes = handler.write_xmp(image_path.read_bytes(), xmp_packet)
image_path.write_bytes(updated_bytes)

# Verify the packet can be recovered
restored_xml = handler.read_xmp(updated_bytes)
print(restored_xml)

# Remove XMP if necessary
clean_bytes = handler.remove_xmp(updated_bytes)
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_xmp_png` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/swarmauri_xmp_png/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_xmp_png` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_xmp_png` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `PNGXMP`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_xmp_png` is located in `standards` and owns pNG handler for embedding and extracting XMP packets in Swarmauri runtimes. Source-declared APIs include `PNGXMP`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_xmp_png`.

Source-declared exports or types: `PNGXMP`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/swarmauri_xmp_png/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.xmp_handlers` → `PNGXMP` → `swarmauri_xmp_png:PNGXMP`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_xmp_png` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/swarmauri_xmp_png/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `EmbedXMP`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_xmp_png`, use the source-declared public interfaces (`PNGXMP`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_xmp_png` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_xmp_png`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/swarmauri_xmp_png/__init__.py). The `swarmauri_xmp_png` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_xmp_png` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_xmp_png` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_png_handler.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/tests/test_png_handler.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_xmp_png` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/swarmauri_xmp_png/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_xmp_png` provides pNG handler for embedding and extracting XMP packets in Swarmauri runtimes; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_xmp_png`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/swarmauri_xmp_png/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_xmp_png` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/swarmauri_xmp_png/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml) provide the supporting context for `swarmauri_xmp_png`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_xmp_png](https://pypi.org/project/swarmauri_xmp_png/)
<!-- readme-standards:end project-links -->

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_xmp_png`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_xmp_png` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_xmp_png` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_xmp_png` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_xmp_png` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_xmp_png` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_xmp_png/NOTICE) for attribution.
<!-- readme-standards:end notices -->
