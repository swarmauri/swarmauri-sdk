# swarmauri_middleware_jwksverifier

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_middleware_jwksverifier</strong></p>
<p align="center">JWKS-based JWT verification middleware for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_jwksverifier/"><img alt="pypi: swarmauri_middleware_jwksverifier" src="https://img.shields.io/pypi/v/swarmauri_middleware_jwksverifier?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_jwksverifier/"><img alt="Monthly PyPI downloads: swarmauri_middleware_jwksverifier" src="https://img.shields.io/pypi/dm/swarmauri_middleware_jwksverifier?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/README.md"><img alt="README hits: swarmauri_middleware_jwksverifier" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_middleware_jwksverifier/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A middleware component providing JWT verification using a cached JWKS with TTL
and LRU eviction.

### Why This Package

`swarmauri_middleware_jwksverifier` isolates this responsibility: JWKS-based JWT verification middleware for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/swarmauri_middleware_jwksverifier/__init__.py) exposes `CachedJWKSVerifier`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_middleware_jwksverifier` when your integration needs jWKS-based JWT verification middleware for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Parses RSA, EC, Ed25519, and HMAC keys from JWKS documents (RFC 7517).
- Thread-safe cache with configurable TTL refresh and LRU eviction limits.
- Optional constructor guards for allowed algorithms and issuer values.
- Manual cache controls for forced refreshes, invalidation, and overrides.

### Non-Goals

`swarmauri_middleware_jwksverifier` owns jWKS-based JWT verification middleware for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `pyjwt`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_middleware_jwksverifier
```

```bash
poetry add swarmauri_middleware_jwksverifier
```

```bash
uv pip install swarmauri_middleware_jwksverifier
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_middleware_jwksverifier
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_middleware_jwksverifier
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_middleware_jwksverifier
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

`CachedJWKSVerifier` expects a callable that returns a JWKS document. The fetch
callback is invoked whenever the cache expires (default `ttl_s=300` seconds) or
when a forced refresh is requested.

The verifier exposes a `verify` helper that performs signature validation and
standard PyJWT checks. Pass the algorithms you are willing to accept by
supplying the `algorithms_whitelist` parameter on every verification call. If
you do not provide an explicit `issuer`, the first value from
`allowed_issuers` (if configured during construction) is used.


**Cache management helpers**

- `refresh(force: bool = False)` ? trigger a JWKS refresh immediately when
  `force` is true or the cache has expired.
- `invalidate(kid: Optional[str] = None)` ? drop either a specific key or the
  entire cache, including overrides.
- `inject_override_key(kid, key_obj)` / `inject_override_jwk(kid, jwk)` ? add
  temporary key material that bypasses JWKS fetching when resolving by `kid`.
- `key_resolver()` ? obtain a callable suitable for advanced PyJWT usage when
  integrating with other verification flows.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/docs/readme/quick_start.py).

```python
import base64

import jwt

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier

SECRET = b"super-secret-signing-key"


def fetch_jwks() -> dict[str, object]:
    return {
        "keys": [
            {
                "kty": "oct",
                "kid": "demo",
                "k": base64.urlsafe_b64encode(SECRET)
                .rstrip(b"=")
                .decode("ascii"),
                "alg": "HS256",
            }
        ]
    }


verifier = CachedJWKSVerifier(fetch=fetch_jwks, ttl_s=60)

token = jwt.encode(
    {"sub": "user-123", "aud": "example-service"},
    SECRET,
    algorithm="HS256",
    headers={"kid": "demo"},
)

claims = verifier.verify(
    token,
    algorithms_whitelist=["HS256"],
    audience="example-service",
)

print(claims["sub"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_middleware_jwksverifier` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/docs/readme/usage.py).

```python
import base64

import jwt

from swarmauri_middleware_jwksverifier import CachedJWKSVerifier

SECRET = b"super-secret-signing-key"


def fetch_jwks() -> dict[str, object]:
    return {
        "keys": [
            {
                "kty": "oct",
                "kid": "demo",
                "k": base64.urlsafe_b64encode(SECRET)
                .rstrip(b"=")
                .decode("ascii"),
                "alg": "HS256",
            }
        ]
    }


verifier = CachedJWKSVerifier(fetch=fetch_jwks, ttl_s=60)

token = jwt.encode(
    {"sub": "user-123", "aud": "example-service"},
    SECRET,
    algorithm="HS256",
    headers={"kid": "demo"},
)

claims = verifier.verify(
    token,
    algorithms_whitelist=["HS256"],
    audience="example-service",
)

print(claims["sub"])
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_middleware_jwksverifier` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/swarmauri_middleware_jwksverifier/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_middleware_jwksverifier` source raises `RuntimeError`, `TypeError`, `ValueError`, `jwt.InvalidAlgorithmError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_middleware_jwksverifier` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CachedJWKSVerifier`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_middleware_jwksverifier` is located in `standards` and owns jWKS-based JWT verification middleware for Swarmauri. Source-declared APIs include `CachedJWKSVerifier`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_middleware_jwksverifier`.

Source-declared exports or types: `CachedJWKSVerifier`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/swarmauri_middleware_jwksverifier/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.middlewares` → `CachedJWKSVerifier` → `swarmauri_middleware_jwksverifier:CachedJWKSVerifier`
<!-- readme-standards:end entry-points -->

The middleware registers under the `swarmauri.middlewares` entry point as
`CachedJWKSVerifier`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_middleware_jwksverifier` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `pyjwt`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/swarmauri_middleware_jwksverifier/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_middleware_jwksverifier` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_middleware_jwksverifier`, use the source-declared public interfaces (`CachedJWKSVerifier`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_middleware_jwksverifier` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_middleware_jwksverifier`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/swarmauri_middleware_jwksverifier/__init__.py). The `swarmauri_middleware_jwksverifier` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_middleware_jwksverifier` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_middleware_jwksverifier` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/tests/test_readme_example.py)
- [tests/functional/test_jwksverifier_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/tests/functional/test_jwksverifier_functional.py)
- [tests/perf/test_jwksverifier_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/tests/perf/test_jwksverifier_perf.py)
- [tests/unit/test_jwksverifier_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/tests/unit/test_jwksverifier_unit.py)
- [tests/unit/test_rfc7515_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/tests/unit/test_rfc7515_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_middleware_jwksverifier` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/swarmauri_middleware_jwksverifier/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_middleware_jwksverifier` provides jWKS-based JWT verification middleware for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_middleware_jwksverifier`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/swarmauri_middleware_jwksverifier/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_middleware_jwksverifier` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/swarmauri_middleware_jwksverifier/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml) provide the supporting context for `swarmauri_middleware_jwksverifier`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_middleware_jwksverifier](https://pypi.org/project/swarmauri_middleware_jwksverifier/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_middleware_jwksverifier` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_middleware_jwksverifier` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_middleware_jwksverifier` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_middleware_jwksverifier` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_middleware_jwksverifier` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwksverifier/NOTICE) for attribution.
<!-- readme-standards:end notices -->
