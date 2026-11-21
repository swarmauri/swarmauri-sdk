# swarmauri_crypto_nacl_pkcs11

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_crypto_nacl_pkcs11</strong></p>
<p align="center">NaCl + PKCS#11 crypto provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_nacl_pkcs11/"><img alt="pypi: swarmauri_crypto_nacl_pkcs11" src="https://img.shields.io/pypi/v/swarmauri_crypto_nacl_pkcs11"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_nacl_pkcs11/"><img alt="Monthly PyPI downloads: swarmauri_crypto_nacl_pkcs11" src="https://img.shields.io/pypi/dm/swarmauri_crypto_nacl_pkcs11"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/README.md"><img alt="README hits: swarmauri_crypto_nacl_pkcs11" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_crypto_nacl_pkcs11/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_crypto_nacl_pkcs11`: NaCl + PKCS#11 crypto provider for Swarmauri

### Why This Package

`swarmauri_crypto_nacl_pkcs11` isolates this responsibility: NaCl + PKCS#11 crypto provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/swarmauri_crypto_nacl_pkcs11/NaClPkcs11Crypto.py) exposes `NaClPkcs11Crypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_crypto_nacl_pkcs11` when your integration needs naCl + PKCS#11 crypto provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `NaClPkcs11Crypto`: Concrete implementation of the ICrypto contract using PyNaCl and

### Non-Goals

`swarmauri_crypto_nacl_pkcs11` owns naCl + PKCS#11 crypto provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `pynacl`, `cryptography`, `python-pkcs11`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the workflow that matches your project:

```bash
pip install swarmauri_crypto_nacl_pkcs11
```

```bash
poetry add swarmauri_crypto_nacl_pkcs11
```

```bash
uv add swarmauri_crypto_nacl_pkcs11
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_crypto_nacl_pkcs11
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_crypto_nacl_pkcs11
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_crypto_nacl_pkcs11
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_crypto_nacl_pkcs11 import NaClPkcs11Crypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def main() -> None:
    crypto = NaClPkcs11Crypto()

    symmetric_key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ciphertext = await crypto.encrypt(symmetric_key, b"hello")
    plaintext = await crypto.decrypt(symmetric_key, ciphertext)
    assert plaintext == b"hello"


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_crypto_nacl_pkcs11` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/docs/readme/usage.py).

```python
import asyncio

from swarmauri_crypto_nacl_pkcs11 import NaClPkcs11Crypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def main() -> None:
    crypto = NaClPkcs11Crypto()

    symmetric_key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ciphertext = await crypto.encrypt(symmetric_key, b"hello")
    plaintext = await crypto.decrypt(symmetric_key, ciphertext)
    assert plaintext == b"hello"


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

All cryptographic methods are asynchronous. The quick-start example below performs an AES-GCM round trip using a 256-bit symmetric key.

<!-- example-start -->
<!-- example-end -->

**Sealed box key exchange**

`seal` and `encrypt_for_many` expect X25519 `KeyRef` instances. Provide the public key bytes via `KeyRef.public` for recipients and the private key bytes via `KeyRef.material` for unsealing. Each recipient receives an opaque sealed payload generated with `nacl.public.SealedBox`.

**PKCS#11-backed key wrapping**

`wrap` and `unwrap` require a key-encryption-key (KEK) stored in the configured PKCS#11 slot. Supply connection details through `KeyRef.tags` or environment variables as described above. The wrapped material is returned as a `WrappedKey` using the `AES-KW` algorithm.

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/swarmauri_crypto_nacl_pkcs11/NaClPkcs11Crypto.py) references configuration keys `PKCS11_KEK_LABEL`, `PKCS11_MODULE`, `PKCS11_SLOT_LABEL`, `PKCS11_USER_PIN`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `swarmauri_crypto_nacl_pkcs11` source raises `RuntimeError`, `UnsupportedAlgorithm`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_crypto_nacl_pkcs11` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `NaClPkcs11Crypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_crypto_nacl_pkcs11` is located in `standards` and owns naCl + PKCS#11 crypto provider for Swarmauri. Source-declared APIs include `NaClPkcs11Crypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_crypto_nacl_pkcs11`.

Source-declared exports or types: `NaClPkcs11Crypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/swarmauri_crypto_nacl_pkcs11/NaClPkcs11Crypto.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.cryptos` → `nacl_pkcs11` → `swarmauri_crypto_nacl_pkcs11:NaClPkcs11Crypto`
- `swarmauri.cryptos` → `NaClPkcs11Crypto` → `swarmauri_crypto_nacl_pkcs11:NaClPkcs11Crypto`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_crypto_nacl_pkcs11` are `swarmauri-core`, `swarmauri-base`, `pynacl`, `cryptography`, `python-pkcs11`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/swarmauri_crypto_nacl_pkcs11/NaClPkcs11Crypto.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_crypto_nacl_pkcs11` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_crypto_nacl_pkcs11`, use the source-declared public interfaces (`NaClPkcs11Crypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_crypto_nacl_pkcs11` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_crypto_nacl_pkcs11`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/swarmauri_crypto_nacl_pkcs11/NaClPkcs11Crypto.py). The `swarmauri_crypto_nacl_pkcs11` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_crypto_nacl_pkcs11` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_crypto_nacl_pkcs11` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/tests/test_readme.py)
- [tests/unit/test_NaClPkcs11Crypto.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/tests/unit/test_NaClPkcs11Crypto.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_crypto_nacl_pkcs11` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/swarmauri_crypto_nacl_pkcs11/NaClPkcs11Crypto.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_crypto_nacl_pkcs11` provides naCl + PKCS#11 crypto provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_crypto_nacl_pkcs11`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/swarmauri_crypto_nacl_pkcs11/NaClPkcs11Crypto.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_crypto_nacl_pkcs11` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/swarmauri_crypto_nacl_pkcs11/NaClPkcs11Crypto.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/pyproject.toml) provide the supporting context for `swarmauri_crypto_nacl_pkcs11`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_crypto_nacl_pkcs11](https://pypi.org/project/swarmauri_crypto_nacl_pkcs11/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_crypto_nacl_pkcs11` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Crypto NaCl PKCS#11**

`swarmauri_crypto_nacl_pkcs11` is a hybrid crypto provider that combines [PyNaCl](https://pynacl.readthedocs.io) for X25519 sealed-box operations with [`python-pkcs11`](https://python-pkcs11.readthedocs.io) for AES key wrapping. The provider implements the `CryptoBase` contract and is discoverable via the `swarmauri.cryptos` entry-point as `NaClPkcs11Crypto`.

**Supported operations**

- **AES-GCM authenticated encryption** via `encrypt`/`decrypt` using symmetric `KeyRef` material that is exactly 16, 24, or 32 bytes long.
- **AES Key Wrap (AES-KW)** via `wrap`/`unwrap` against an HSM-protected key. The PKCS#11 session is resolved from the `KeyRef.tags` (`module`, `slot_label`, `user_pin`, `label`) or the environment variables `PKCS11_MODULE`, `PKCS11_SLOT_LABEL`, `PKCS11_USER_PIN`, and `PKCS11_KEK_LABEL`.
- **X25519 sealed boxes** via `seal`/`unseal` and `encrypt_for_many`, enabling single or multi-recipient payload distribution. When additional authenticated data (AAD) is supplied the envelope is rebound with AES-GCM before delivery.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_crypto_nacl_pkcs11` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_crypto_nacl_pkcs11` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_crypto_nacl_pkcs11` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/NOTICE) for attribution.
<!-- readme-standards:end notices -->
