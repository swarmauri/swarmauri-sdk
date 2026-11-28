# swarmauri_crypto_paramiko

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_crypto_paramiko</strong></p>
<p align="center">Paramiko-backed RSA + AES-GCM crypto provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_paramiko/"><img alt="pypi: swarmauri_crypto_paramiko" src="https://img.shields.io/pypi/v/swarmauri_crypto_paramiko?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_paramiko/"><img alt="Monthly PyPI downloads: swarmauri_crypto_paramiko" src="https://img.shields.io/pypi/dm/swarmauri_crypto_paramiko?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/README.md"><img alt="README hits: swarmauri_crypto_paramiko" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_crypto_paramiko/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_crypto_paramiko`: Paramiko-backed RSA + AES-GCM crypto provider for Swarmauri

### Why This Package

`swarmauri_crypto_paramiko` isolates this responsibility: Paramiko-backed RSA + AES-GCM crypto provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/swarmauri_crypto_paramiko/ParamikoCrypto.py) exposes `ParamikoCrypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_crypto_paramiko` when your integration needs paramiko-backed RSA + AES-GCM crypto provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- AES-256-GCM symmetric encrypt/decrypt (16/24/32 byte keys)
- RSA-OAEP(SHA-256) wrap/unwrap for OpenSSH RSA key pairs
- AES-256-GCM key wrap/unwrap when the KEK is symmetric
- RSA-OAEP(SHA-256) sealing for small payloads
- Multi-recipient hybrid envelopes using OpenSSH public keys

Keys are represented by `KeyRef` objects. Public keys should be provided in
OpenSSH format via `KeyRef.public`, while private keys are supplied as
PEM-encoded bytes in `KeyRef.material`. RSA sealing is limited to inputs no
larger than the modulus-dependent RSA-OAEP bound (`modulus_bytes - 2 * hash_len
- 2`). For larger payloads use the hybrid envelope mode instead.

### Non-Goals

`swarmauri_crypto_paramiko` owns paramiko-backed RSA + AES-GCM crypto provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`, `paramiko`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_crypto_paramiko

# Poetry
poetry add swarmauri_crypto_paramiko

# uv
uv add swarmauri_crypto_paramiko
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_crypto_paramiko
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_crypto_paramiko
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_crypto_paramiko
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_crypto_paramiko")
assert package.__name__ == "swarmauri_crypto_paramiko"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_crypto_paramiko`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_crypto_paramiko")
assert package.__name__ == "swarmauri_crypto_paramiko"
```
<!-- readme-standards:end example.usage -->

**Symmetric AEAD Encryption**

```python
from swarmauri_crypto_paramiko import ParamikoCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = ParamikoCrypto()

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

**RSA Key Wrapping/Unwrapping**

```python
import paramiko
from cryptography.hazmat.primitives import serialization
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = ParamikoCrypto()

key = paramiko.RSAKey.generate(2048)
pub_line = f"{key.get_name()} {key.get_base64()}\n".encode()
priv_pem = key.key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

recipient = KeyRef(
    kid="rsa1",
    version=1,
    type=KeyType.RSA,
    uses=(KeyUse.WRAP, KeyUse.UNWRAP),
    export_policy=ExportPolicy.PUBLIC_ONLY,
    public=pub_line,
    material=priv_pem,
)

wrapped = await crypto.wrap(recipient)
unwrapped = await crypto.unwrap(recipient, wrapped)
```

To wrap with a symmetric key-encryption key instead, provide the AES key bytes
in `KeyRef.material` and set `wrap_alg="AES-256-GCM"`:

```python
sym_kek = KeyRef(
    kid="kek1",
    version=1,
    type=KeyType.SYMMETRIC,
    uses=(KeyUse.WRAP, KeyUse.UNWRAP),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=b"\x01" * 32,
)

wrapped = await crypto.wrap(sym_kek, wrap_alg="AES-256-GCM")
plaintext_key = await crypto.unwrap(sym_kek, wrapped)
```

**RSA Sealing for Small Payloads**

```python
# Using the `recipient` defined above
sealed = await crypto.seal(recipient, b"tiny secret")
plaintext = await crypto.unseal(recipient, sealed)
```

**Hybrid Envelope for Multiple Recipients**

```python
env = await crypto.encrypt_for_many([recipient], b"secret")
```

Calling `encrypt_for_many` without overrides produces an AES-256-GCM ciphertext
shared by every recipient, while `env.recipients` holds RSA-OAEP-wrapped
session keys. Use `enc_alg="RSA-OAEP-SHA256-SEAL"` to emit individual RSA-OAEP
sealed payloads instead of a shared ciphertext when the plaintext fits within
the sealing size limit.

### Configuration

Configure `swarmauri_crypto_paramiko` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/swarmauri_crypto_paramiko/ParamikoCrypto.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_crypto_paramiko` source raises `IntegrityError`, `UnsupportedAlgorithm`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_crypto_paramiko` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ParamikoCrypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_crypto_paramiko` is located in `standards` and owns paramiko-backed RSA + AES-GCM crypto provider for Swarmauri. Source-declared APIs include `ParamikoCrypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_crypto_paramiko`.

Source-declared exports or types: `ParamikoCrypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/swarmauri_crypto_paramiko/ParamikoCrypto.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.cryptos` → `paramiko_crypto` → `swarmauri_crypto_paramiko:ParamikoCrypto`
- `swarmauri.cryptos` → `ParamikoCrypto` → `swarmauri_crypto_paramiko:ParamikoCrypto`
<!-- readme-standards:end entry-points -->

The provider is registered under the `swarmauri.cryptos` entry-point as `ParamikoCrypto`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_crypto_paramiko` are `swarmauri-core`, `swarmauri-base`, `cryptography`, `paramiko`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/swarmauri_crypto_paramiko/ParamikoCrypto.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_crypto_paramiko` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_crypto_paramiko`, use the source-declared public interfaces (`ParamikoCrypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_crypto_paramiko` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_crypto_paramiko`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/swarmauri_crypto_paramiko/ParamikoCrypto.py). The `swarmauri_crypto_paramiko` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_crypto_paramiko` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_crypto_paramiko` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_ParamikoCrypto.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/tests/unit/test_ParamikoCrypto.py)
- [tests/unit/test_usage_examples.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/tests/unit/test_usage_examples.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_crypto_paramiko` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/swarmauri_crypto_paramiko/ParamikoCrypto.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_crypto_paramiko` provides paramiko-backed RSA + AES-GCM crypto provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_crypto_paramiko`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/swarmauri_crypto_paramiko/ParamikoCrypto.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_crypto_paramiko` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/swarmauri_crypto_paramiko/ParamikoCrypto.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml) provide the supporting context for `swarmauri_crypto_paramiko`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_crypto_paramiko](https://pypi.org/project/swarmauri_crypto_paramiko/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_crypto_paramiko` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Crypto Paramiko**

Paramiko-backed crypto provider implementing the `ICrypto` contract via
`CryptoBase`. Built on top of [`paramiko`](https://www.paramiko.org/) and
[`cryptography`](https://cryptography.io/), it exposes an asynchronous API for
several cryptographic primitives using OpenSSH-formatted public keys and
PEM-encoded private keys supplied through `KeyRef` objects.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_crypto_paramiko` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_crypto_paramiko` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_crypto_paramiko` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_paramiko/NOTICE) for attribution.
<!-- readme-standards:end notices -->
