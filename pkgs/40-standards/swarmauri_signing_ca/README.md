# swarmauri_signing_ca

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_ca</strong></p>
<p align="center">Certificate authority style signer for Swarmauri envelopes</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_ca/"><img alt="pypi: swarmauri_signing_ca" src="https://img.shields.io/pypi/v/swarmauri_signing_ca"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_ca/"><img alt="Monthly PyPI downloads: swarmauri_signing_ca" src="https://img.shields.io/pypi/dm/swarmauri_signing_ca"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/README.md"><img alt="README hits: swarmauri_signing_ca" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_signing_ca/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_signing_ca` exposes a certificate-authority-capable implementation of
`ISigning` that focuses on detached signatures over raw bytes and canonicalized
Swarmauri envelopes. The signer understands common public key algorithms and ships
with utilities for issuing and validating X.509 material.

### Why This Package

`swarmauri_signing_ca` isolates this responsibility: Certificate authority style signer for Swarmauri envelopes. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/swarmauri_signing_ca/__init__.py) exposes `CASigner`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_ca` when your integration needs certificate authority style signer for Swarmauri envelopes. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Deterministic JSON canonicalization for envelopes (JSON is the supported canon).
- Detached signature support for Ed25519, ECDSA (P-256 and compatible curves), and RSA-PSS/RS256.
- Accepts PEM-encoded private keys or pre-instantiated cryptography objects via `KeyRef`.
- X.509 helpers for issuing self-signed certificates, signing CSRs, and verifying simple chains.
- Advertises the `multi`, `detached_only`, and `x509` features under the `swarmauri.signings` entry point as `CASigner`.

### Non-Goals

`swarmauri_signing_ca` owns certificate authority style signer for Swarmauri envelopes. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that fits your workflow:

```bash
# pip
pip install swarmauri_signing_ca

# Poetry
poetry add swarmauri_signing_ca

# uv
uv add swarmauri_signing_ca
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_ca
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_ca
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_ca
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

The example below generates an Ed25519 key, signs a message, and verifies the
signature using the same public key. It mirrors what `CASigner` performs in
production environments.


**Notes on verification**

`CASigner.verify_bytes` expects the caller to provide one or more verification
keys via `opts={"pubkeys": [...]}`. Entries may be `cryptography` public-key
objects or PEM-encoded bytes. The signer reports success as soon as the required
number of signatures validates against the supplied key material.

**X.509 utilities**

Beyond detached signatures, `CASigner` assists with certificate authority tasks:

- `issue_self_signed` ? build a CA or leaf certificate directly from a
  `KeyRef` and subject mapping.
- `create_csr` ? generate a certificate signing request complete with SAN and
  key-usage extensions.
- `sign_csr` ? issue certificates from CSRs using an existing CA key and
  certificate chain.
- `verify_chain` ? validate a leaf against an intermediate chain and optional
  trust anchors with basic time and CA checks.

These helpers rely on the same key-loading logic demonstrated in the quickstart,
so PEM-encoded keys or `KeyRef.tags["crypto_obj"]` objects both work seamlessly.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/docs/readme/quick_start.py).

```python
import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_signing_ca import CASigner


async def main() -> None:
    signer = CASigner()

    private_key = ed25519.Ed25519PrivateKey.generate()
    key_ref = KeyRef(
        kid="demo-ed25519",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )

    message = b"trust but verify"
    signatures = await signer.sign_bytes(key_ref, message)
    signature = signatures[0]

    verified = await signer.verify_bytes(
        message,
        signatures,
        opts={"pubkeys": [private_key.public_key()]},
    )

    print("Signature algorithm:", signature["alg"])
    print("Key fingerprint:", key_ref.fingerprint)
    print("Signature valid:", verified)

    assert verified is True


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_signing_ca` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/docs/readme/usage.py).

```python
import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_signing_ca import CASigner


async def main() -> None:
    signer = CASigner()

    private_key = ed25519.Ed25519PrivateKey.generate()
    key_ref = KeyRef(
        kid="demo-ed25519",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )

    message = b"trust but verify"
    signatures = await signer.sign_bytes(key_ref, message)
    signature = signatures[0]

    verified = await signer.verify_bytes(
        message,
        signatures,
        opts={"pubkeys": [private_key.public_key()]},
    )

    print("Signature algorithm:", signature["alg"])
    print("Key fingerprint:", key_ref.fingerprint)
    print("Signature valid:", verified)

    assert verified is True


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_signing_ca` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/swarmauri_signing_ca/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_ca` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_ca` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CASigner`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_ca` is located in `standards` and owns certificate authority style signer for Swarmauri envelopes. Source-declared APIs include `CASigner`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_ca`.

Source-declared exports or types: `CASigner`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/swarmauri_signing_ca/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.signings` → `ca` → `swarmauri_signing_ca:CASigner`
- `swarmauri.signings` → `CASigner` → `swarmauri_signing_ca:CASigner`
<!-- readme-standards:end entry-points -->

The signer registers under the `swarmauri.signings` entry point as `CASigner` and
can be resolved through the Swarmauri plugin manager alongside other signing
implementations.

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_ca` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/swarmauri_signing_ca/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_signing_ca` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_signing_ca`, use the source-declared public interfaces (`CASigner`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_ca` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_ca`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/swarmauri_signing_ca/__init__.py). The `swarmauri_signing_ca` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_ca` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_ca` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_quickstart.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/tests/example/test_readme_quickstart.py)
- [tests/functional/test_signer_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/tests/functional/test_signer_functional.py)
- [tests/perf/test_signer_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/tests/perf/test_signer_perf.py)
- [tests/unit/test_rfc5280_cert_chain.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/tests/unit/test_rfc5280_cert_chain.py)
- [tests/unit/test_rfc5480_ecdsa.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/tests/unit/test_rfc5480_ecdsa.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_ca` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/swarmauri_signing_ca/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_ca` provides certificate authority style signer for Swarmauri envelopes; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_ca`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/swarmauri_signing_ca/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_ca` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/swarmauri_signing_ca/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml) provide the supporting context for `swarmauri_signing_ca`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_ca#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_ca)
- [pypi: swarmauri_signing_ca](https://pypi.org/project/swarmauri_signing_ca/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_signing_ca` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_signing_ca` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_ca` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_ca` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_ca` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ca/NOTICE) for attribution.
<!-- readme-standards:end notices -->
