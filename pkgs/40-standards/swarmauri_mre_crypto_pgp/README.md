# swarmauri_mre_crypto_pgp

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_mre_crypto_pgp</strong></p>
<p align="center">OpenPGP sealed-per-recipient MRE provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_mre_crypto_pgp/"><img alt="pypi: swarmauri_mre_crypto_pgp" src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_pgp"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_mre_crypto_pgp/"><img alt="Monthly PyPI downloads: swarmauri_mre_crypto_pgp" src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_pgp"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/README.md"><img alt="README hits: swarmauri_mre_crypto_pgp" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_mre_crypto_pgp/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_mre_crypto_pgp`: OpenPGP sealed-per-recipient MRE provider for Swarmauri

### Why This Package

`swarmauri_mre_crypto_pgp` isolates this responsibility: OpenPGP sealed-per-recipient MRE provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/swarmauri_mre_crypto_pgp/__init__.py) exposes `PGPMreCrypto`, `PGPSealMreCrypto`, `PGPSealedCekMreCrypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_mre_crypto_pgp` when your integration needs openPGP sealed-per-recipient MRE provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **PGPSealMreCrypto** ? Implements the `sealed_per_recipient` mode. Each
  recipient receives a sealed copy of the plaintext. Associated data (AAD) is
  not supported and re-wrapping new recipients requires the original plaintext
  via `opts["plaintext"]`.
- **PGPSealedCekMreCrypto** ? Implements the `sealed_cek+aead` mode with an
  AES-256-GCM payload. The CEK is sealed per recipient and can be re-used to
  add or rotate recipients without decrypting the payload when
  `opts["cek"]` or `opts["opener_identities"]` are supplied.
- **PGPMreCrypto** ? Composite provider supporting both
  `enc_once+per_recipient_header` (AES-256-GCM payload with OpenPGP headers)
  and `sealed_per_recipient`. Re-wrapping shared-payload envelopes requires the
  CEK via `opts["cek"]` or a managing private key supplied through
  `opts["manage_key"]`.

All providers fingerprint OpenPGP keys to derive recipient identifiers. Public
keys can be supplied as live `PGPKey` objects or ASCII-armored blobs using the
following recipient `KeyRef` forms:

- `{"kind": "pgpy_pub", "pub": pgpy.PGPKey}`
- `{"kind": "pgpy_pub_armored", "pub": "-----BEGIN PGP PUBLIC KEY-----"}`
- `{"kind": "pgpy_key", "key": pgpy.PGPKey}` (sealed CEK helper that lifts
  the public subkey from a combined key object)

Use these identity `KeyRef` forms when opening envelopes:

- `{"kind": "pgpy_priv", "priv": pgpy.PGPKey}`
- `{"kind": "pgpy_priv_armored", "priv": "-----BEGIN PGP PRIVATE KEY-----"}`
- `{"kind": "pgpy_key", "key": pgpy.PGPKey}` (sealed CEK provider)
- `{"kind": "pgpy_key_armored", "key": "-----BEGIN PGP PRIVATE KEY-----"}`

Private keys may be locked; pass the unlocking secret in `opts["passphrase"]`.

### Non-Goals

`swarmauri_mre_crypto_pgp` owns openPGP sealed-per-recipient MRE provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `pgpy`, `standard-imghdr`. Read the example’s inputs and service requirements before execution.

### Installation

Install the provider with your preferred packaging tool:

```bash
# pip
pip install swarmauri_mre_crypto_pgp

# Poetry
poetry add swarmauri_mre_crypto_pgp

# uv (project dependency)
uv add swarmauri_mre_crypto_pgp

# uv (virtualenv-only install)
uv pip install swarmauri_mre_crypto_pgp
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_mre_crypto_pgp
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_mre_crypto_pgp
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_mre_crypto_pgp
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/docs/readme/quick_start.py).

```python
import asyncio
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)
from swarmauri_mre_crypto_pgp import PGPMreCrypto


async def main():
    # Generate an OpenPGP key pair with pgpy
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Test User", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.EncryptCommunications},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )

    # Create references understood by the provider
    pub_ref = {"kind": "pgpy_pub", "pub": key.pubkey}
    priv_ref = {"kind": "pgpy_priv", "priv": key}

    # Encrypt for many and open with the private key
    mre = PGPMreCrypto()
    pt = b"hello"
    env = await mre.encrypt_for_many([pub_ref], pt)
    rt = await mre.open_for(priv_ref, env)
    print(rt)


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_mre_crypto_pgp` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/docs/readme/usage.py).

```python
import asyncio
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)
from swarmauri_mre_crypto_pgp import PGPMreCrypto


async def main():
    # Generate an OpenPGP key pair with pgpy
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Test User", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.EncryptCommunications},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )

    # Create references understood by the provider
    pub_ref = {"kind": "pgpy_pub", "pub": key.pubkey}
    priv_ref = {"kind": "pgpy_priv", "priv": key}

    # Encrypt for many and open with the private key
    mre = PGPMreCrypto()
    pt = b"hello"
    env = await mre.encrypt_for_many([pub_ref], pt)
    rt = await mre.open_for(priv_ref, env)
    print(rt)


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_mre_crypto_pgp` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/swarmauri_mre_crypto_pgp/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_mre_crypto_pgp` source raises `PermissionError`, `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_mre_crypto_pgp` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `PGPMreCrypto`, `PGPSealMreCrypto`, `PGPSealedCekMreCrypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_mre_crypto_pgp` is located in `standards` and owns openPGP sealed-per-recipient MRE provider for Swarmauri. Source-declared APIs include `PGPMreCrypto`, `PGPSealMreCrypto`, `PGPSealedCekMreCrypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_mre_crypto_pgp`.

Source-declared exports or types: `PGPMreCrypto`, `PGPSealMreCrypto`, `PGPSealedCekMreCrypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/swarmauri_mre_crypto_pgp/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.mre_cryptos` → `pgp_mre` → `swarmauri_mre_crypto_pgp.pgp_mre:PGPMreCrypto`
- `peagen.plugins.mre_cryptos` → `pgp_seal` → `swarmauri_mre_crypto_pgp:PGPSealMreCrypto`
- `peagen.plugins.mre_cryptos` → `pgp_sealed_cek` → `swarmauri_mre_crypto_pgp.pgp_sealed_cek_mre:PGPSealedCekMreCrypto`
- `swarmauri.mre_cryptos` → `PGPMreCrypto` → `swarmauri_mre_crypto_pgp.pgp_mre:PGPMreCrypto`
- `swarmauri.mre_cryptos` → `PGPSealMreCrypto` → `swarmauri_mre_crypto_pgp:PGPSealMreCrypto`
- `swarmauri.mre_cryptos` → `PGPSealedCekMreCrypto` → `swarmauri_mre_crypto_pgp.pgp_sealed_cek_mre:PGPSealedCekMreCrypto`
<!-- readme-standards:end entry-points -->

Providers are registered under the `swarmauri.mre_cryptos` entry point as
`PGPSealMreCrypto`, `PGPSealedCekMreCrypto`, and `PGPMreCrypto`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_mre_crypto_pgp` are `swarmauri-core`, `swarmauri-base`, `pgpy`, `standard-imghdr`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/swarmauri_mre_crypto_pgp/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_mre_crypto_pgp` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_mre_crypto_pgp`, use the source-declared public interfaces (`PGPMreCrypto`, `PGPSealMreCrypto`, `PGPSealedCekMreCrypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_mre_crypto_pgp` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_mre_crypto_pgp`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/swarmauri_mre_crypto_pgp/__init__.py). The `swarmauri_mre_crypto_pgp` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_mre_crypto_pgp` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_mre_crypto_pgp` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_pgpmrecrypto_rewrap_integration.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/tests/i9n/test_pgpmrecrypto_rewrap_integration.py)
- [tests/i9n/test_rewrap_integration.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/tests/i9n/test_rewrap_integration.py)
- [tests/perf/test_encrypt_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/tests/perf/test_encrypt_perf.py)
- [tests/perf/test_pgpmrecrypto_encrypt_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/tests/perf/test_pgpmrecrypto_encrypt_perf.py)
- [tests/unit/test_PGPMreCrypto.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/tests/unit/test_PGPMreCrypto.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_mre_crypto_pgp` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/swarmauri_mre_crypto_pgp/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_mre_crypto_pgp` provides openPGP sealed-per-recipient MRE provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_mre_crypto_pgp`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/swarmauri_mre_crypto_pgp/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_mre_crypto_pgp` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/swarmauri_mre_crypto_pgp/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml) provide the supporting context for `swarmauri_mre_crypto_pgp`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_mre_crypto_pgp](https://pypi.org/project/swarmauri_mre_crypto_pgp/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_mre_crypto_pgp` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri MRE Crypto PGP**

OpenPGP-based multi-recipient encryption providers that implement the
`IMreCrypto` contract. The package includes three concrete providers, all of
which rely on [PGPy](https://pgpy.readthedocs.io/) for public-key encryption.
Providers that wrap a shared content-encryption key (CEK) additionally require
[`cryptography`](https://cryptography.io/en/latest/).

**Selecting modes**

`PGPMreCrypto` defaults to `MreMode.ENC_ONCE_HEADERS`. Pass
`mode=MreMode.SEALED_PER_RECIPIENT` (or the string value) to switch to the
sealed-per-recipient variant. `PGPSealedCekMreCrypto` always operates in the
`sealed_cek+aead` mode and will raise when the envelope mode or algorithms do
not match the expected values.

**Re-wrapping envelopes**

- **Sealed per recipient** ? Re-wrapping with additional recipients requires
  `opts["plaintext"]` so the providers can seal the original payload again.
- **Shared CEK (enc_once / sealed_cek)** ? Supply either the decrypted CEK via
  `opts["cek"]` or provide identities capable of opening the envelope through
  `opts["manage_key"]` (composite provider) or
  `opts["opener_identities"]` (sealed CEK provider).
  Enable payload rotation with `opts["rotate_payload_on_revoke"]` to generate a
  fresh CEK when removing recipients.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_mre_crypto_pgp` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_mre_crypto_pgp` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_mre_crypto_pgp` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_pgp/NOTICE) for attribution.
<!-- readme-standards:end notices -->
