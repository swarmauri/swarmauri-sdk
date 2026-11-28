# swarmauri_crypto_ecdh_es_a128kw

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_crypto_ecdh_es_a128kw</strong></p>
<p align="center">ECDH-ES+A128KW crypto provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_ecdh_es_a128kw/"><img alt="pypi: swarmauri_crypto_ecdh_es_a128kw" src="https://img.shields.io/pypi/v/swarmauri_crypto_ecdh_es_a128kw?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_ecdh_es_a128kw/"><img alt="Monthly PyPI downloads: swarmauri_crypto_ecdh_es_a128kw" src="https://img.shields.io/pypi/dm/swarmauri_crypto_ecdh_es_a128kw?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/README.md"><img alt="README hits: swarmauri_crypto_ecdh_es_a128kw" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

ECDH-ES+A128KW key wrapping provider for Swarmauri.

### Why This Package

`swarmauri_crypto_ecdh_es_a128kw` isolates this responsibility: ECDH-ES+A128KW crypto provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/swarmauri_crypto_ecdh_es_a128kw/ECDHESA128KWCrypto.py) exposes `ECDHESA128KWCrypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_crypto_ecdh_es_a128kw` when your integration needs eCDH-ES+A128KW crypto provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Implements the JSON Web Encryption ECDH-ES key agreement combined with AES Key Wrap using a 128-bit KEK (`ECDH-ES+A128KW`).
- Accepts `KeyRef` objects whose `public` attribute carries an EC public key in PEM format for wrapping and whose `material` attribute provides the corresponding private key for unwrapping.
- Derives a one-time key-encryption key via Concat KDF with SHA-256 and serializes results as JSON containing the ephemeral public key (`epk`) and wrapped DEK (`kw`), both Base64URL encoded.
- Generates a fresh 16-byte DEK when one is not provided so you can delegate symmetric key generation to the provider.

### Non-Goals

`swarmauri_crypto_ecdh_es_a128kw` owns eCDH-ES+A128KW crypto provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_crypto_ecdh_es_a128kw

# Poetry
poetry add swarmauri_crypto_ecdh_es_a128kw

# uv
uv add swarmauri_crypto_ecdh_es_a128kw
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_crypto_ecdh_es_a128kw
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_crypto_ecdh_es_a128kw
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_crypto_ecdh_es_a128kw
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

The example below creates a recipient EC key pair, wraps a deterministic 128-bit DEK, and then unwraps it again to demonstrate the round trip. Run it with `python quickstart.py` or paste it into a REPL.


**What to expect**

- `wrap` derives an ephemeral ECDH shared secret with the recipient public key, hashes it with Concat KDF (SHA-256) to produce a 128-bit KEK, and AES-KW wraps the provided DEK.
- The returned `WrappedKey` stores a JSON document containing the ephemeral public key (`epk`) and the wrapped DEK (`kw`), both Base64URL encoded.
- `unwrap` repeats the derivation using the recipient private key (`KeyRef.material`) and returns the original DEK bytes.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/docs/readme/quick_start.py).

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_crypto_ecdh_es_a128kw import ECDHESA128KWCrypto


def make_recipient_key() -> KeyRef:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    return KeyRef(
        kid="recipient-key",
        version=1,
        type=KeyType.EC,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        public=public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )


async def main() -> None:
    crypto = ECDHESA128KWCrypto()
    recipient = make_recipient_key()
    dek = b"0123456789ABCDEF"  # 16 byte content encryption key

    wrapped = await crypto.wrap(recipient, dek=dek)
    recovered = await crypto.unwrap(recipient, wrapped)

    print("Wrapped payload:", wrapped.wrapped.decode("utf-8"))
    assert recovered == dek


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_crypto_ecdh_es_a128kw` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/docs/readme/usage.py).

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_crypto_ecdh_es_a128kw import ECDHESA128KWCrypto


def make_recipient_key() -> KeyRef:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    return KeyRef(
        kid="recipient-key",
        version=1,
        type=KeyType.EC,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        public=public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )


async def main() -> None:
    crypto = ECDHESA128KWCrypto()
    recipient = make_recipient_key()
    dek = b"0123456789ABCDEF"  # 16 byte content encryption key

    wrapped = await crypto.wrap(recipient, dek=dek)
    recovered = await crypto.unwrap(recipient, wrapped)

    print("Wrapped payload:", wrapped.wrapped.decode("utf-8"))
    assert recovered == dek


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_crypto_ecdh_es_a128kw` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/swarmauri_crypto_ecdh_es_a128kw/ECDHESA128KWCrypto.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_crypto_ecdh_es_a128kw` source raises `UnsupportedAlgorithm`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_crypto_ecdh_es_a128kw` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ECDHESA128KWCrypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_crypto_ecdh_es_a128kw` is located in `standards` and owns eCDH-ES+A128KW crypto provider for Swarmauri. Source-declared APIs include `ECDHESA128KWCrypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_crypto_ecdh_es_a128kw`.

Source-declared exports or types: `ECDHESA128KWCrypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/swarmauri_crypto_ecdh_es_a128kw/ECDHESA128KWCrypto.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.cryptos` → `ecdh_es_a128kw` → `swarmauri_crypto_ecdh_es_a128kw:ECDHESA128KWCrypto`
- `swarmauri.cryptos` → `ECDHESA128KWCrypto` → `swarmauri_crypto_ecdh_es_a128kw:ECDHESA128KWCrypto`
<!-- readme-standards:end entry-points -->

The provider is registered under the `swarmauri.cryptos` entry point as `ECDHESA128KWCrypto`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_crypto_ecdh_es_a128kw` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/swarmauri_crypto_ecdh_es_a128kw/ECDHESA128KWCrypto.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_crypto_ecdh_es_a128kw` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_crypto_ecdh_es_a128kw`, use the source-declared public interfaces (`ECDHESA128KWCrypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_crypto_ecdh_es_a128kw` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_crypto_ecdh_es_a128kw`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/swarmauri_crypto_ecdh_es_a128kw/ECDHESA128KWCrypto.py). The `swarmauri_crypto_ecdh_es_a128kw` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_crypto_ecdh_es_a128kw` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_crypto_ecdh_es_a128kw` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/tests/test_readme_example.py)
- [tests/test_wrap_unwrap.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/tests/test_wrap_unwrap.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_crypto_ecdh_es_a128kw` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/swarmauri_crypto_ecdh_es_a128kw/ECDHESA128KWCrypto.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_crypto_ecdh_es_a128kw` provides eCDH-ES+A128KW crypto provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_crypto_ecdh_es_a128kw`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/swarmauri_crypto_ecdh_es_a128kw/ECDHESA128KWCrypto.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_crypto_ecdh_es_a128kw` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/swarmauri_crypto_ecdh_es_a128kw/ECDHESA128KWCrypto.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml) provide the supporting context for `swarmauri_crypto_ecdh_es_a128kw`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_crypto_ecdh_es_a128kw](https://pypi.org/project/swarmauri_crypto_ecdh_es_a128kw/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_crypto_ecdh_es_a128kw` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_crypto_ecdh_es_a128kw` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_crypto_ecdh_es_a128kw` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_crypto_ecdh_es_a128kw` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/LICENSE).
<!-- readme-standards:end license -->

`swarmauri_crypto_ecdh_es_a128kw` is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/LICENSE) file for details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_ecdh_es_a128kw/NOTICE) for attribution.
<!-- readme-standards:end notices -->
