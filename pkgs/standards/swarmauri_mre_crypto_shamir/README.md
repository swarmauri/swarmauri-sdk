# swarmauri_mre_crypto_shamir

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_mre_crypto_shamir</strong></p>
<p align="center">Shamir secret sharing based MRE crypto provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/"><img alt="pypi: swarmauri_mre_crypto_shamir" src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_shamir"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/"><img alt="Monthly PyPI downloads: swarmauri_mre_crypto_shamir" src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_shamir"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/README.md"><img alt="README hits: swarmauri_mre_crypto_shamir" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_mre_crypto_shamir/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Shamir Secret Sharing based multi-recipient encryption (MRE) provider for the Swarmauri framework. The provider splits an AES-256-GCM content encryption key using Shamir's threshold scheme and distributes shares to recipients.

### Why This Package

`swarmauri_mre_crypto_shamir` isolates this responsibility: Shamir secret sharing based MRE crypto provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/swarmauri_mre_crypto_shamir/ShamirMreCrypto.py) exposes `ShamirMreCrypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_mre_crypto_shamir` when your integration needs shamir secret sharing based MRE crypto provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- AES-256-GCM payload encryption
- Threshold k-of-n key sharing via Shamir secret sharing
- Envelope rewrapping with optional payload rotation
- Optional authenticated data (AAD) handling

### Non-Goals

`swarmauri_mre_crypto_shamir` owns shamir secret sharing based MRE crypto provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_mre_crypto_shamir

# Poetry
poetry add swarmauri_mre_crypto_shamir

# uv (project dependency)
uv add swarmauri_mre_crypto_shamir

# uv (one-off virtual environment)
uv pip install swarmauri_mre_crypto_shamir
```

Install extras, such as CBOR canonicalization support, with `swarmauri_mre_crypto_shamir[cbor]`.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_mre_crypto_shamir
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_mre_crypto_shamir
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_mre_crypto_shamir
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

`ShamirMreCrypto` encrypts a payload with a fresh AES-256-GCM content encryption key, splits the key into Shamir shares, and stores the encrypted payload and shares in a multi-recipient envelope. Provide a threshold with `opts["threshold_k"]` (defaults to a simple majority) to control how many shares are required to decrypt.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_mre_crypto_shamir import ShamirMreCrypto


async def main() -> None:
    provider = ShamirMreCrypto()

    recipients = [
        {"kid": "alice"},
        {"kid": "bob"},
        {"kid": "carol"},
    ]

    plaintext = b"Secret launch codes"

    envelope = await provider.encrypt_for_many(
        recipients,
        plaintext,
        opts={"threshold_k": 2},
    )

    print("Mode:", envelope["mode"])
    print("Recipients:", [entry["id"] for entry in envelope["recipients"]])
    print(
        "Threshold:",
        int.from_bytes(envelope["shared"]["threshold_k"], "big"),
    )

    recovered = await provider.open_for_many(
        [{"kid": "alice"}, {"kid": "carol"}],
        envelope,
    )

    assert recovered == plaintext
    print("Recovered plaintext:", recovered.decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_mre_crypto_shamir` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/docs/readme/usage.py).

```python
import asyncio

from swarmauri_mre_crypto_shamir import ShamirMreCrypto


async def main() -> None:
    provider = ShamirMreCrypto()

    recipients = [
        {"kid": "alice"},
        {"kid": "bob"},
        {"kid": "carol"},
    ]

    plaintext = b"Secret launch codes"

    envelope = await provider.encrypt_for_many(
        recipients,
        plaintext,
        opts={"threshold_k": 2},
    )

    print("Mode:", envelope["mode"])
    print("Recipients:", [entry["id"] for entry in envelope["recipients"]])
    print(
        "Threshold:",
        int.from_bytes(envelope["shared"]["threshold_k"], "big"),
    )

    recovered = await provider.open_for_many(
        [{"kid": "alice"}, {"kid": "carol"}],
        envelope,
    )

    assert recovered == plaintext
    print("Recovered plaintext:", recovered.decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_mre_crypto_shamir` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/swarmauri_mre_crypto_shamir/ShamirMreCrypto.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_mre_crypto_shamir` source raises `ValueError`, `ZeroDivisionError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_mre_crypto_shamir` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ShamirMreCrypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_mre_crypto_shamir` is located in `standards` and owns shamir secret sharing based MRE crypto provider for Swarmauri. Source-declared APIs include `ShamirMreCrypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_mre_crypto_shamir`.

Source-declared exports or types: `ShamirMreCrypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/swarmauri_mre_crypto_shamir/ShamirMreCrypto.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.mre_cryptos` → `shamir` → `swarmauri_mre_crypto_shamir:ShamirMreCrypto`
- `swarmauri.mre_cryptos` → `ShamirMreCrypto` → `swarmauri_mre_crypto_shamir:ShamirMreCrypto`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_mre_crypto_shamir` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/swarmauri_mre_crypto_shamir/ShamirMreCrypto.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_mre_crypto_shamir` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_mre_crypto_shamir`, use the source-declared public interfaces (`ShamirMreCrypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_mre_crypto_shamir` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_mre_crypto_shamir`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/swarmauri_mre_crypto_shamir/ShamirMreCrypto.py). The `swarmauri_mre_crypto_shamir` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_mre_crypto_shamir` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_mre_crypto_shamir` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/tests/test_readme_example.py)
- [tests/functional/test_shamir_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/tests/functional/test_shamir_functional.py)
- [tests/perf/test_shamir_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/tests/perf/test_shamir_perf.py)
- [tests/unit/test_shamir_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/tests/unit/test_shamir_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_mre_crypto_shamir` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/swarmauri_mre_crypto_shamir/ShamirMreCrypto.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_mre_crypto_shamir` provides shamir secret sharing based MRE crypto provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_mre_crypto_shamir`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/swarmauri_mre_crypto_shamir/ShamirMreCrypto.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_mre_crypto_shamir` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/swarmauri_mre_crypto_shamir/ShamirMreCrypto.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml) provide the supporting context for `swarmauri_mre_crypto_shamir`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_mre_crypto_shamir](https://pypi.org/project/swarmauri_mre_crypto_shamir/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_mre_crypto_shamir` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Extras**

The plugin supports optional canonicalization extras:

- `cbor` ? enables CBOR canonicalization via `cbor2`

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_mre_crypto_shamir` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_mre_crypto_shamir` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_mre_crypto_shamir` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_mre_crypto_shamir/NOTICE) for attribution.
<!-- readme-standards:end notices -->
