# swarmauri_signing_jws

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_jws</strong></p>
<p align="center">Composite JWS signer/verifier for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_jws/"><img alt="pypi: swarmauri_signing_jws" src="https://img.shields.io/pypi/v/swarmauri_signing_jws?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_jws/"><img alt="Monthly PyPI downloads: swarmauri_signing_jws" src="https://img.shields.io/pypi/dm/swarmauri_signing_jws?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/README.md"><img alt="README hits: swarmauri_signing_jws" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_signing_jws/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Composite JSON Web Signature (JWS) signer and verifier that orchestrates
multiple Swarmauri signing providers behind a single asynchronous API.

### Why This Package

`swarmauri_signing_jws` isolates this responsibility: Composite JWS signer/verifier for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/swarmauri_signing_jws/jws_signer.py) exposes `JWSSigner`, `JwsResult`, `JwsSignerVerifier`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_jws` when your integration needs composite JWS signer/verifier for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Async helpers for both compact and general JSON JWS serialization
- Algorithm routing across HMAC (HS256/384/512), RSA (RS*/PS*), ECDSA
  (ES256/384/512), Ed25519 (EdDSA), and optional secp256k1 (ES256K when the
  `secp256k1` extra is installed)
- Works with direct key material, Swarmauri signer objects, or a JWKS resolver
  while returning the protected header and payload via `JwsResult`

### Non-Goals

`swarmauri_signing_jws` owns composite JWS signer/verifier for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-signing-hmac`, `swarmauri-signing-rsa`, `swarmauri-signing-ecdsa`, `swarmauri-signing-ed25519`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_jws
```
<!-- readme-standards:end installation.uv -->

To add the dependency to a `pyproject.toml` managed by `uv`:

```bash
uv add swarmauri_signing_jws
```

Or install it into the active environment:

```bash
uv pip install swarmauri_signing_jws
```

Optional extras:

- `secp256k1` enables ES256K support through `swarmauri_signing_secp256k1`

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_jws
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_signing_jws
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_jws
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_signing_jws
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/docs/readme/quick_start.py).

```python
import asyncio
from swarmauri_signing_jws import JwsSignerVerifier


async def main() -> None:
    signer = JwsSignerVerifier()
    key = {"kind": "raw", "key": "0" * 32}

    compact = await signer.sign_compact(
        payload={"msg": "hi"},
        alg="HS256",
        key=key,
    )

    result = await signer.verify_compact(
        compact,
        hmac_keys=[key],
    )

    print(result.payload.decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_signing_jws` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/docs/readme/usage.py).

```python
import asyncio
from swarmauri_signing_jws import JwsSignerVerifier


async def main() -> None:
    signer = JwsSignerVerifier()
    key = {"kind": "raw", "key": "0" * 32}

    compact = await signer.sign_compact(
        payload={"msg": "hi"},
        alg="HS256",
        key=key,
    )

    result = await signer.verify_compact(
        compact,
        hmac_keys=[key],
    )

    print(result.payload.decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The public methods accept either raw strings or `JWAAlg` enum values for the
`alg` parameter. Compact verification returns a `JwsResult` dataclass containing
the parsed header and payload bytes so applications can safely forward or decode
the authenticated message.

### Configuration

Configure `swarmauri_signing_jws` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/swarmauri_signing_jws/jws_signer.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_jws` source raises `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_jws` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `JWSSigner`, `JwsResult`, `JwsSignerVerifier`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_jws` is located in `standards` and owns composite JWS signer/verifier for Swarmauri. Source-declared APIs include `JWSSigner`, `JwsResult`, `JwsSignerVerifier`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_jws`.

Source-declared exports or types: `JWSSigner`, `JwsResult`, `JwsSignerVerifier`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/swarmauri_signing_jws/jws_signer.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.signings` → `jws` → `swarmauri_signing_jws:JwsSignerVerifier`
- `swarmauri.signings` → `JwsSignerVerifier` → `swarmauri_signing_jws:JwsSignerVerifier`
<!-- readme-standards:end entry-points -->

The signer registers under the `swarmauri.signings` entry point as
`JwsSignerVerifier`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_jws` are `swarmauri-core`, `swarmauri-base`, `swarmauri-signing-hmac`, `swarmauri-signing-rsa`, `swarmauri-signing-ecdsa`, `swarmauri-signing-ed25519`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/swarmauri_signing_jws/jws_signer.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `MediaSigner`, `swarmauri_middleware_jwt`, `swarmauri_signing_dpop`, `swarmauri_tokens_jwt`, `swarmauri_transport_https_unicast`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_signing_jws`, use the source-declared public interfaces (`JWSSigner`, `JwsResult`, `JwsSignerVerifier`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_jws` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_jws`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/swarmauri_signing_jws/jws_signer.py). The `swarmauri_signing_jws` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_jws` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_jws` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/tests/test_readme_example.py)
- [tests/functional/test_jws_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/tests/functional/test_jws_functional.py)
- [tests/perf/test_jws_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/tests/perf/test_jws_perf.py)
- [tests/unit/test_jws_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/tests/unit/test_jws_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_jws` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/swarmauri_signing_jws/jws_signer.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_jws` provides composite JWS signer/verifier for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_jws`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/swarmauri_signing_jws/jws_signer.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_jws` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/swarmauri_signing_jws/jws_signer.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml) provide the supporting context for `swarmauri_signing_jws`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_signing_ecdsa](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ecdsa/README.md): ECDSA-based signer for Swarmauri
- [swarmauri_signing_ed25519](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_ed25519/README.md): Ed25519-based signer for Swarmauri
- [swarmauri_signing_hmac](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_hmac/README.md): HMAC-based signer for Swarmauri
- [swarmauri_signing_rsa](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_rsa/README.md): RSA-based signer for Swarmauri

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_jws#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_jws)
- [pypi: swarmauri_signing_jws](https://pypi.org/project/swarmauri_signing_jws/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_signing_jws` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**API highlights**

- `sign_compact(...)` / `verify_compact(...)` wrap the standard compact
  serialization, including optional allowlists and JWKS resolvers.
- `sign_general_json(...)` / `verify_general_json(...)` operate on the general
  JSON serialization and support multi-signer verification with `min_signers`
  thresholds.
- Each algorithm family accepts dedicated key collections (`hmac_keys`,
  `rsa_pubkeys`, `ec_pubkeys`, `ed_pubkeys`, `k1_pubkeys`) or a `jwks_resolver`
  callback for dynamic key retrieval.

**HMAC key requirements**

All HMAC-based operations **require a secret of at least 32 bytes (256 bits)**.
Shorter keys are rejected to avoid truncation mistakes and to keep forgery
probabilities negligible even after many verification attempts.

Rationale:

- Forgery success scales with tag length; a 256-bit tag keeps the chance
  negligible even after many tries ([NIST SP 800-107 Rev.1](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-107r1.pdf)).
- [RFC 7518](https://datatracker.ietf.org/doc/html/rfc7518) already mandates
  HS256 keys >= 256 bits; using the full HMAC-SHA-256 output avoids
  inadvertent strength reduction.
- A full 32-byte tag preserves approximately 128-bit security even under generic quantum
  search speedups ([NIST IR 8547](https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf)).
- Fixed-length tags simplify constant-time verification and prevent
  configuration mismatches.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_jws` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_jws` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_jws` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/NOTICE) for attribution.
<!-- readme-standards:end notices -->
