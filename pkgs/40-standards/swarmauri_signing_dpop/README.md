# swarmauri_signing_dpop

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_dpop</strong></p>
<p align="center">DPoP signer/verifier for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_dpop/"><img alt="pypi: swarmauri_signing_dpop" src="https://img.shields.io/pypi/v/swarmauri_signing_dpop?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_dpop/"><img alt="Monthly PyPI downloads: swarmauri_signing_dpop" src="https://img.shields.io/pypi/dm/swarmauri_signing_dpop?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/README.md"><img alt="README hits: swarmauri_signing_dpop" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_signing_dpop/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

DPoP proof signer/verifier implementing RFC 9449 for proof-of-possession over HTTP requests.

Features:
- Creates and validates `dpop+jwt` proofs with embedded public JWK thumbprints.
- Supports `ES256`, `RS256`, and `EdDSA` algorithms through the `SigningBase` interface.
- Optional access-token hash binding (`ath`), nonce enforcement, and replay-protection hooks.

### Why This Package

`swarmauri_signing_dpop` isolates this responsibility: DPoP signer/verifier for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/swarmauri_signing_dpop/DpopSigner.py) exposes `DpopSigner`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_dpop` when your integration needs dPoP signer/verifier for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `DpopSigner`: DPoP proof signer/verifier that conforms to the SigningBase/ISigning

### Non-Goals

`swarmauri_signing_dpop` owns dPoP signer/verifier for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-signing-jws`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

The package is published on PyPI together with the dependencies required to sign and verify DPoP proofs.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_dpop
```
<!-- readme-standards:end installation.uv -->

```bash
uv add swarmauri_signing_dpop
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_dpop
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_signing_dpop
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_dpop
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_signing_dpop
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/docs/readme/quick_start.py).

```python
import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner


async def main() -> None:
    signer = DpopSigner()

    private_key = ed25519.Ed25519PrivateKey.generate()
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key = {"kind": "pem", "priv": priv_pem, "alg": "EdDSA"}

    signatures = await signer.sign_bytes(
        key,
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x"},
    )

    is_valid = await signer.verify_bytes(
        b"",
        signatures,
        require={"htm": "GET", "htu": "https://api.example/x"},
    )
    assert is_valid
    print("DPoP proof valid:", is_valid)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_signing_dpop` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/docs/readme/usage.py).

```python
import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner


async def main() -> None:
    signer = DpopSigner()

    private_key = ed25519.Ed25519PrivateKey.generate()
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key = {"kind": "pem", "priv": priv_pem, "alg": "EdDSA"}

    signatures = await signer.sign_bytes(
        key,
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x"},
    )

    is_valid = await signer.verify_bytes(
        b"",
        signatures,
        require={"htm": "GET", "htu": "https://api.example/x"},
    )
    assert is_valid
    print("DPoP proof valid:", is_valid)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

`DpopSigner` implements the asynchronous `SigningBase` / `ISigning` interface. Signing requires the HTTP method and URL (`opts['htm']` and `opts['htu']`), and verification requires the same data passed via `require`.

**Signing and verifying a request**


**Signature format**

`sign_bytes` and `sign_envelope` return a sequence with a single detached signature entry:

```python
{
    "alg": "EdDSA",            # JWS algorithm used
    "format": "dpop+jwt",      # proof media type
    "sig": "<compact JWT>",    # DPoP proof token containing the claims
    "jkt": "<thumbprint>",     # SHA-256 JWK thumbprint for cnf.jkt binding
}
```

Use the `jkt` helper when comparing against `cnf.jkt` values embedded in access tokens.

**Key references**

Keys are provided using the `KeyRef` mapping expected by other Swarmauri signing packages:

- `{ "kind": "pem", "priv": <PEM bytes|str> }` ? RSA/EC keys and Ed25519 PKCS8 PEM.
- `{ "kind": "jwk", "priv": <private JWK dict> }` ? accepts EC, RSA, or OKP keys with private fields.

For Ed25519 material, both formats are supported; the signer derives and embeds the public JWK automatically.

**Options reference**

- `opts['htm']` / `opts['htu']`: HTTP method and URL that will be bound in the proof (required for signing).
- `opts['nonce']`: Optional server-issued `DPoP-Nonce` to include in the proof.
- `opts['access_token']`: Optional access token to derive the `ath` confirmation hash.
- `require['htm']` / `require['htu']`: Expected method and URL (required for verification).
- `require['max_skew_s']`: IAT skew tolerance (defaults to 300 seconds).
- `require['algs']`: Allowed signing algorithms. Defaults to all supported values.
- `require['nonce']`: Expected nonce when enforcing a server challenge.
- `require['access_token']`: Expected bearer token when validating `ath`.
- `require['replay']`: Mapping with `seen(jti) -> bool` and `mark(jti, ttl_s)` callables for replay prevention.

`sign_envelope` and `verify_envelope` reuse the same logic after canonicalizing the envelope to bytes (`raw` or `json`). Payload bytes are otherwise unused because the DPoP proof binds request metadata instead of message content.

### Configuration

Configure `swarmauri_signing_dpop` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/swarmauri_signing_dpop/DpopSigner.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_dpop` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_dpop` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `DpopSigner`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_dpop` is located in `standards` and owns dPoP signer/verifier for Swarmauri. Source-declared APIs include `DpopSigner`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_dpop`.

Source-declared exports or types: `DpopSigner`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/swarmauri_signing_dpop/DpopSigner.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.signings` → `dpop` → `swarmauri_signing_dpop:DpopSigner`
- `swarmauri.signings` → `DpopSigner` → `swarmauri_signing_dpop:DpopSigner`
<!-- readme-standards:end entry-points -->

The signer registers under the `swarmauri.signings` entry point as `DpopSigner`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_dpop` are `swarmauri-core`, `swarmauri-base`, `swarmauri-signing-jws`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/swarmauri_signing_dpop/DpopSigner.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_signing_dpop` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_signing_dpop`, use the source-declared public interfaces (`DpopSigner`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_dpop` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_dpop`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/swarmauri_signing_dpop/DpopSigner.py). The `swarmauri_signing_dpop` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_dpop` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_dpop` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/tests/test_readme_example.py)
- [tests/unit/test_dpop_replay_hooks.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/tests/unit/test_dpop_replay_hooks.py)
- [tests/unit/test_dpop_signer.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/tests/unit/test_dpop_signer.py)
- [tests/unit/test_dpop_signer_ath.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/tests/unit/test_dpop_signer_ath.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_dpop` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/swarmauri_signing_dpop/DpopSigner.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_dpop` provides dPoP signer/verifier for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_dpop`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/swarmauri_signing_dpop/DpopSigner.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_dpop` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/swarmauri_signing_dpop/DpopSigner.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml) provide the supporting context for `swarmauri_signing_dpop`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_signing_jws](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/README.md): Composite JWS signer/verifier for Swarmauri

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_dpop#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_dpop)
- [pypi: swarmauri_signing_dpop](https://pypi.org/project/swarmauri_signing_dpop/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_signing_dpop` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_signing_dpop` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_dpop` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_dpop` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_dpop` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_dpop/NOTICE) for attribution.
<!-- readme-standards:end notices -->
