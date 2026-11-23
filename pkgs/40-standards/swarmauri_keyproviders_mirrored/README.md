# swarmauri_keyproviders_mirrored

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyproviders_mirrored</strong></p>
<p align="center">Mirrored key provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/"><img alt="pypi: swarmauri_keyproviders_mirrored" src="https://img.shields.io/pypi/v/swarmauri_keyproviders_mirrored?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyproviders_mirrored/"><img alt="Monthly PyPI downloads: swarmauri_keyproviders_mirrored" src="https://img.shields.io/pypi/dm/swarmauri_keyproviders_mirrored?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/README.md"><img alt="README hits: swarmauri_keyproviders_mirrored" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_keyproviders_mirrored/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

An asynchronous failover key provider that keeps a primary provider as the
system of record while best-effort mirroring material to a secondary provider
for redundancy.

### Why This Package

`swarmauri_keyproviders_mirrored` isolates this responsibility: Mirrored key provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py) exposes `MirroredKeyProvider`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_keyproviders_mirrored` when your integration needs mirrored key provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Write operations (`create`, `import`, `rotate`, `destroy`) execute on the
  primary provider first and then mirror to the secondary provider when
  possible.
- `mirror_mode` governs what is replicated: `public_only` (default) mirrors only
  public material, `full` attempts to replicate private material when export
  policy allows, and `none` disables replication while retaining read
  failover.
- Read operations (`get_key`, `get_public_jwk`, `jwks`, `list_versions`,
  `random_bytes`, `hkdf`) favor the primary provider and fail over to the
  secondary provider when `fail_open_reads` is enabled.
- JWKS responses merge keys from both providers, preferring primary entries when
  the same `kid` appears in both sets.
- Maintains an in-memory mapping of mirrored key identifiers to coordinate
  destroy operations and failover reads?persist or rebuild this mapping if you
  need cross-process continuity.
- Optional extras add canonical JSON (`jsoncanon`) and CBOR (`cbor`) support for
  consumers that require deterministic encodings.

### Non-Goals

`swarmauri_keyproviders_mirrored` owns mirrored key provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-local`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_keyproviders_mirrored
```

```bash
poetry add swarmauri_keyproviders_mirrored
```

```bash
uv pip install swarmauri_keyproviders_mirrored
```

Enable extras for canonicalization when needed:

```bash
pip install swarmauri_keyproviders_mirrored[jsoncanon]
```

```bash
pip install swarmauri_keyproviders_mirrored[cbor]
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyproviders_mirrored
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyproviders_mirrored
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyproviders_mirrored
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_core.crypto.types import KeyUse
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_keyproviders_mirrored import MirroredKeyProvider


async def main() -> None:
    primary = LocalKeyProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(
        primary,
        secondary,
        mirror_mode="public_only",
        fail_open_reads=True,
    )

    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    created = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(created.kid, created.version)

    await primary.destroy_key(created.kid, created.version)
    mirrored = await provider.get_public_jwk(created.kid, created.version)

    assert mirrored["x"] == jwk["x"]
    print(
        "Failover retrieved Ed25519 key from secondary provider:",
        mirrored["kid"],
    )


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyproviders_mirrored` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/docs/readme/usage.py).

```python
import asyncio

from swarmauri_core.crypto.types import KeyUse
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_keyproviders_mirrored import MirroredKeyProvider


async def main() -> None:
    primary = LocalKeyProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(
        primary,
        secondary,
        mirror_mode="public_only",
        fail_open_reads=True,
    )

    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    created = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(created.kid, created.version)

    await primary.destroy_key(created.kid, created.version)
    mirrored = await provider.get_public_jwk(created.kid, created.version)

    assert mirrored["x"] == jwk["x"]
    print(
        "Failover retrieved Ed25519 key from secondary provider:",
        mirrored["kid"],
    )


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The provider mirrors newly created keys to the secondary provider and fails open
on reads when the primary becomes unavailable.


In the example above the primary key is destroyed after mirroring, forcing
`MirroredKeyProvider` to serve the public key from the secondary provider.
Although mirrored keys may have different `kid` values, the public material
remains identical and ready for verification.

### Configuration

Configure `swarmauri_keyproviders_mirrored` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyproviders_mirrored` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py).

### Best Practices

Use the explicit `swarmauri_keyproviders_mirrored` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `MirroredKeyProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_keyproviders_mirrored` is located in `standards` and owns mirrored key provider for Swarmauri. Source-declared APIs include `MirroredKeyProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyproviders_mirrored`.

Source-declared exports or types: `MirroredKeyProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.key_providers` → `mirrored` → `swarmauri_keyproviders_mirrored.MirroredKeyProvider:MirroredKeyProvider`
- `swarmauri.key_providers` → `MirroredKeyProvider` → `swarmauri_keyproviders_mirrored.MirroredKeyProvider:MirroredKeyProvider`
<!-- readme-standards:end entry-points -->

The provider registers under the `swarmauri.key_providers` entry point as
`MirroredKeyProvider`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyproviders_mirrored` are `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-local`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_keyproviders_mirrored` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_keyproviders_mirrored`, use the source-declared public interfaces (`MirroredKeyProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyproviders_mirrored` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyproviders_mirrored`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py). The `swarmauri_keyproviders_mirrored` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyproviders_mirrored` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyproviders_mirrored` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/tests/example/test_readme_example.py)
- [tests/i9n/test_failover_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/tests/i9n/test_failover_functional.py)
- [tests/perf/test_perf_get_key.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/tests/perf/test_perf_get_key.py)
- [tests/unit/test_mirrored_key_provider.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/tests/unit/test_mirrored_key_provider.py)
- [tests/unit/test_rfc7517.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/tests/unit/test_rfc7517.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyproviders_mirrored` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_keyproviders_mirrored` provides mirrored key provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_keyproviders_mirrored`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyproviders_mirrored` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/swarmauri_keyproviders_mirrored/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml) provide the supporting context for `swarmauri_keyproviders_mirrored`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_keyprovider_local](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_local/README.md): In-memory key provider for development and testing

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_keyproviders_mirrored](https://pypi.org/project/swarmauri_keyproviders_mirrored/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_keyproviders_mirrored` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Mirror Modes**

- `public_only` *(default)* ? Mirrors public key material and JWKS entries when
  available.
- `full` ? Attempts to mirror private material when export policy permits,
  falling back to public-only replication otherwise.
- `none` ? Disables replication while still permitting read failover to the
  secondary provider.

**Failover Semantics**

The `fail_open_reads` flag controls whether read operations fall back to the
secondary provider when the primary raises an exception. Disable it to surface
primary errors immediately.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyproviders_mirrored` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyproviders_mirrored` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyproviders_mirrored` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyproviders_mirrored/NOTICE) for attribution.
<!-- readme-standards:end notices -->
