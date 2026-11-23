# jaml

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>jaml</strong></p>
<p align="center">Swarmauri&#x27;s Canon Jaml Handler</p>
<p align="center">
<a href="https://pypi.org/project/jaml/"><img alt="pypi: jaml unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=jaml%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml"><img alt="Source version: 0.2.1.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.2.1.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml"><img alt="Layer: experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/jaml/"><img alt="pypi downloads: jaml: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=jaml%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/README.md"><img alt="README hits: jaml" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/70-experimental/jaml/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`jaml`: Swarmauri's Canon Jaml Handler

### Why This Package

`jaml` isolates this responsibility: Swarmauri's Canon Jaml Handler. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/jaml/__init__.py) exposes `check_extension`, `dump`, `dumps`, `load`, `loads`, `parser`, `render`, `resolve`, `round_trip_dump`, `round_trip_dumps`, `round_trip_load`, `round_trip_loads`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `jaml` when your integration needs swarmauri's Canon Jaml Handler. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `BaseNode`: declared in jaml/_ast_nodes.py
- `StartNode`: declared in jaml/_ast_nodes.py
- `SectionNode`: declared in jaml/_ast_nodes.py
- `SectionNameNode`: declared in jaml/_ast_nodes.py
- `TableArraySectionNode`: declared in jaml/_ast_nodes.py
- `TableArrayHeaderNode`: Represents a [[…]] table‑array section header.
- `ComprehensionHeaderNode`: declared in jaml/_ast_nodes.py
- `AssignmentNode`: declared in jaml/_ast_nodes.py

### Non-Goals

`jaml` owns swarmauri's Canon Jaml Handler. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml) declares runtime dependencies including `lark`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`jaml` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`jaml` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`jaml` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/jaml
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("jaml")
assert package.__name__ == "jaml"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `jaml`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("jaml")
assert package.__name__ == "jaml"
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `jaml` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/jaml/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `jaml` source raises `AttributeError`, `NotImplementedError`, `SyntaxError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `jaml` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `check_extension`, `dump`, `dumps`, `load`, `loads`, `parser`, `render`, `resolve`, `round_trip_dump`, `round_trip_dumps`, `round_trip_load`, `round_trip_loads`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`jaml` is located in `experimental` and owns swarmauri's Canon Jaml Handler. Source-declared APIs include `check_extension`, `dump`, `dumps`, `load`, `loads`, `parser`, `render`, `resolve`, `round_trip_dump`, `round_trip_dumps`, `round_trip_load`, `round_trip_loads`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `jaml`.

Source-declared exports or types: `check_extension`, `dump`, `dumps`, `load`, `loads`, `parser`, `render`, `resolve`, `round_trip_dump`, `round_trip_dumps`, `round_trip_load`, `round_trip_loads`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/jaml/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `jaml` are `lark`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/jaml/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `jaml` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `jaml`, use the source-declared public interfaces (`check_extension`, `dump`, `dumps`, `load`, `loads`, `parser`, `render`, `resolve`, `round_trip_dump`, `round_trip_dumps`, `round_trip_load`, `round_trip_loads`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `jaml` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `jaml`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/jaml/__init__.py). The `jaml` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `jaml` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `jaml` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/r8n/test_basic_references.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/tests/r8n/test_basic_references.py)
- [tests/r8n/test_circular_reference.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/tests/r8n/test_circular_reference.py)
- [tests/r8n/test_comments.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/tests/r8n/test_comments.py)
- [tests/r8n/test_conditional_table_blocks.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/tests/r8n/test_conditional_table_blocks.py)
- [tests/r8n/test_dynamic_static_reference.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/tests/r8n/test_dynamic_static_reference.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `jaml` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/jaml/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `jaml` provides swarmauri's Canon Jaml Handler; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `jaml`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/jaml/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `jaml` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/jaml/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml) provide the supporting context for `jaml`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

No direct local dependency was identified for `jaml` in this checkout. External dependency names are listed under Prerequisites; packages in the same directory layer are not automatically dependencies.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: jaml](https://pypi.org/project/jaml/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `jaml`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/70-experimental/jaml` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `jaml` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `jaml` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`jaml` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `jaml` source version is `0.2.1.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

The matching PyPI name belongs to an unrelated project. This source project is not represented by that registry release; use the checkout instructions and do not install the unrelated distribution as a substitute.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/jaml/NOTICE) for attribution.
<!-- readme-standards:end notices -->
