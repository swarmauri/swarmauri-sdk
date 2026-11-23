# swarmauri_tokens_introspection

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tokens_introspection</strong></p>
<p align="center">OAuth 2.0 Token Introspection service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_introspection/"><img alt="pypi: swarmauri_tokens_introspection" src="https://img.shields.io/pypi/v/swarmauri_tokens_introspection"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_introspection/"><img alt="Monthly PyPI downloads: swarmauri_tokens_introspection" src="https://img.shields.io/pypi/dm/swarmauri_tokens_introspection"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/README.md"><img alt="README hits: swarmauri_tokens_introspection" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tokens_introspection/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

An OAuth 2.0 token introspection service plugin implementing RFC 7662 for verifying opaque access tokens.

### Why This Package

`swarmauri_tokens_introspection` isolates this responsibility: OAuth 2.0 Token Introspection service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/swarmauri_tokens_introspection/__init__.py) exposes `IntrospectionTokenService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tokens_introspection` when your integration needs oAuth 2.0 Token Introspection service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Asynchronous token verification against a remote introspection endpoint using `httpx`
- Supports `client_secret_basic`, `client_secret_post`, and bearer authentication schemes
- Caches positive and negative introspection results with configurable TTLs and expiry-aware caching
- Validates standard claims (`exp`, `nbf`, `iat`) with optional issuer and audience enforcement
- Optional JWKS passthrough for issuers that also publish signing keys via `jwks_url`
- Strictly verification-only: `mint()` raises `NotImplementedError` because opaque tokens are produced by the authorization server

### Non-Goals

`swarmauri_tokens_introspection` owns oAuth 2.0 Token Introspection service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the toolchain that matches your project:

```bash
pip install swarmauri_tokens_introspection
```

```bash
poetry add swarmauri_tokens_introspection
```

```bash
uv add swarmauri_tokens_introspection
```

The package exposes an async API, so ensure your environment includes an event loop (e.g., `asyncio`) when calling it.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tokens_introspection
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tokens_introspection
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tokens_introspection
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/docs/readme/quick_start.py).

```python
"""Execute the README example with `python README_example.py`."""

import asyncio

import httpx

from swarmauri_tokens_introspection import IntrospectionTokenService


async def main() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url == httpx.URL("https://auth.example.com/introspect")
        assert request.headers["Authorization"].startswith("Basic ")
        form = dict(httpx.QueryParams(request.content.decode()))
        assert form["token"] == "opaque-token"
        return httpx.Response(
            200,
            json={
                "active": True,
                "sub": "user-123",
                "scope": "profile email",
                "exp": 2_147_483_647,
            },
        )

    transport = httpx.MockTransport(handler)

    service = IntrospectionTokenService(
        "https://auth.example.com/introspect",
        client_id="id",
        client_secret="secret",
        cache_ttl_s=300,
    )

    # Exercise the provider with a mocked introspection response.
    service._client = httpx.AsyncClient(transport=transport)

    claims = await service.verify("opaque-token")
    print(claims["sub"])  # user-123

    await service.aclose()


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tokens_introspection` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/docs/readme/usage.py).

```python
"""Execute the README example with `python README_example.py`."""

import asyncio

import httpx

from swarmauri_tokens_introspection import IntrospectionTokenService


async def main() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url == httpx.URL("https://auth.example.com/introspect")
        assert request.headers["Authorization"].startswith("Basic ")
        form = dict(httpx.QueryParams(request.content.decode()))
        assert form["token"] == "opaque-token"
        return httpx.Response(
            200,
            json={
                "active": True,
                "sub": "user-123",
                "scope": "profile email",
                "exp": 2_147_483_647,
            },
        )

    transport = httpx.MockTransport(handler)

    service = IntrospectionTokenService(
        "https://auth.example.com/introspect",
        client_id="id",
        client_secret="secret",
        cache_ttl_s=300,
    )

    # Exercise the provider with a mocked introspection response.
    service._client = httpx.AsyncClient(transport=transport)

    claims = await service.verify("opaque-token")
    print(claims["sub"])  # user-123

    await service.aclose()


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The example below demonstrates how to exercise the service with a mocked introspection endpoint. The same API works against a live OAuth 2.0 Authorization Server?simply omit the mock transport and let `httpx` reach your configured `endpoint`.


**Caching and validation highlights**

- Positive responses respect both `cache_ttl_s` and the `exp` claim (including the configured leeway).
- Negative introspection results are cached for `negative_ttl_s` seconds to shield your AS from repeated invalid requests.
- Local validation enforces `exp`, `nbf`, and `iat` drift using `leeway_s`, and supports issuer/audience pinning.
- Configuring `jwks_url` enables `jwks()` passthrough for deployments that expose signing keys alongside introspection.

### Configuration

Configure `swarmauri_tokens_introspection` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/swarmauri_tokens_introspection/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tokens_introspection` source raises `ImportError`, `NotImplementedError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tokens_introspection` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `IntrospectionTokenService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tokens_introspection` is located in `standards` and owns oAuth 2.0 Token Introspection service for Swarmauri. Source-declared APIs include `IntrospectionTokenService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tokens_introspection`.

Source-declared exports or types: `IntrospectionTokenService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/swarmauri_tokens_introspection/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.tokens` → `introspection` → `swarmauri_tokens_introspection:IntrospectionTokenService`
- `swarmauri.tokens` → `IntrospectionTokenService` → `swarmauri_tokens_introspection:IntrospectionTokenService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tokens_introspection` are `swarmauri-core`, `swarmauri-base`, `httpx`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/swarmauri_tokens_introspection/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tokens_introspection` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tokens_introspection`, use the source-declared public interfaces (`IntrospectionTokenService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tokens_introspection` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tokens_introspection`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/swarmauri_tokens_introspection/__init__.py). The `swarmauri_tokens_introspection` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tokens_introspection` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tokens_introspection` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/tests/test_functional.py)
- [tests/test_performance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/tests/test_performance.py)
- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/tests/test_readme_example.py)
- [tests/test_rfc7662.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/tests/test_rfc7662.py)
- [tests/test_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/tests/test_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tokens_introspection` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/swarmauri_tokens_introspection/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tokens_introspection` provides oAuth 2.0 Token Introspection service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tokens_introspection`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/swarmauri_tokens_introspection/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tokens_introspection` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/swarmauri_tokens_introspection/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml) provide the supporting context for `swarmauri_tokens_introspection`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tokens_introspection](https://pypi.org/project/swarmauri_tokens_introspection/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tokens_introspection` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_tokens_introspection` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tokens_introspection` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tokens_introspection` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tokens_introspection` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/LICENSE).
<!-- readme-standards:end license -->

`Apache-2.0` ? Swarmauri

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_introspection/NOTICE) for attribution.
<!-- readme-standards:end notices -->
