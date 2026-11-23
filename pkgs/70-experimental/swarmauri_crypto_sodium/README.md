# swarmauri_crypto_sodium

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_crypto_sodium</strong></p>
<p align="center">Libsodium-backed crypto provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_sodium/"><img alt="pypi: swarmauri_crypto_sodium unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=swarmauri_crypto_sodium%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/pyproject.toml"><img alt="Source version: 0.11.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/pyproject.toml"><img alt="Layer: experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_sodium/"><img alt="pypi downloads: swarmauri_crypto_sodium: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=swarmauri_crypto_sodium%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/README.md"><img alt="README hits: swarmauri_crypto_sodium" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/70-experimental/swarmauri_crypto_sodium/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`Swarmauri Crypto Sodium` is a high-performance cryptography provider powered by [libsodium](https://github.com/jedisct1/libsodium). It implements the `ICrypto` contract via `CryptoBase`, enabling fast and secure cryptographic operations inside the Swarmauri ecosystem.

### Why This Package

`swarmauri_crypto_sodium` isolates this responsibility: Libsodium-backed crypto provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/swarmauri_crypto_sodium/SodiumCrypto.py) exposes `SodiumCrypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_crypto_sodium` when your integration needs libsodium-backed crypto provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **XChaCha20-Poly1305** symmetric encryption and decryption
- **X25519 sealed boxes** for data sealing and key wrapping
- **Multi-recipient envelopes** combining XChaCha20-Poly1305 and X25519

### Non-Goals

`swarmauri_crypto_sodium` owns libsodium-backed crypto provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `ninja`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
pip install swarmauri_crypto_sodium
```

#### uv

<!-- readme-standards:begin installation.uv -->
`swarmauri_crypto_sodium` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`swarmauri_crypto_sodium` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`swarmauri_crypto_sodium` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/swarmauri_crypto_sodium
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_crypto_sodium")
assert package.__name__ == "swarmauri_crypto_sodium"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_crypto_sodium`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_crypto_sodium")
assert package.__name__ == "swarmauri_crypto_sodium"
```
<!-- readme-standards:end example.usage -->

```python
from swarmauri_crypto_sodium import SodiumCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = SodiumCrypto()

sym = KeyRef(
    kid="sym1",
    version=1,
    type=KeyType.SYMMETRIC,
    uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=b"\x00" * 32,
)

ct = await crypto.encrypt(sym, b"hello")
pt = await crypto.decrypt(sym, ct)
```

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/swarmauri_crypto_sodium/SodiumCrypto.py) references configuration keys `LIBSODIUM_PATH`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `swarmauri_crypto_sodium` source raises `IntegrityError`, `RuntimeError`, `UnsupportedAlgorithm`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_crypto_sodium` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SodiumCrypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_crypto_sodium` is located in `experimental` and owns libsodium-backed crypto provider for Swarmauri. Source-declared APIs include `SodiumCrypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_crypto_sodium`.

Source-declared exports or types: `SodiumCrypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/swarmauri_crypto_sodium/SodiumCrypto.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.cryptos` → `sodium` → `swarmauri_crypto_sodium:SodiumCrypto`
- `swarmauri.cryptos` → `SodiumCrypto` → `swarmauri_crypto_sodium:SodiumCrypto`
<!-- readme-standards:end entry-points -->

The provider registers under the `swarmauri.cryptos` entry point as `SodiumCrypto`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_crypto_sodium` are `swarmauri-core`, `swarmauri-base`, `ninja`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/swarmauri_crypto_sodium/SodiumCrypto.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_crypto_sodium` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_crypto_sodium`, use the source-declared public interfaces (`SodiumCrypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_crypto_sodium` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_crypto_sodium`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/swarmauri_crypto_sodium/SodiumCrypto.py). The `swarmauri_crypto_sodium` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_crypto_sodium` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_crypto_sodium` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_SodiumCrypto.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/tests/unit/test_SodiumCrypto.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_crypto_sodium` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/swarmauri_crypto_sodium/SodiumCrypto.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_crypto_sodium` provides libsodium-backed crypto provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_crypto_sodium`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/swarmauri_crypto_sodium/SodiumCrypto.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_crypto_sodium` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/swarmauri_crypto_sodium/SodiumCrypto.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/pyproject.toml) provide the supporting context for `swarmauri_crypto_sodium`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_crypto_sodium](https://pypi.org/project/swarmauri_crypto_sodium/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_crypto_sodium`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/70-experimental/swarmauri_crypto_sodium` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_crypto_sodium` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_crypto_sodium` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_crypto_sodium` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_crypto_sodium` source version is `0.11.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the terms of the [MIT License](LICENSE).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/swarmauri_crypto_sodium/NOTICE) for attribution.
<!-- readme-standards:end notices -->
