# swarmauri_skill_local

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_skill_local</strong></p>
<p align="center">Local skill-root resolver for Swarmauri.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_skill_local/"><img alt="pypi: swarmauri_skill_local" src="https://img.shields.io/pypi/v/swarmauri_skill_local"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_skill_local/"><img alt="Monthly PyPI downloads: swarmauri_skill_local" src="https://img.shields.io/pypi/dm/swarmauri_skill_local"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/README.md"><img alt="README hits: swarmauri_skill_local" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_skill_local/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

LocalSkill resolves Swarmauri skills from configured local skill roots.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_skill_local)](https://pepy.tech/projects/swarmauri_skill_local)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_local.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_skill_local/)
[![Python Versions](https://img.shields.io/pypi/pyversions/swarmauri_skill_local)](https://pypi.org/project/swarmauri_skill_local/)
[![License](https://img.shields.io/pypi/l/swarmauri_skill_local)](https://pypi.org/project/swarmauri_skill_local/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_skill_local)](https://pypi.org/project/swarmauri_skill_local/)

### Why This Package

`swarmauri_skill_local` isolates this responsibility: Local skill-root resolver for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py) exposes `LocalSkill`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_skill_local` when your integration needs local skill-root resolver for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Provides a first-class Swarmauri standard component.
- Uses existing Swarmauri core and base contracts.
- Keeps skill and agent composition language-agnostic at the package boundary.

### Non-Goals

`swarmauri_skill_local` owns local skill-root resolver for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_skill_local
```

```bash
pip install swarmauri_skill_local
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_skill_local
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_skill_local
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_skill_local
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/docs/readme/quick_start.py).

```python
from swarmauri_skill_local import LocalSkill

skill = LocalSkill.from_name("my-skill", roots=["./skills"])
print(skill.name)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_skill_local` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/docs/readme/usage.py).

```python
from swarmauri_skill_local import LocalSkill

skill = LocalSkill.from_name("my-skill", roots=["./skills"])
print(skill.name)
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_skill_local` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_skill_local` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py).

### Best Practices

Use the explicit `swarmauri_skill_local` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `LocalSkill`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_skill_local` is located in `standards` and owns local skill-root resolver for Swarmauri. Source-declared APIs include `LocalSkill`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_skill_local`.

Source-declared exports or types: `LocalSkill`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.skills` → `LocalSkill` → `swarmauri_skill_local:LocalSkill`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_skill_local` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_skill_local` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_skill_local`, use the source-declared public interfaces (`LocalSkill`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_skill_local` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_skill_local`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py). The `swarmauri_skill_local` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_skill_local` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_skill_local` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for local skill-root resolver for Swarmauri.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_skill_local` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_skill_local` provides local skill-root resolver for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_skill_local`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_skill_local` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/swarmauri_skill_local/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml) provide the supporting context for `swarmauri_skill_local`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_skill_local](https://pypi.org/project/swarmauri_skill_local/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

This package is part of the Swarmauri SDK monorepo.

### Development Setup

Work from the `pkgs/standards/swarmauri_skill_local` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_skill_local` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_skill_local` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_skill_local` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_skill_local` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_skill_local/NOTICE) for attribution.
<!-- readme-standards:end notices -->
