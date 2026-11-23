# swarmauri_keyprovider_inmemory

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyprovider_inmemory</strong></p>
<p align="center">In-memory key provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_inmemory/"><img alt="pypi: swarmauri_keyprovider_inmemory" src="https://img.shields.io/pypi/v/swarmauri_keyprovider_inmemory?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_inmemory/"><img alt="Monthly PyPI downloads: swarmauri_keyprovider_inmemory" src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_inmemory?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/README.md"><img alt="README hits: swarmauri_keyprovider_inmemory" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_keyprovider_inmemory/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Volatile, in-memory key provider for Swarmauri. All key material is kept strictly in process memory (no disk writes). Ideal for testing, CI, and ephemeral gateways where persistence is not desired. Not intended for long-term or production storage of secrets.

### Why This Package

`swarmauri_keyprovider_inmemory` isolates this responsibility: In-memory key provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/swarmauri_keyprovider_inmemory/InMemoryKeyProvider.py) exposes `InMemoryKeyProvider`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_keyprovider_inmemory` when your integration needs in-memory key provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `InMemoryKeyProvider`: In-memory key provider for testing or ephemeral environments.

### Non-Goals

`swarmauri_keyprovider_inmemory` owns in-memory key provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python tooling:

```bash
pip install swarmauri_keyprovider_inmemory
```

```bash
poetry add swarmauri_keyprovider_inmemory
```

```bash
pip install uv
uv pip install swarmauri_keyprovider_inmemory
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyprovider_inmemory
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyprovider_inmemory
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyprovider_inmemory
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,  # optional, not enforced by the provider
    KeyClass,
    KeySpec,
    KeyUse,
)
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider


async def main() -> None:
    provider = InMemoryKeyProvider()

    # Create a symmetric key kept only in memory
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,  # optional hint ? not strictly enforced
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="session-key",
    )
    ref = await provider.create_key(spec)
    assert ref.kid and ref.version == 1
    # ref.material may be populated depending on export_policy

    # Rotate to get a new version, still in memory only
    ref2 = await provider.rotate_key(ref.kid)
    assert ref2.version == 2

    # List available versions
    versions = await provider.list_versions(ref.kid)
    print(versions)  # e.g., (1, 2)

    # Import existing key material
    imported = await provider.import_key(
        spec,
        material=b"\x00" * 32,
    )
    assert imported.version == 1

    # Fetch current version
    current = await provider.get_key(ref.kid)
    assert current.version == max(versions)

    # Destroy a specific version or the whole key
    await provider.destroy_key(ref.kid, version=1)  # delete only v1
    await provider.destroy_key(imported.kid)  # delete all versions

    # Utilities
    rand = await provider.random_bytes(16)
    okm = await provider.hkdf(b"ikm", salt=b"salt", info=b"ctx", length=32)
    print(len(rand), len(okm))


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyprovider_inmemory` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/docs/readme/usage.py).

```python
import asyncio

from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,  # optional, not enforced by the provider
    KeyClass,
    KeySpec,
    KeyUse,
)
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider


async def main() -> None:
    provider = InMemoryKeyProvider()

    # Create a symmetric key kept only in memory
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,  # optional hint ? not strictly enforced
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="session-key",
    )
    ref = await provider.create_key(spec)
    assert ref.kid and ref.version == 1
    # ref.material may be populated depending on export_policy

    # Rotate to get a new version, still in memory only
    ref2 = await provider.rotate_key(ref.kid)
    assert ref2.version == 2

    # List available versions
    versions = await provider.list_versions(ref.kid)
    print(versions)  # e.g., (1, 2)

    # Import existing key material
    imported = await provider.import_key(
        spec,
        material=b"\x00" * 32,
    )
    assert imported.version == 1

    # Fetch current version
    current = await provider.get_key(ref.kid)
    assert current.version == max(versions)

    # Destroy a specific version or the whole key
    await provider.destroy_key(ref.kid, version=1)  # delete only v1
    await provider.destroy_key(imported.kid)  # delete all versions

    # Utilities
    rand = await provider.random_bytes(16)
    okm = await provider.hkdf(b"ikm", salt=b"salt", info=b"ctx", length=32)
    print(len(rand), len(okm))


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Create and manage symmetric (or opaque/asymmetric placeholder) keys entirely in memory. The snippet below creates a new symmetric key and returns a `KeyRef` with material present when allowed by the export policy.

### Configuration

Configure `swarmauri_keyprovider_inmemory` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/swarmauri_keyprovider_inmemory/InMemoryKeyProvider.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyprovider_inmemory` source raises `KeyError`, `NotImplementedError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_keyprovider_inmemory` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `InMemoryKeyProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_keyprovider_inmemory` is located in `standards` and owns in-memory key provider for Swarmauri. Source-declared APIs include `InMemoryKeyProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyprovider_inmemory`.

Source-declared exports or types: `InMemoryKeyProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/swarmauri_keyprovider_inmemory/InMemoryKeyProvider.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.key_providers` → `inmemory` → `swarmauri_keyprovider_inmemory.InMemoryKeyProvider:InMemoryKeyProvider`
- `swarmauri.key_providers` → `InMemoryKeyProvider` → `swarmauri_keyprovider_inmemory.InMemoryKeyProvider:InMemoryKeyProvider`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyprovider_inmemory` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/swarmauri_keyprovider_inmemory/InMemoryKeyProvider.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `MediaSigner`, `swarmauri_certs_x509`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_keyprovider_inmemory`, use the source-declared public interfaces (`InMemoryKeyProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyprovider_inmemory` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyprovider_inmemory`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/swarmauri_keyprovider_inmemory/InMemoryKeyProvider.py). The `swarmauri_keyprovider_inmemory` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyprovider_inmemory` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyprovider_inmemory` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/tests/example/test_readme_usage.py)
- [tests/unit/test_inmemory_provider_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/tests/unit/test_inmemory_provider_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyprovider_inmemory` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/swarmauri_keyprovider_inmemory/InMemoryKeyProvider.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_keyprovider_inmemory` provides in-memory key provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_keyprovider_inmemory`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/swarmauri_keyprovider_inmemory/InMemoryKeyProvider.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyprovider_inmemory` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/swarmauri_keyprovider_inmemory/InMemoryKeyProvider.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml) provide the supporting context for `swarmauri_keyprovider_inmemory`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_keyprovider_inmemory` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Capabilities**

- Class support: `symmetric`, `asymmetric (opaque)`
- Features: `create`, `import`, `rotate`, `destroy`, `list_versions`, `get_key`, `random_bytes`, `hkdf`
- No persistence: data is lost when the process exits
- Not supported: JWK/JWKS export (will raise `NotImplementedError`)

**Security Considerations**

- Keys exist only for the lifetime of the Python process; restarting drops all material.
- No hardware isolation or disk persistence is provided.
- Use only for development, CI, or other ephemeral scenarios.

- Exported `KeyRef.material` presence depends on the `ExportPolicy`. Use `ExportPolicy.NONE` to prevent material from being surfaced to callers.
- For gateways, set this provider as the default to keep keys off disk in development and CI.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyprovider_inmemory` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyprovider_inmemory` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyprovider_inmemory` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/NOTICE) for attribution.
<!-- readme-standards:end notices -->
