# swarmauri_mre_crypto_age

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_mre_crypto_age</strong></p>
<p align="center">Age-style X25519 sealed-per-recipient MRE provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_mre_crypto_age/"><img alt="pypi: swarmauri_mre_crypto_age" src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_age?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_mre_crypto_age/"><img alt="Monthly PyPI downloads: swarmauri_mre_crypto_age" src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_age?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/README.md"><img alt="README hits: swarmauri_mre_crypto_age" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_mre_crypto_age/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_mre_crypto_age`: Age-style X25519 sealed-per-recipient MRE provider for Swarmauri

### Why This Package

`swarmauri_mre_crypto_age` isolates this responsibility: Age-style X25519 sealed-per-recipient MRE provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/swarmauri_mre_crypto_age/__init__.py) exposes `AgeMreCrypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_mre_crypto_age` when your integration needs age-style X25519 sealed-per-recipient MRE provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `AgeMreCrypto`: AgeMreCrypto (sealed-per-recipient, X25519 stanzas).

### Non-Goals

`swarmauri_mre_crypto_age` owns age-style X25519 sealed-per-recipient MRE provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the installer that matches your project workflow:

```bash
# pip
pip install swarmauri_mre_crypto_age

# Poetry
poetry add swarmauri_mre_crypto_age

# uv
uv add swarmauri_mre_crypto_age
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_mre_crypto_age
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_mre_crypto_age
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_mre_crypto_age
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_mre_crypto_age")
assert package.__name__ == "swarmauri_mre_crypto_age"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_mre_crypto_age`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_mre_crypto_age")
assert package.__name__ == "swarmauri_mre_crypto_age"
```
<!-- readme-standards:end example.usage -->

The provider exposes asynchronous helpers for encrypting data to many
recipients and decrypting it for a specific private key.  The example below
walks through a complete round trip.

1. Create the crypto provider.
2. Generate key pairs for two recipients.
3. Encrypt a payload for both recipients.
4. Decrypt the payload for one recipient.

```python
from swarmauri_mre_crypto_age import AgeMreCrypto
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

crypto = AgeMreCrypto()

# generate key pairs for each participant
sk1 = X25519PrivateKey.generate()
pk1 = sk1.public_key()
sk2 = X25519PrivateKey.generate()
pk2 = sk2.public_key()

recipients = [
    {"kind": "cryptography_obj", "obj": pk1},
    {"kind": "cryptography_obj", "obj": pk2},
]

env = await crypto.encrypt_for_many(recipients, b"secret")
pt = await crypto.open_for({"kind": "cryptography_obj", "obj": sk1}, env)
assert pt == b"secret"
```

The helper accepts multiple `KeyRef` formats, including dictionaries with
`kind="cryptography_obj"` (for `X25519PublicKey` / `X25519PrivateKey` objects)
and raw byte references such as `kind="raw_x25519_pk"` or `kind="age_x25519_pk"`.
When rewrapping an existing envelope to add recipients, pass the plaintext via
`opts["pt"]` or provide an identity through `opts["open_with"]` so the payload
can be resealed for the new recipients.

### Configuration

Configure `swarmauri_mre_crypto_age` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/swarmauri_mre_crypto_age/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_mre_crypto_age` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_mre_crypto_age` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AgeMreCrypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_mre_crypto_age` is located in `standards` and owns age-style X25519 sealed-per-recipient MRE provider for Swarmauri. Source-declared APIs include `AgeMreCrypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_mre_crypto_age`.

Source-declared exports or types: `AgeMreCrypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/swarmauri_mre_crypto_age/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.mre_cryptos` → `age_mre` → `swarmauri_mre_crypto_age:AgeMreCrypto`
- `swarmauri.mre_cryptos` → `AgeMreCrypto` → `swarmauri_mre_crypto_age:AgeMreCrypto`
<!-- readme-standards:end entry-points -->

The provider is registered under the `swarmauri.mre_cryptos` entry-point as `AgeMreCrypto`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_mre_crypto_age` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/swarmauri_mre_crypto_age/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_mre_crypto_age` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_mre_crypto_age`, use the source-declared public interfaces (`AgeMreCrypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_mre_crypto_age` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_mre_crypto_age`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/swarmauri_mre_crypto_age/__init__.py). The `swarmauri_mre_crypto_age` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_mre_crypto_age` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_mre_crypto_age` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_example_usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/tests/functional/test_example_usage.py)
- [tests/functional/test_open_for_many.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/tests/functional/test_open_for_many.py)
- [tests/perf/test_encrypt_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/tests/perf/test_encrypt_perf.py)
- [tests/unit/test_AgeMreCrypto.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/tests/unit/test_AgeMreCrypto.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_mre_crypto_age` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/swarmauri_mre_crypto_age/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_mre_crypto_age` provides age-style X25519 sealed-per-recipient MRE provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_mre_crypto_age`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/swarmauri_mre_crypto_age/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_mre_crypto_age` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/swarmauri_mre_crypto_age/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml) provide the supporting context for `swarmauri_mre_crypto_age`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_mre_crypto_age](https://pypi.org/project/swarmauri_mre_crypto_age/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_mre_crypto_age` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri MRE Crypto Age**

Age-based multi-recipient encryption provider implementing the `IMreCrypto` contract.

- Sealed-per-recipient X25519 stanzas (`mode="sealed_per_recipient"` and `recipient_alg="X25519-SEAL"`)
- ChaCha20-Poly1305 payload encryption for each recipient header
- Deterministic recipient identifiers via SHA-256 public key fingerprints
- Rewrapping support for adding or removing recipients when provided the original plaintext or an opening identity

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_mre_crypto_age` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_mre_crypto_age` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_mre_crypto_age` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_mre_crypto_age/NOTICE) for attribution.
<!-- readme-standards:end notices -->
