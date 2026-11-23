# swarmauri_typing

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_typing</strong></p>
<p align="center">Dynamic typing utilities for Swarmauri annotated unions, intersection metadata, and registry-driven component models.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_typing/"><img alt="pypi: swarmauri_typing" src="https://img.shields.io/pypi/v/swarmauri_typing"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml"><img alt="Layer: typing" src="https://img.shields.io/static/v1?label=Layer&amp;message=typing&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_typing/"><img alt="Monthly PyPI downloads: swarmauri_typing" src="https://img.shields.io/pypi/dm/swarmauri_typing"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/README.md"><img alt="README hits: swarmauri_typing" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/00-typing/swarmauri_typing/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_typing` provides typing utilities for Swarmauri's dynamic component model. It exposes annotated intersection and union helpers used by `swarmauri_base` to build Pydantic-compatible component unions from runtime registries.

### Why This Package

`swarmauri_typing` isolates the small dynamic typing helpers used by Swarmauri's component model. It lets foundational packages generate metadata-rich `Annotated` unions without coupling those helpers to a specific component family.

### When to Use

Use `swarmauri_typing` directly when you need dynamic `Annotated` type construction in a Swarmauri-compatible package. Most application developers interact with it indirectly through `swarmauri_base.ComponentBase`, `DynamicBase`, and `SubclassUnion`.

### Features

- `Intersection` creates an annotated union of common classes from multiple input types.
- `IntersectionMetadata` preserves the source classes used to build the intersection annotation.
- `UnionFactory` builds annotated union types from a user-supplied type lookup function.
- `UnionFactoryMetadata` records the source model or key used to build a dynamic union.
- Annotation extenders allow callers to attach additional metadata such as Pydantic discriminators.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_typing` owns dynamic typing utilities for Swarmauri annotated unions, intersection metadata, and registry-driven component models. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml) declares no direct runtime dependencies. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_typing
```

Install with `pip`:

```bash
pip install swarmauri_typing
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_typing
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_typing
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_typing
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/docs/readme/quick_start.py).

```python
from typing import get_args

from swarmauri_typing import Intersection, IntersectionMetadata


class Root:
    pass


class Left(Root):
    pass


class Right(Root):
    pass


Common = Intersection[Left, Right]
metadata = [
    item
    for item in get_args(Common)[1:]
    if isinstance(item, IntersectionMetadata)
]

assert metadata[0].classes == (Left, Right)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_typing` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/docs/readme/usage.py).

```python
from typing import get_args

from swarmauri_typing import Intersection, IntersectionMetadata


class Root:
    pass


class Left(Root):
    pass


class Right(Root):
    pass


Common = Intersection[Left, Right]
metadata = [
    item
    for item in get_args(Common)[1:]
    if isinstance(item, IntersectionMetadata)
]

assert metadata[0].classes == (Left, Right)
```
<!-- readme-standards:end example.usage -->

Create an intersection annotation:


Create a dynamic annotated union:

```python
from typing import Any

from swarmauri_typing import UnionFactory, UnionFactoryMetadata


class JsonStore:
    pass


class SqlStore:
    pass


def store_types(model_name: str) -> list[type]:
    if model_name == "Store":
        return [JsonStore, SqlStore]
    return []


StoreUnion = UnionFactory(store_types, name="store_union")["Store"]

assert any(
    isinstance(item, UnionFactoryMetadata) and item.name == "store_union"
    for item in getattr(StoreUnion, "__metadata__", ())
)
```

### Configuration

Configure `swarmauri_typing` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/swarmauri_typing/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_typing` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/swarmauri_typing/__init__.py).

### Best Practices

Use the explicit `swarmauri_typing` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `Intersection`, `IntersectionMetadata`, `UnionFactory`, `UnionFactoryMetadata`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_typing` is located in `typing` and owns dynamic typing utilities for Swarmauri annotated unions, intersection metadata, and registry-driven component models. Source-declared APIs include `Intersection`, `IntersectionMetadata`, `UnionFactory`, `UnionFactoryMetadata`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_typing`.

Source-declared exports or types: `Intersection`, `IntersectionMetadata`, `UnionFactory`, `UnionFactoryMetadata`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/swarmauri_typing/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_typing` are empty in the manifest. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/swarmauri_typing/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_base`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_typing`, use the source-declared public interfaces (`Intersection`, `IntersectionMetadata`, `UnionFactory`, `UnionFactoryMetadata`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_typing` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_typing`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/swarmauri_typing/__init__.py). The `swarmauri_typing` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_typing` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_typing` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_swarmauri_typing__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/tests/i9n/test_swarmauri_typing__init__.py)
- [tests/unit/test_Intersection.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/tests/unit/test_Intersection.py)
- [tests/unit/test_MetadataRepr.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/tests/unit/test_MetadataRepr.py)
- [tests/unit/test_UnionFactory.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/tests/unit/test_UnionFactory.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_typing` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/swarmauri_typing/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: What does UnionFactory do?**

A: `UnionFactory` builds an `Annotated[Union[...], ...]` type from a caller-provided lookup function. `swarmauri_base` uses this pattern for dynamic component subtype unions.

**Q: What does Intersection do?**

A: `Intersection` computes common classes from input types and returns an annotated type that carries `IntersectionMetadata`.

**Q: Do most application developers import this package directly?**

A: Usually no. Most users get this behavior through `swarmauri_base.DynamicBase` and `SubclassUnion`.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_typing`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/swarmauri_typing/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_typing` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/swarmauri_typing/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml) provide the supporting context for `swarmauri_typing`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Foundational packages:

- [swarmauri_base](https://pypi.org/project/swarmauri_base/) uses these typing helpers for dynamic component deserialization.
- [swarmauri_core](https://pypi.org/project/swarmauri_core/) provides the interface contracts for Swarmauri component families.
- [swarmauri](https://pypi.org/project/swarmauri/) provides the namespace importer and plugin discovery layer.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides first-party components that depend on the core/base typing model.

Component-kind packages that benefit from dynamic typing:

- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/)
- [swarmauri_crypto_composite](https://pypi.org/project/swarmauri_crypto_composite/)
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/)
- [swarmauri_storage_memory](https://pypi.org/project/swarmauri_storage_memory/)
- [swarmauri_transport_stdio](https://pypi.org/project/swarmauri_transport_stdio/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_typing](https://pypi.org/project/swarmauri_typing/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

When changing these helpers, keep the API small and compatible with Pydantic metadata usage in `swarmauri_base`, add focused tests for generated annotations, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).

### Development Setup

Work from the `pkgs/00-typing/swarmauri_typing` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Component Usage**

`swarmauri_base.DynamicBase` uses `UnionFactory` to turn registered component subtypes into discriminated unions. This lets models typed with `SubclassUnion[BaseComponent]` hydrate concrete subclasses from serialized payloads that include a `type` field.

```python
from pydantic import Field

from swarmauri_typing import UnionFactory


def component_types(model_name: str) -> list[type]:
    return []


SubclassUnion = UnionFactory(
    component_types,
    name="subclass_union",
    annotation_extenders=[Field(discriminator="type")],
)
```

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_typing` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_typing` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_typing` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/00-typing/swarmauri_typing/NOTICE) for attribution.
<!-- readme-standards:end notices -->
