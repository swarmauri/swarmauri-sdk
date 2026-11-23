# swarmauri_keyprovider_file

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyprovider_file</strong></p>
<p align="center">File-backed key provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_file/"><img alt="pypi: swarmauri_keyprovider_file" src="https://img.shields.io/pypi/v/swarmauri_keyprovider_file"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_file/"><img alt="Monthly PyPI downloads: swarmauri_keyprovider_file" src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_file"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/README.md"><img alt="README hits: swarmauri_keyprovider_file" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_keyprovider_file/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`FileKeyProvider` is a file-backed implementation of the `KeyProviderBase`
interface. It persists each key beneath a `keys/<kid>/v<version>/` directory,
captures metadata in `meta.json`, and exports public material in PEM or JWK
form. The provider supports the same lifecycle semantics as the in-memory
providers, but every operation is durable on disk.

### Why This Package

`swarmauri_keyprovider_file` isolates this responsibility: File-backed key provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/__init__.py) exposes `FileKeyProvider`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_keyprovider_file` when your integration needs file-backed key provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Generate symmetric AES-256-GCM keys and asymmetric Ed25519, X25519, RSA
  (OAEP/PSS), or ECDSA (P-256) key material.
- Import existing keys while preserving private material when allowed by the
  selected `ExportPolicy`.
- Rotate versions in-place, destroy versions or entire keys, and list
  historical versions stored on disk.
- Publish public material as individual JWKs or aggregate JWKS documents and
  expose HKDF and random byte helpers.

### Non-Goals

`swarmauri_keyprovider_file` owns file-backed key provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_keyprovider_file

# Poetry
poetry add swarmauri_keyprovider_file

# uv
uv add swarmauri_keyprovider_file
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyprovider_file
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyprovider_file
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyprovider_file
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/docs/readme/quick_start.py).

```python
import asyncio
from tempfile import TemporaryDirectory

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)
from swarmauri_core.crypto.types import KeyUse


async def run_example() -> str:
    with TemporaryDirectory() as tmp:
        provider = FileKeyProvider(tmp)
        spec = KeySpec(
            klass=KeyClass.symmetric,
            alg=KeyAlg.AES256_GCM,
            uses=(KeyUse.ENCRYPT,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        )
        created = await provider.create_key(spec)
        provider2 = FileKeyProvider(tmp)
        loaded = await provider2.get_key(created.kid, include_secret=True)
        print(f"Loaded key: {loaded.kid}")


asyncio.run(run_example())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyprovider_file` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/docs/readme/usage.py).

```python
import asyncio
from tempfile import TemporaryDirectory

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)
from swarmauri_core.crypto.types import KeyUse


async def run_example() -> str:
    with TemporaryDirectory() as tmp:
        provider = FileKeyProvider(tmp)
        spec = KeySpec(
            klass=KeyClass.symmetric,
            alg=KeyAlg.AES256_GCM,
            uses=(KeyUse.ENCRYPT,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        )
        created = await provider.create_key(spec)
        provider2 = FileKeyProvider(tmp)
        loaded = await provider2.get_key(created.kid, include_secret=True)
        print(f"Loaded key: {loaded.kid}")


asyncio.run(run_example())
```
<!-- readme-standards:end example.usage -->

`FileKeyProvider` is asynchronous?every lifecycle method returns a
`KeyRef`. Use `include_secret=True` when retrieving keys that allow private
material export so symmetric key bytes are loaded from disk.

### Configuration

Configure `swarmauri_keyprovider_file` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyprovider_file` source raises `KeyError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_keyprovider_file` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `FileKeyProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_keyprovider_file` is located in `standards` and owns file-backed key provider for Swarmauri. Source-declared APIs include `FileKeyProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyprovider_file`.

Source-declared exports or types: `FileKeyProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.key_providers` → `file` → `swarmauri_keyprovider_file.FileKeyProvider:FileKeyProvider`
- `swarmauri.key_providers` → `FileKeyProvider` → `swarmauri_keyprovider_file.FileKeyProvider:FileKeyProvider`
<!-- readme-standards:end entry-points -->

The provider registers under the `swarmauri.key_providers` entry point as `FileKeyProvider`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyprovider_file` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_keyprovider_file` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_keyprovider_file`, use the source-declared public interfaces (`FileKeyProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyprovider_file` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyprovider_file`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/__init__.py). The `swarmauri_keyprovider_file` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyprovider_file` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyprovider_file` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_file_keyprovider_basic.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/tests/test_file_keyprovider_basic.py)
- [tests/test_file_keyprovider_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/tests/test_file_keyprovider_functional.py)
- [tests/test_file_keyprovider_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/tests/test_file_keyprovider_perf.py)
- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/tests/test_readme_example.py)
- [tests/test_rfc5869_hkdf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/tests/test_rfc5869_hkdf.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyprovider_file` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_keyprovider_file` provides file-backed key provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_keyprovider_file`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyprovider_file` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml) provide the supporting context for `swarmauri_keyprovider_file`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_keyprovider_file](https://pypi.org/project/swarmauri_keyprovider_file/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_keyprovider_file` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_keyprovider_file` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyprovider_file` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyprovider_file` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyprovider_file` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_file/NOTICE) for attribution.
<!-- readme-standards:end notices -->
