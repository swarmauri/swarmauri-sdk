# swarmauri_distance_minkowski

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_distance_minkowski</strong></p>
<p align="center">Minkowski Distance for Swarmauri.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_distance_minkowski/"><img alt="pypi: swarmauri_distance_minkowski" src="https://img.shields.io/pypi/v/swarmauri_distance_minkowski"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/README.md#lifecycle-and-migration"><img alt="Lifecycle: deprecated" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=deprecated&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_distance_minkowski/"><img alt="Monthly PyPI downloads: swarmauri_distance_minkowski" src="https://img.shields.io/pypi/dm/swarmauri_distance_minkowski"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/README.md"><img alt="README hits: swarmauri_distance_minkowski" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_distance_minkowski/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Use it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

### Why This Package

`swarmauri_distance_minkowski` isolates this responsibility: Minkowski Distance for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/swarmauri_distance_minkowski/__init__.py) exposes `MinkowskiDistance`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_distance_minkowski` when your integration needs minkowski Distance for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `MinkowskiDistance`: Implementation of the IDistanceSimiliarity interface using the Minkowski

### Non-Goals

`swarmauri_distance_minkowski` owns minkowski Distance for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml) declares runtime dependencies including `scipy`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_distance_minkowski
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_distance_minkowski
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_distance_minkowski
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_distance_minkowski")
assert package.__name__ == "swarmauri_distance_minkowski"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_distance_minkowski`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_distance_minkowski")
assert package.__name__ == "swarmauri_distance_minkowski"
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_distance_minkowski` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/swarmauri_distance_minkowski/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_distance_minkowski` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_distance_minkowski` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `MinkowskiDistance`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_distance_minkowski` is located in `standards` and owns minkowski Distance for Swarmauri. Source-declared APIs include `MinkowskiDistance`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_distance_minkowski`.

Source-declared exports or types: `MinkowskiDistance`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/swarmauri_distance_minkowski/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.distances` → `MinkowskiDistance` → `swarmauri_distance_minkowski:MinkowskiDistance`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_distance_minkowski` are `scipy`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/swarmauri_distance_minkowski/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_distance_minkowski` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_distance_minkowski`, use the source-declared public interfaces (`MinkowskiDistance`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_distance_minkowski` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_distance_minkowski`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/swarmauri_distance_minkowski/__init__.py). The `swarmauri_distance_minkowski` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

- Re-exports the deprecated `MinkowskiDistance` compatibility shim.
- Emits a `DeprecationWarning` on import.
- Remains compatible only with Swarmauri packages earlier than `0.10.0`.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_distance_minkowski` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/tests/test_readme_example.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_distance_minkowski` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/swarmauri_distance_minkowski/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_distance_minkowski` provides minkowski Distance for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_distance_minkowski`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/swarmauri_distance_minkowski/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_distance_minkowski` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/swarmauri_distance_minkowski/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml) provide the supporting context for `swarmauri_distance_minkowski`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_distance_minkowski](https://pypi.org/project/swarmauri_distance_minkowski/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_distance_minkowski`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/standards/swarmauri_distance_minkowski` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_distance_minkowski` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_distance_minkowski` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_distance_minkowski` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Preferred import: `swarmauri_standard.metrics.LpMetric.LpMetric`
- Migration note: use `LpMetric(p=<order>)` for Minkowski semantics.

```python
from swarmauri_standard.metrics.LpMetric import LpMetric

metric = LpMetric(p=2)
distance = metric.distance([1.0, 2.0], [1.0, 2.0])
similarity = 1.0 if distance == 0.0 else 1.0 / (1.0 + distance)
```

```bash
pip install swarmauri_distance_minkowski
```

```bash
uv pip install swarmauri_distance_minkowski
```

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_distance_minkowski/NOTICE) for attribution.
<!-- readme-standards:end notices -->
