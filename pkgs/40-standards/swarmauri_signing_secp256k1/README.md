# swarmauri_signing_secp256k1

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_secp256k1</strong></p>
<p align="center">secp256k1-based signer for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_secp256k1/"><img alt="pypi: swarmauri_signing_secp256k1" src="https://img.shields.io/pypi/v/swarmauri_signing_secp256k1?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_secp256k1/"><img alt="Monthly PyPI downloads: swarmauri_signing_secp256k1" src="https://img.shields.io/pypi/dm/swarmauri_signing_secp256k1?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/README.md"><img alt="README hits: swarmauri_signing_secp256k1" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_signing_secp256k1/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

An opinionated secp256k1 ECDSA signer that implements the Swarmauri
`ISigning` interface for detached signatures over raw bytes and
canonicalized envelopes.

### Why This Package

`swarmauri_signing_secp256k1` isolates this responsibility: secp256k1-based signer for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/swarmauri_signing_secp256k1/__init__.py) exposes `Secp256k1EnvelopeSigner`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_secp256k1` when your integration needs secp256k1-based signer for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Asynchronous API** ? `sign_bytes`, `verify_bytes`, `sign_envelope`, and
  `verify_envelope` operate with `asyncio` and return canonical Swarmauri
  signature payloads.
- **Multiple canonicalizations** ? JSON canonicalization is always
  available, while CBOR canonicalization can be enabled with the optional
  `cbor2` dependency.
- **Flexible key loading** ? accepts PEM strings/paths, JWK dictionaries, or
  native `cryptography` key objects via the `KeyRef` protocol.
- **Deterministic verification requirements** ? verification expects one or
  more secp256k1 public keys provided through `opts["pubkeys"]`.
- **Signature format control** ? DER encoding is returned by default; supply
  `opts={"format": "RAW"}` when signing or verifying to work with
  JOSE-style `r || s` concatenated signatures.

### Non-Goals

`swarmauri_signing_secp256k1` owns secp256k1-based signer for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

The package requires `cryptography` and, optionally, `cbor2` when CBOR
canonicalization is needed.

```bash
pip install swarmauri_signing_secp256k1

# install with CBOR canonicalization support
pip install "swarmauri_signing_secp256k1[cbor]"
```

```bash
poetry add swarmauri_signing_secp256k1
```

```bash
uv add swarmauri_signing_secp256k1

# with the optional CBOR extra
uv add "swarmauri_signing_secp256k1[cbor]"
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_secp256k1
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_secp256k1
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_secp256k1
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/docs/readme/quick_start.py).

```python
import asyncio

from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_secp256k1 import Secp256k1EnvelopeSigner


async def main() -> bool:
    signer = Secp256k1EnvelopeSigner()

    private_key = ec.generate_private_key(ec.SECP256K1())
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    payload = b"hello from secp256k1"
    signatures = await signer.sign_bytes(key_ref, payload)

    public_key_ref = {
        "kind": "cryptography_obj",
        "obj": private_key.public_key(),
    }
    is_valid = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [public_key_ref]},
    )

    print(f"Signature valid? {is_valid}")
    assert is_valid
    return is_valid


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_signing_secp256k1` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/docs/readme/usage.py).

```python
import asyncio

from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_secp256k1 import Secp256k1EnvelopeSigner


async def main() -> bool:
    signer = Secp256k1EnvelopeSigner()

    private_key = ec.generate_private_key(ec.SECP256K1())
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    payload = b"hello from secp256k1"
    signatures = await signer.sign_bytes(key_ref, payload)

    public_key_ref = {
        "kind": "cryptography_obj",
        "obj": private_key.public_key(),
    }
    is_valid = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [public_key_ref]},
    )

    print(f"Signature valid? {is_valid}")
    assert is_valid
    return is_valid


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

**Sign and verify raw bytes**

The signer derives a key identifier (`kid`) from the provided private key and
requires the corresponding public key when verifying signatures.

<!-- example-start -->
<!-- example-end -->

**Canonicalized envelopes**

To sign envelopes, pass JSON-serializable dictionaries (and optionally
`canon="cbor"`). Canonicalization reuses the same raw signing logic shown
above:

```python
envelope = {"payload": {"msg": "hello"}}
signatures = await signer.sign_envelope(key_ref, envelope, canon="json")
is_valid = await signer.verify_envelope(
    envelope,
    signatures,
    opts={"pubkeys": [public_key_ref]},
)
```

### Configuration

Configure `swarmauri_signing_secp256k1` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/swarmauri_signing_secp256k1/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_secp256k1` source raises `InvalidSignature`, `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_secp256k1` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `Secp256k1EnvelopeSigner`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_secp256k1` is located in `standards` and owns secp256k1-based signer for Swarmauri. Source-declared APIs include `Secp256k1EnvelopeSigner`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_secp256k1`.

Source-declared exports or types: `Secp256k1EnvelopeSigner`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/swarmauri_signing_secp256k1/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.signings` → `secp256k1` → `swarmauri_signing_secp256k1:Secp256k1EnvelopeSigner`
- `swarmauri.signings` → `Secp256k1EnvelopeSigner` → `swarmauri_signing_secp256k1:Secp256k1EnvelopeSigner`
<!-- readme-standards:end entry-points -->

The signer registers under the `swarmauri.signings` entry point as
`Secp256k1EnvelopeSigner`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_secp256k1` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/swarmauri_signing_secp256k1/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_signing_secp256k1` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_signing_secp256k1`, use the source-declared public interfaces (`Secp256k1EnvelopeSigner`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_secp256k1` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_secp256k1`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/swarmauri_signing_secp256k1/__init__.py). The `swarmauri_signing_secp256k1` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_secp256k1` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_secp256k1` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/tests/test_readme_example.py)
- [tests/functional/test_signer_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/tests/functional/test_signer_functional.py)
- [tests/perf/test_signer_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/tests/perf/test_signer_perf.py)
- [tests/unit/test_signer_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/tests/unit/test_signer_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_secp256k1` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/swarmauri_signing_secp256k1/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_secp256k1` provides secp256k1-based signer for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_secp256k1`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/swarmauri_signing_secp256k1/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_secp256k1` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/swarmauri_signing_secp256k1/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml) provide the supporting context for `swarmauri_signing_secp256k1`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_secp256k1#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_secp256k1)
- [pypi: swarmauri_signing_secp256k1](https://pypi.org/project/swarmauri_signing_secp256k1/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_signing_secp256k1` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_signing_secp256k1` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_secp256k1` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_secp256k1` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_secp256k1` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_secp256k1/NOTICE) for attribution.
<!-- readme-standards:end notices -->
