# swarmauri_tokens_rotatingjwt

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tokens_rotatingjwt</strong></p>
<p align="center">Rotating JWT token service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_rotatingjwt/"><img alt="pypi: swarmauri_tokens_rotatingjwt" src="https://img.shields.io/pypi/v/swarmauri_tokens_rotatingjwt"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_rotatingjwt/"><img alt="Monthly PyPI downloads: swarmauri_tokens_rotatingjwt" src="https://img.shields.io/pypi/dm/swarmauri_tokens_rotatingjwt"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/README.md"><img alt="README hits: swarmauri_tokens_rotatingjwt" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tokens_rotatingjwt/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Rotating JWT token service plugin for Swarmauri.

This package provides a token issuer/verifier that automatically rotates its
signing key.  It exposes a `RotatingJWTTokenService` implementing
`ITokenService` and conforms to RFC 7515, 7517, 7518 and 7519.

### Why This Package

`swarmauri_tokens_rotatingjwt` isolates this responsibility: Rotating JWT token service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/swarmauri_tokens_rotatingjwt/__init__.py) exposes `RotatingJWTTokenService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tokens_rotatingjwt` when your integration needs rotating JWT token service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Supports RS256, PS256, ES256, EdDSA and HS256 algorithms.
- Automatic key rotation based on time or token count.
- JWKS publication retaining previous key versions.

### Non-Goals

`swarmauri_tokens_rotatingjwt` owns rotating JWT token service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `pyjwt`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tokens_rotatingjwt
```

Optional extras are available for specific signing canons:

```bash
uv add swarmauri_tokens_rotatingjwt[rsa]
uv add swarmauri_tokens_rotatingjwt[ecdsa]
uv add swarmauri_tokens_rotatingjwt[eddsa]
uv add swarmauri_tokens_rotatingjwt[hmac]
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tokens_rotatingjwt
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tokens_rotatingjwt
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tokens_rotatingjwt
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_tokens_rotatingjwt")
assert package.__name__ == "swarmauri_tokens_rotatingjwt"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_tokens_rotatingjwt`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_tokens_rotatingjwt")
assert package.__name__ == "swarmauri_tokens_rotatingjwt"
```
<!-- readme-standards:end example.usage -->

```python
from swarmauri_tokens_rotatingjwt import RotatingJWTTokenService
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider
from swarmauri_core.crypto.types import JWAAlg

kp = InMemoryKeyProvider()
service = RotatingJWTTokenService(kp, alg=JWAAlg.RS256)

token = await service.mint({"sub": "alice"}, alg=JWAAlg.RS256)
claims = await service.verify(token)
jwks = await service.jwks()
```

The service handles key rotation based on time or token volume and exposes a
JWKS endpoint that includes previous keys so existing tokens remain valid.

### Configuration

Configure `swarmauri_tokens_rotatingjwt` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/swarmauri_tokens_rotatingjwt/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tokens_rotatingjwt` source raises `RuntimeError`, `ValueError`, `jwt.InvalidTokenError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tokens_rotatingjwt` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `RotatingJWTTokenService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tokens_rotatingjwt` is located in `standards` and owns rotating JWT token service for Swarmauri. Source-declared APIs include `RotatingJWTTokenService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tokens_rotatingjwt`.

Source-declared exports or types: `RotatingJWTTokenService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/swarmauri_tokens_rotatingjwt/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.tokens` → `rotating_jwt` → `swarmauri_tokens_rotatingjwt:RotatingJWTTokenService`
- `swarmauri.tokens` → `RotatingJWTTokenService` → `swarmauri_tokens_rotatingjwt:RotatingJWTTokenService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tokens_rotatingjwt` are `swarmauri-core`, `swarmauri-base`, `pyjwt`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/swarmauri_tokens_rotatingjwt/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tokens_rotatingjwt` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tokens_rotatingjwt`, use the source-declared public interfaces (`RotatingJWTTokenService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tokens_rotatingjwt` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tokens_rotatingjwt`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/swarmauri_tokens_rotatingjwt/__init__.py). The `swarmauri_tokens_rotatingjwt` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tokens_rotatingjwt` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tokens_rotatingjwt` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_performance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/tests/test_performance.py)
- [tests/test_rfc7515_jws.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/tests/test_rfc7515_jws.py)
- [tests/test_rfc7517_jwks.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/tests/test_rfc7517_jwks.py)
- [tests/test_rfc7518_jwa.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/tests/test_rfc7518_jwa.py)
- [tests/test_rfc7519_jwt.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/tests/test_rfc7519_jwt.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tokens_rotatingjwt` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/swarmauri_tokens_rotatingjwt/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tokens_rotatingjwt` provides rotating JWT token service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tokens_rotatingjwt`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/swarmauri_tokens_rotatingjwt/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tokens_rotatingjwt` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/swarmauri_tokens_rotatingjwt/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml) provide the supporting context for `swarmauri_tokens_rotatingjwt`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tokens_rotatingjwt](https://pypi.org/project/swarmauri_tokens_rotatingjwt/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tokens_rotatingjwt` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_tokens_rotatingjwt` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tokens_rotatingjwt` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tokens_rotatingjwt` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tokens_rotatingjwt` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_rotatingjwt/NOTICE) for attribution.
<!-- readme-standards:end notices -->
