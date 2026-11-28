# swarmauri_signing_pep458

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_pep458</strong></p>
<p align="center">PEP 458 compatible detached signing provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_pep458/"><img alt="pypi: swarmauri_signing_pep458" src="https://img.shields.io/pypi/v/swarmauri_signing_pep458?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_pep458/"><img alt="Monthly PyPI downloads: swarmauri_signing_pep458" src="https://img.shields.io/pypi/dm/swarmauri_signing_pep458?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/README.md"><img alt="README hits: swarmauri_signing_pep458" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_signing_pep458/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_signing_pep458` packages a detached signature provider that implements
[PEP 458](https://peps.python.org/pep-0458/) style signing for The Update Framework
(TUF) metadata. It brings canonical JSON, multi-algorithm support, and quorum-aware
verification to the Swarmauri runtime so supply-chain aware components can produce
and validate repository metadata with a uniform API.

### Why This Package

`swarmauri_signing_pep458` isolates this responsibility: PEP 458 compatible detached signing provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/swarmauri_signing_pep458/__init__.py) exposes `Pep458Signer`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_pep458` when your integration needs pEP 458 compatible detached signing provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `Pep458Signer`: Detached signer aligned with the TUF/PEP 458 metadata format.

### Non-Goals

`swarmauri_signing_pep458` owns pEP 458 compatible detached signing provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

**Using uv**

```bash
uv add swarmauri_signing_pep458
```

**Using pip**

```bash
pip install swarmauri_signing_pep458
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_pep458
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_pep458
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_pep458
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/docs/readme/quick_start.py).

```python
import asyncio
from cryptography.hazmat.primitives.asymmetric import ed25519
from swarmauri_signing_pep458 import Pep458Signer


async def main() -> None:
    signer = Pep458Signer()
    private = ed25519.Ed25519PrivateKey.generate()
    keyref = {"kind": "cryptography_obj", "obj": private, "alg": "Ed25519"}

    payload = b"release metadata"
    signatures = await signer.sign_bytes(keyref, payload)

    is_valid = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [private.public_key()]},
    )
    print(f"Signature valid? {is_valid}")


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_signing_pep458` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/docs/readme/usage.py).

```python
import asyncio
from cryptography.hazmat.primitives.asymmetric import ed25519
from swarmauri_signing_pep458 import Pep458Signer


async def main() -> None:
    signer = Pep458Signer()
    private = ed25519.Ed25519PrivateKey.generate()
    keyref = {"kind": "cryptography_obj", "obj": private, "alg": "Ed25519"}

    payload = b"release metadata"
    signatures = await signer.sign_bytes(keyref, payload)

    is_valid = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [private.public_key()]},
    )
    print(f"Signature valid? {is_valid}")


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_signing_pep458` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/swarmauri_signing_pep458/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_pep458` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_pep458` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `Pep458Signer`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_pep458` is located in `standards` and owns pEP 458 compatible detached signing provider for Swarmauri. Source-declared APIs include `Pep458Signer`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_pep458`.

Source-declared exports or types: `Pep458Signer`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/swarmauri_signing_pep458/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_pep458` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/swarmauri_signing_pep458/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_signing_pep458` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_signing_pep458`, use the source-declared public interfaces (`Pep458Signer`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_pep458` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_pep458`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/swarmauri_signing_pep458/__init__.py). The `swarmauri_signing_pep458` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_pep458` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_pep458` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_pep458_signer.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/tests/unit/test_pep458_signer.py)
- [tests/unit/test_pep458_signer_helpers.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/tests/unit/test_pep458_signer_helpers.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_pep458` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/swarmauri_signing_pep458/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_pep458` provides pEP 458 compatible detached signing provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_pep458`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/swarmauri_signing_pep458/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_pep458` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/swarmauri_signing_pep458/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml) provide the supporting context for `swarmauri_signing_pep458`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_pep458#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_pep458)
- [pypi: swarmauri_signing_pep458](https://pypi.org/project/swarmauri_signing_pep458/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_signing_pep458`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

- Format the code with `ruff format .` and lint with `ruff check . --fix`.
- Run the asynchronous unit tests with `pytest` once cryptography dependencies are
  available.
- Contributions should include updates to documentation fragments and policy tables
  when new capabilities are added.

### Notes for Maintainers

**Key Features**

- **PEP 458 compatible format** ? Signatures emit the `tuf/pep458` envelope with
  `method`, `keyid`, and base64-encoded payloads so the metadata aligns with the
  specification's detached signature requirements.
- **Deterministic canonicalization** ? Canonicalizes envelopes using TUF's
  lexicographically-sorted JSON encoding to guarantee byte-for-byte reproducibility.
- **Multiple signature algorithms** ? Supports Ed25519 for online roles and
  RSA-PSS-SHA256 for offline root-style metadata, allowing you to mix schemes per
  role.
- **Quorum aware verification** ? Enforces `min_signers`, explicit key-id allow
  lists, and algorithm restrictions during verification to help model offline
  threshold signing policies.
- **Flexible key inputs** ? Accepts cryptography key objects, PEM encoded key
  material, or Swarmauri `KeyRef` dictionaries for both signing and verification.

**Signature Format**

Each signature returned by the signer follows this shape:

```json
{
  "format": "tuf/pep458",
  "method": "ed25519",
  "alg": "Ed25519",
  "keyid": "base64(SHA256(method || SPKI))",
  "sig": "base64(signature-bytes)"
}
```

Use the `method` label when matching public keys and verifying thresholds for a
particular TUF role.

**Verification Policy Hints**

The `verify_bytes` and `verify_envelope` APIs accept a `require` mapping with the
following helpful keys:

- `min_signers`: Require at least _n_ distinct key ids to validate.
- `algs`: Restrict verification to a subset of algorithms, e.g. `("Ed25519",)`. The
  values are normalized case-insensitively.
- `kids`: Whitelist key identifiers allowed to satisfy the policy.
- `pubkeys`: Explicit public key materials to use when verifying (PEM strings,
  cryptography objects, or `{"kind": "pem", "pub": ...}` dictionaries).

**Relationship to the Cipher Suite**

Pair this package with `swarmauri_cipher_suite_pep458` to describe repository role
policies, canonicalization settings, and default algorithm choices across the
Swarmauri ecosystem.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_pep458` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_pep458` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_pep458` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the [Apache License 2.0](LICENSE).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pep458/NOTICE) for attribution.
<!-- readme-standards:end notices -->
