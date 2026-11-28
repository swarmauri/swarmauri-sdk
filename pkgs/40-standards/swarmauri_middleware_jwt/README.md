# swarmauri_middleware_jwt

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_middleware_jwt</strong></p>
<p align="center">ASGI Bearer JWT authentication middleware for Swarmauri applications.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_jwt/"><img alt="pypi: swarmauri_middleware_jwt" src="https://img.shields.io/pypi/v/swarmauri_middleware_jwt?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_jwt/"><img alt="Monthly PyPI downloads: swarmauri_middleware_jwt" src="https://img.shields.io/pypi/dm/swarmauri_middleware_jwt?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/README.md"><img alt="README hits: swarmauri_middleware_jwt" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_middleware_jwt/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_middleware_jwt` is the ASGI adapter for authenticating compact JWT
Bearer credentials. It delegates JWS verification to `swarmauri_signing_jws`
and framework-neutral claim policy to `swarmauri_tokens_jwt`.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_middleware_jwt)](https://pepy.tech/projects/swarmauri_middleware_jwt)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_middleware_jwt.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_middleware_jwt/)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_middleware_jwt/)
[![License](https://img.shields.io/pypi/l/swarmauri_middleware_jwt)](https://pypi.org/project/swarmauri_middleware_jwt/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_middleware_jwt)](https://pypi.org/project/swarmauri_middleware_jwt/)

### Why This Package

`swarmauri_middleware_jwt` isolates this responsibility: ASGI Bearer JWT authentication middleware for Swarmauri applications. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/swarmauri_middleware_jwt/BearerTokenExtractor.py) exposes `BearerTokenError`, `BearerTokenExtractor`, `JWTMiddleware`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_middleware_jwt` when your integration needs aSGI Bearer JWT authentication middleware for Swarmauri applications. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Extracts RFC 6750-style Bearer credentials without coupling extraction to
  token semantics.
- Verifies compact HMAC JWS signatures with an explicit algorithm allowlist.
- Applies reusable JWT policy for temporal, issuer, audience, required-claim,
  scope, and role validation.
- Stores authenticated claims on a configurable request-state attribute.
- Supports synchronous manual verification and asynchronous middleware flows.
- Uses Starlette request and exception contracts and works with FastAPI.

### Non-Goals

`swarmauri_middleware_jwt` owns aSGI Bearer JWT authentication middleware for Swarmauri applications. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml) declares runtime dependencies including `starlette`, `swarmauri-core`, `swarmauri-base`, `swarmauri-signing-jws`, `swarmauri-tokens-jwt`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_middleware_jwt
```

```bash
pip install swarmauri_middleware_jwt
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_middleware_jwt
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_middleware_jwt
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_middleware_jwt
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/docs/readme/quick_start.py).

```python
import asyncio
import time

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_middleware_jwt import JWTMiddleware
from swarmauri_signing_jws import JwsSignerVerifier

SECRET = "replace-with-at-least-32-secret-bytes"


async def protected(request: Request) -> JSONResponse:
    return JSONResponse({"subject": request.state.jwt_payload["sub"]})


routes = Starlette(routes=[Route("/protected", protected)])
jwt_middleware = JWTMiddleware(
    secret_key=SECRET,
    app=routes,
    issuer="https://identity.example.com",
    audience="swarmauri-api",
    required_claims={"sub", "iat", "exp"},
)
app = jwt_middleware


async def issue_example_token() -> str:
    now = int(time.time())
    return await JwsSignerVerifier().sign_compact(
        payload={
            "sub": "demo-user",
            "iat": now,
            "exp": now + 300,
            "iss": "https://identity.example.com",
            "aud": "swarmauri-api",
        },
        alg=JWAAlg.HS256,
        key={"kind": "raw", "key": SECRET, "alg": "HS256"},
        typ="JWT",
    )


token = asyncio.run(issue_example_token())
assert jwt_middleware.verify_token(token)["sub"] == "demo-user"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_middleware_jwt` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/docs/readme/usage.py).

```python
import asyncio
import time

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_middleware_jwt import JWTMiddleware
from swarmauri_signing_jws import JwsSignerVerifier

SECRET = "replace-with-at-least-32-secret-bytes"


async def protected(request: Request) -> JSONResponse:
    return JSONResponse({"subject": request.state.jwt_payload["sub"]})


routes = Starlette(routes=[Route("/protected", protected)])
jwt_middleware = JWTMiddleware(
    secret_key=SECRET,
    app=routes,
    issuer="https://identity.example.com",
    audience="swarmauri-api",
    required_claims={"sub", "iat", "exp"},
)
app = jwt_middleware


async def issue_example_token() -> str:
    now = int(time.time())
    return await JwsSignerVerifier().sign_compact(
        payload={
            "sub": "demo-user",
            "iat": now,
            "exp": now + 300,
            "iss": "https://identity.example.com",
            "aud": "swarmauri-api",
        },
        alg=JWAAlg.HS256,
        key={"kind": "raw", "key": SECRET, "alg": "HS256"},
        typ="JWT",
    )


token = asyncio.run(issue_example_token())
assert jwt_middleware.verify_token(token)["sub"] == "demo-user"
```
<!-- readme-standards:end example.usage -->

For asymmetric keys or managed key providers, use
`swarmauri_tokens_jwt.JWTTokenService` and pass an appropriate verifier into
your application boundary.

### Configuration

Configure `swarmauri_middleware_jwt` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/swarmauri_middleware_jwt/BearerTokenExtractor.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_middleware_jwt` source raises `BearerTokenError`, `HTTPException`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_middleware_jwt` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `BearerTokenError`, `BearerTokenExtractor`, `JWTMiddleware`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_middleware_jwt` is located in `standards` and owns aSGI Bearer JWT authentication middleware for Swarmauri applications. Source-declared APIs include `BearerTokenError`, `BearerTokenExtractor`, `JWTMiddleware`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_middleware_jwt`.

Source-declared exports or types: `BearerTokenError`, `BearerTokenExtractor`, `JWTMiddleware`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/swarmauri_middleware_jwt/BearerTokenExtractor.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.middlewares` → `JWTMiddleware` → `swarmauri_middleware_jwt:JWTMiddleware`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_middleware_jwt` are `starlette`, `swarmauri-core`, `swarmauri-base`, `swarmauri-signing-jws`, `swarmauri-tokens-jwt`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/swarmauri_middleware_jwt/BearerTokenExtractor.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_middleware_jwt` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_middleware_jwt`, use the source-declared public interfaces (`BearerTokenError`, `BearerTokenExtractor`, `JWTMiddleware`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_middleware_jwt` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_middleware_jwt`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/swarmauri_middleware_jwt/BearerTokenExtractor.py). The `swarmauri_middleware_jwt` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_middleware_jwt` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_middleware_jwt` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/tests/test_readme_example.py)
- [tests/unit/test_JWTMiddleware.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/tests/unit/test_JWTMiddleware.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_middleware_jwt` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/swarmauri_middleware_jwt/BearerTokenExtractor.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_middleware_jwt` provides aSGI Bearer JWT authentication middleware for Swarmauri applications; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_middleware_jwt`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/swarmauri_middleware_jwt/BearerTokenExtractor.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_middleware_jwt` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/swarmauri_middleware_jwt/BearerTokenExtractor.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml) provide the supporting context for `swarmauri_middleware_jwt`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_signing_jws](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/README.md): Composite JWS signer/verifier for Swarmauri
- [swarmauri_tokens_jwt](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/README.md): JWT token service for Swarmauri

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_middleware_jwt](https://pypi.org/project/swarmauri_middleware_jwt/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

See the repository [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).

### Development Setup

Work from the `pkgs/40-standards/swarmauri_middleware_jwt` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_middleware_jwt` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_middleware_jwt` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_middleware_jwt` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_middleware_jwt` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jwt/NOTICE) for attribution.
<!-- readme-standards:end notices -->
