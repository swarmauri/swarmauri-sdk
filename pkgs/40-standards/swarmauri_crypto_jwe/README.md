# swarmauri_crypto_jwe

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_crypto_jwe</strong></p>
<p align="center">RFC 7516/7518 compliant JWE crypto provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_jwe/"><img alt="pypi: swarmauri_crypto_jwe" src="https://img.shields.io/pypi/v/swarmauri_crypto_jwe?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_jwe/"><img alt="Monthly PyPI downloads: swarmauri_crypto_jwe" src="https://img.shields.io/pypi/dm/swarmauri_crypto_jwe?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/README.md"><img alt="README hits: swarmauri_crypto_jwe" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_crypto_jwe/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_crypto_jwe`: RFC 7516/7518 compliant JWE crypto provider for Swarmauri

### Why This Package

`swarmauri_crypto_jwe` isolates this responsibility: RFC 7516/7518 compliant JWE crypto provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/swarmauri_crypto_jwe/JweCrypto.py) exposes `JweCrypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_crypto_jwe` when your integration needs rFC 7516/7518 compliant JWE crypto provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Asynchronous API for compact JWE serialization returning strings.
- Accepts `JWAAlg` enums from [`swarmauri_core.crypto.types`](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/10-interfaces/swarmauri_core/swarmauri_core/crypto/types.py) for algorithms.
- Supports `dir`, `RSA-OAEP`, `RSA-OAEP-256`, and `ECDH-ES` key management algorithms.
- Supports `A128GCM`, `A192GCM`, and `A256GCM` content encryption.
- Optional compression (`zip` = `DEF`) and Additional Authenticated Data (AAD).
- Returns structured decrypt results that include both the protected header and plaintext.
- Registers with the Swarmauri PluginManager via the `swarmauri.cryptos` entry point.

### Non-Goals

`swarmauri_crypto_jwe` owns rFC 7516/7518 compliant JWE crypto provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
pip install swarmauri_crypto_jwe
# or
poetry add swarmauri_crypto_jwe
# or, with uv
uv add swarmauri_crypto_jwe
```

> [!TIP]
> `uv` can be installed with `pip install uv` or by following the instructions at [astral.sh/uv](https://docs.astral.sh/uv/). Once installed, run `uv add swarmauri_crypto_jwe` from your project directory to add the dependency.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_crypto_jwe
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_crypto_jwe
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_crypto_jwe
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/docs/readme/quick_start.py).

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_crypto_jwe import JweCrypto


async def main() -> None:
    crypto = JweCrypto()

    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk_pem = sk.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    jwe = await crypto.encrypt_compact(
        payload=b"secret",
        alg=JWAAlg.RSA_OAEP_256,
        enc=JWAAlg.A256GCM,
        key={"pub": pk_pem},
    )

    result = await crypto.decrypt_compact(
        jwe,
        rsa_private_pem=sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )
    assert result.plaintext == b"secret"


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_crypto_jwe` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/docs/readme/usage.py).

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_crypto_jwe import JweCrypto


async def main() -> None:
    crypto = JweCrypto()

    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk_pem = sk.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    jwe = await crypto.encrypt_compact(
        payload=b"secret",
        alg=JWAAlg.RSA_OAEP_256,
        enc=JWAAlg.A256GCM,
        key={"pub": pk_pem},
    )

    result = await crypto.decrypt_compact(
        jwe,
        rsa_private_pem=sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )
    assert result.plaintext == b"secret"


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The helpers are asynchronous and return compact JWE strings that can be
decrypted back into their original plaintext. A typical flow is:

1. Generate or load the key material for the chosen algorithm.
2. Instantiate `JweCrypto`.
3. Call `encrypt_compact` with the payload, algorithm, and key details.
4. Call `decrypt_compact` with the resulting JWE and the corresponding
   private key.

### Configuration

Configure `swarmauri_crypto_jwe` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/swarmauri_crypto_jwe/JweCrypto.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_crypto_jwe` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_crypto_jwe` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `JweCrypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_crypto_jwe` is located in `standards` and owns rFC 7516/7518 compliant JWE crypto provider for Swarmauri. Source-declared APIs include `JweCrypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_crypto_jwe`.

Source-declared exports or types: `JweCrypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/swarmauri_crypto_jwe/JweCrypto.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

The provider is registered under the `swarmauri.cryptos` entry point as `JweCrypto`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_crypto_jwe` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/swarmauri_crypto_jwe/JweCrypto.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_crypto_jwe` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_crypto_jwe`, use the source-declared public interfaces (`JweCrypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_crypto_jwe` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_crypto_jwe`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/swarmauri_crypto_jwe/JweCrypto.py). The `swarmauri_crypto_jwe` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_crypto_jwe` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_crypto_jwe` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/tests/example/test_readme_example.py)
- [tests/functional/test_jwe_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/tests/functional/test_jwe_functional.py)
- [tests/perf/test_jwe_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/tests/perf/test_jwe_perf.py)
- [tests/rfc/test_rfc7516.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/tests/rfc/test_rfc7516.py)
- [tests/rfc/test_rfc7518.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/tests/rfc/test_rfc7518.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_crypto_jwe` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/swarmauri_crypto_jwe/JweCrypto.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_crypto_jwe` provides rFC 7516/7518 compliant JWE crypto provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_crypto_jwe`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/swarmauri_crypto_jwe/JweCrypto.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_crypto_jwe` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/swarmauri_crypto_jwe/JweCrypto.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml) provide the supporting context for `swarmauri_crypto_jwe`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_crypto_jwe](https://pypi.org/project/swarmauri_crypto_jwe/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_crypto_jwe` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Crypto JWE**

JSON Web Encryption (JWE) provider implementing RFC 7516 and RFC 7518 compliant encryption and decryption helpers.

**Loading via PluginManager**

```python
from swarmauri.plugin import PluginManager

pm = PluginManager()
crypto = pm.load("swarmauri.cryptos", "JweCrypto")
```

**Parameters**

- `alg` ? `JWAAlg` member describing the key management algorithm (`JWAAlg.RSA_OAEP_256`, `JWAAlg.DIR`, etc.).
- `enc` ? `JWAAlg` member describing the content encryption algorithm (`JWAAlg.A256GCM`, `JWAAlg.A128GCM`, etc.).
- `key` ? mapping containing the key material used for encryption:
  - `{"k": bytes}` for direct symmetric keys (`dir`).
  - `{"pub": rsa_public_key}` for RSA OAEP, where the public key may be PEM bytes or an `RSAPublicKey` instance.
  - `{"pub": ec_public_key}` for ECDH-ES with PEM, JWK, or key objects.
- Optional `header_extra` values are merged into the protected header (use `zip="DEF"` to enable compression).
- Decryption requires the matching private key via `dir_key`, `rsa_private_pem`/`rsa_private_password`, or `ecdh_private_key`.
- `expected_algs` and `expected_encs` constrain acceptable algorithms during decryption, and `aad` must match the authenticated data provided at encryption time.

**Opt-in X448**

Use `JweCrypto(enable_x448=True)` with `alg=JWAAlg.ECDH_ES`,
`enc=JWAAlg.A256GCM`, and a public recipient JWK with `kty="OKP"`,
`crv="X448"`, and a base64url-encoded `x`. Pass an
`X448PrivateKey` as `ecdh_private_key` to decrypt.

New ECDH-ES tokens use the RFC 7518 Concat KDF. To read X25519 or
NIST-curve tokens issued with the previous Swarmauri KDF, pass
`legacy_ecdh_kdf=True` to `decrypt_compact` for those known tokens.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_crypto_jwe` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_crypto_jwe` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_crypto_jwe` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_jwe/NOTICE) for attribution.
<!-- readme-standards:end notices -->
