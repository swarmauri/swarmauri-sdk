# swamauri_metric_wasserstein

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swamauri_metric_wasserstein</strong></p>
<p align="center">Wasserstein metric plugin for Swarmauri vector comparisons.</p>
<p align="center">
<a href="https://pypi.org/project/swamauri_metric_wasserstein/"><img alt="pypi: swamauri_metric_wasserstein" src="https://img.shields.io/pypi/v/swamauri_metric_wasserstein"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/README.md#lifecycle-and-migration"><img alt="Lifecycle: deprecated" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=deprecated&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swamauri_metric_wasserstein/"><img alt="Monthly PyPI downloads: swamauri_metric_wasserstein" src="https://img.shields.io/pypi/dm/swamauri_metric_wasserstein"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/README.md"><img alt="README hits: swamauri_metric_wasserstein" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swamauri_metric_wasserstein/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
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

`swamauri_metric_wasserstein` provides a Swarmauri-compatible metric class
for computing the first Wasserstein distance (Earth Mover's Distance) between
numeric vectors.

### Why This Package

`swamauri_metric_wasserstein` isolates this responsibility: Wasserstein metric plugin for Swarmauri vector comparisons. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/swamauri_metric_wasserstein/__init__.py) exposes `WassersteinMetric`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swamauri_metric_wasserstein` when your integration needs wasserstein metric plugin for Swarmauri vector comparisons. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Implements `WassersteinMetric` as a `MetricBase` plugin.
- Computes distance using a built-in pure-Python 1D Wasserstein implementation.
- Includes helper methods for batched `distances` and `similarities`.
- Supports Python 3.10, 3.11, and 3.12.

### Non-Goals

`swamauri_metric_wasserstein` owns wasserstein metric plugin for Swarmauri vector comparisons. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv pip install swamauri_metric_wasserstein
```

```bash
pip install swamauri_metric_wasserstein
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swamauri_metric_wasserstein
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swamauri_metric_wasserstein
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swamauri_metric_wasserstein
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/docs/readme/quick_start.py).

```python
from swamauri_metric_wasserstein import WassersteinMetric
from swarmauri_standard.vectors.Vector import Vector

vector_a = Vector(value=[0.0, 1.0, 2.0])
vector_b = Vector(value=[0.0, 1.0, 2.0])

distance_calculator = WassersteinMetric()

distance = distance_calculator.distance(vector_a, vector_b)
similarity = distance_calculator.similarity(vector_a, vector_b)

print(f"Distance: {distance}")
print(f"Similarity: {similarity}")
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swamauri_metric_wasserstein` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/docs/readme/usage.py).

```python
from swamauri_metric_wasserstein import WassersteinMetric
from swarmauri_standard.vectors.Vector import Vector

vector_a = Vector(value=[0.0, 1.0, 2.0])
vector_b = Vector(value=[0.0, 1.0, 2.0])

distance_calculator = WassersteinMetric()

distance = distance_calculator.distance(vector_a, vector_b)
similarity = distance_calculator.similarity(vector_a, vector_b)

print(f"Distance: {distance}")
print(f"Similarity: {similarity}")
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swamauri_metric_wasserstein` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/swamauri_metric_wasserstein/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swamauri_metric_wasserstein` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swamauri_metric_wasserstein` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `WassersteinMetric`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swamauri_metric_wasserstein` is located in `standards` and owns wasserstein metric plugin for Swarmauri vector comparisons. Source-declared APIs include `WassersteinMetric`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swamauri_metric_wasserstein`.

Source-declared exports or types: `WassersteinMetric`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/swamauri_metric_wasserstein/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.metrics` → `WassersteinMetric` → `swamauri_metric_wasserstein:WassersteinMetric`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swamauri_metric_wasserstein` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/swamauri_metric_wasserstein/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swamauri_metric_wasserstein` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swamauri_metric_wasserstein`, use the source-declared public interfaces (`WassersteinMetric`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swamauri_metric_wasserstein` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swamauri_metric_wasserstein`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/swamauri_metric_wasserstein/__init__.py). The `swamauri_metric_wasserstein` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swamauri_metric_wasserstein` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swamauri_metric_wasserstein` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/tests/test_readme_example.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swamauri_metric_wasserstein` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/swamauri_metric_wasserstein/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swamauri_metric_wasserstein` provides wasserstein metric plugin for Swarmauri vector comparisons; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swamauri_metric_wasserstein`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/swamauri_metric_wasserstein/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swamauri_metric_wasserstein` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/swamauri_metric_wasserstein/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml) provide the supporting context for `swamauri_metric_wasserstein`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swamauri_metric_wasserstein](https://pypi.org/project/swamauri_metric_wasserstein/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swamauri_metric_wasserstein` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swamauri_metric_wasserstein` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swamauri_metric_wasserstein` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swamauri_metric_wasserstein` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Current state: no active standalone Wasserstein replacement package exists in the workspace.
- Migration path: keep this deprecated package only for compatibility, or vendor a project-specific metric until a correctly named active package is published.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swamauri_metric_wasserstein/NOTICE) for attribution.
<!-- readme-standards:end notices -->
