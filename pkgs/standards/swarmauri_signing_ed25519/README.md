# swarmauri_signing_ed25519

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_ed25519</strong></p>
<p align="center">Ed25519-based signer for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_ed25519/"><img alt="pypi: swarmauri_signing_ed25519" src="https://img.shields.io/pypi/v/swarmauri_signing_ed25519"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_ed25519/"><img alt="Monthly PyPI downloads: swarmauri_signing_ed25519" src="https://img.shields.io/pypi/dm/swarmauri_signing_ed25519"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/README.md"><img alt="README hits: swarmauri_signing_ed25519" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_signing_ed25519/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_signing_ed25519` provides an Ed25519 implementation of the
`ISigning` interface for creating detached signatures over byte payloads and
canonicalized envelopes.

### Why This Package

`swarmauri_signing_ed25519` isolates this responsibility: Ed25519-based signer for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/swarmauri_signing_ed25519/__init__.py) exposes `Ed25519EnvelopeSigner`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_ed25519` when your integration needs ed25519-based signer for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Deterministic JSON canonicalization is always available, ensuring stable
  digests for dictionary-based envelopes.
- Optional CBOR canonicalization can be enabled with the `[cbor]` extra to
  install the `cbor2` dependency.
- Detached signatures are produced with `cryptography`'s Ed25519 primitives and
  returned as sequences so multi-signature workflows remain possible.
- Verification accepts multiple public keys via `opts["pubkeys"]` and honours
  `require={"min_signers": N}` for quorum checks.
- Ed25519 private keys can be supplied either as cryptography objects or raw
  seed bytes using the `KeyRef` helper structure from `swarmauri_core`.

### Non-Goals

`swarmauri_signing_ed25519` owns ed25519-based signer for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_ed25519
```
<!-- readme-standards:end installation.uv -->

```bash
uv add swarmauri_signing_ed25519
```

Install with the `[cbor]` extra when CBOR canonicalization is required:

```bash
pip install "swarmauri_signing_ed25519[cbor]"
poetry add swarmauri_signing_ed25519[cbor]
uv add swarmauri_signing_ed25519[cbor]
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_ed25519
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_signing_ed25519
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_ed25519
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_signing_ed25519
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/docs/readme/quick_start.py).

```python
import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner


async def main() -> bool:
    signer = Ed25519EnvelopeSigner()
    private_key = Ed25519PrivateKey.generate()
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    envelope = {"subject": "alice", "scope": ["inbox:read"]}
    signatures = await signer.sign_envelope(key_ref, envelope)

    public_key = private_key.public_key()
    verified = await signer.verify_envelope(
        envelope,
        signatures,
        opts={"pubkeys": [public_key]},
    )
    return verified


verified = asyncio.run(main())
print(f"Signature verified? {verified}")
```
<!-- readme-standards:end example.quick-start -->

The example below signs a JSON envelope and verifies the detached signature with
the generated public key.

<!-- example-start -->
<!-- example-end -->

#### Expected Result

The example demonstrates the documented `swarmauri_signing_ed25519` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/docs/readme/usage.py).

```python
import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner


async def main() -> bool:
    signer = Ed25519EnvelopeSigner()
    private_key = Ed25519PrivateKey.generate()
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    envelope = {"subject": "alice", "scope": ["inbox:read"]}
    signatures = await signer.sign_envelope(key_ref, envelope)

    public_key = private_key.public_key()
    verified = await signer.verify_envelope(
        envelope,
        signatures,
        opts={"pubkeys": [public_key]},
    )
    return verified


verified = asyncio.run(main())
print(f"Signature verified? {verified}")
```
<!-- readme-standards:end example.usage -->

The package exposes a single entry point, `Ed25519EnvelopeSigner`, implementing
`ISigning`. The signer reports JSON (and optionally CBOR) support via
`supports()`, canonicalizes envelopes through `canonicalize_envelope`, and
produces detached signatures using `sign_bytes`/`sign_envelope`. Verification
expects the relevant public keys to be supplied using `opts["pubkeys"]`.

**Key references**

`Ed25519EnvelopeSigner` accepts Ed25519 private keys using `KeyRef` values. The
two supported forms are:

- `{"kind": "cryptography_obj", "obj": Ed25519PrivateKey}` for in-memory
  cryptography objects.
- `{"kind": "raw_ed25519_sk", "bytes": seed}` where `seed` is the 32-byte
  private key seed (or the 64-byte expanded secret key).

### Configuration

Configure `swarmauri_signing_ed25519` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/swarmauri_signing_ed25519/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_ed25519` source raises `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_ed25519` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `Ed25519EnvelopeSigner`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_ed25519` is located in `standards` and owns ed25519-based signer for Swarmauri. Source-declared APIs include `Ed25519EnvelopeSigner`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_ed25519`.

Source-declared exports or types: `Ed25519EnvelopeSigner`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/swarmauri_signing_ed25519/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.signings` → `ed25519` → `swarmauri_signing_ed25519:Ed25519EnvelopeSigner`
- `swarmauri.signings` → `Ed25519EnvelopeSigner` → `swarmauri_signing_ed25519:Ed25519EnvelopeSigner`
<!-- readme-standards:end entry-points -->

The signer registers under the `swarmauri.signings` entry point as
`Ed25519EnvelopeSigner`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_ed25519` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/swarmauri_signing_ed25519/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_signing_jws`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_signing_ed25519`, use the source-declared public interfaces (`Ed25519EnvelopeSigner`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_ed25519` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_ed25519`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/swarmauri_signing_ed25519/__init__.py). The `swarmauri_signing_ed25519` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_ed25519` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_ed25519` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/tests/test_readme_example.py)
- [tests/functional/test_signer_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/tests/functional/test_signer_functional.py)
- [tests/perf/test_signer_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/tests/perf/test_signer_perf.py)
- [tests/unit/test_signer_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/tests/unit/test_signer_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_ed25519` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/swarmauri_signing_ed25519/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_ed25519` provides ed25519-based signer for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_ed25519`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/swarmauri_signing_ed25519/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_ed25519` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/swarmauri_signing_ed25519/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml) provide the supporting context for `swarmauri_signing_ed25519`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_signing_ed25519#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_signing_ed25519)
- [pypi: swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_signing_ed25519` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_signing_ed25519` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_ed25519` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_ed25519` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_ed25519` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ed25519/NOTICE) for attribution.
<!-- readme-standards:end notices -->
