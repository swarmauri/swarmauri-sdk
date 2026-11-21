# swarmauri_middleware_ratelimit

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_middleware_ratelimit</strong></p>
<p align="center">Rate limiting middleware for Swarmauri applications</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_ratelimit/"><img alt="pypi: swarmauri_middleware_ratelimit" src="https://img.shields.io/pypi/v/swarmauri_middleware_ratelimit"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_ratelimit/"><img alt="Monthly PyPI downloads: swarmauri_middleware_ratelimit" src="https://img.shields.io/pypi/dm/swarmauri_middleware_ratelimit"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/README.md"><img alt="README hits: swarmauri_middleware_ratelimit" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_middleware_ratelimit/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Flexible rate limiting middleware for Swarmauri applications.

This package provides a drop-in Starlette middleware that throttles requests
based on the client IP address or an authentication token. It is useful for
preventing abuse of public APIs or protecting upstream services from bursts of
traffic.

### Why This Package

`swarmauri_middleware_ratelimit` isolates this responsibility: Rate limiting middleware for Swarmauri applications. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/swarmauri_middleware_ratelimit/__init__.py) exposes `RateLimitMiddleware`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_middleware_ratelimit` when your integration needs rate limiting middleware for Swarmauri applications. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Configurable request limit and time window that defaults to ``100`` requests
  per ``60`` seconds.
- Tracks callers by IP address or a custom authentication token header.
- Maintains in-memory counters that reset automatically after the configured
  time window.
- Returns Starlette ``Response`` objects with HTTP ``429`` status codes when the
  limit is exceeded.

### Non-Goals

`swarmauri_middleware_ratelimit` owns rate limiting middleware for Swarmauri applications. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `starlette`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_middleware_ratelimit

# Poetry
poetry add swarmauri_middleware_ratelimit

# uv
uv add swarmauri_middleware_ratelimit
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_middleware_ratelimit
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_middleware_ratelimit
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_middleware_ratelimit
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/docs/readme/quick_start.py).

```python
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from swarmauri_middleware_ratelimit import RateLimitMiddleware

app = Starlette()
rate_limiter = RateLimitMiddleware(rate_limit=2, time_window=60)


async def limit_requests(request, call_next):
    return await rate_limiter.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=limit_requests)

async def ping(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/ping", ping)

async def ping(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/ping", ping)

client = TestClient(app)

assert client.get("/ping").status_code == 200
assert client.get("/ping").status_code == 200
assert client.get("/ping").status_code == 429
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_middleware_ratelimit` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/docs/readme/usage.py).

```python
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from swarmauri_middleware_ratelimit import RateLimitMiddleware

app = Starlette()
rate_limiter = RateLimitMiddleware(rate_limit=2, time_window=60)


async def limit_requests(request, call_next):
    return await rate_limiter.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=limit_requests)


async def ping(_request):
    return JSONResponse({"status": "ok"})


app.add_route("/ping", ping)

client = TestClient(app)

assert client.get("/ping").status_code == 200
assert client.get("/ping").status_code == 200
assert client.get("/ping").status_code == 429
```
<!-- readme-standards:end example.usage -->

**Basic IP-based limiting**


In this example the first two requests succeed because they fall inside the
allowed limit. A third request within the same 60-second window exceeds the
threshold and the middleware immediately returns a ``429`` response with the
body ``"Rate limit exceeded"``. The middleware instance keeps request counters
in memory, so you should create one instance per application process.

**Token-based rate limiting**

```python
# Use the value of the `X-Api-Key` header to track clients instead of IP
rate_limiter = RateLimitMiddleware(
    rate_limit=100,
    time_window=60,
    use_token=True,
    token_header="X-Api-Key",
)


async def limit_requests(request, call_next):
    return await rate_limiter.dispatch(request, call_next)


app.add_middleware(BaseHTTPMiddleware, dispatch=limit_requests)
```

When ``use_token`` is ``True`` the middleware looks for the configured header on
every request and raises a ``ValueError`` if it is missing. This makes it safe
to enforce API key or bearer token quotas even when requests are routed through
shared proxies. Reuse the same middleware instance across requests to ensure
counters continue to accumulate across calls.

### Configuration

Configure `swarmauri_middleware_ratelimit` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/swarmauri_middleware_ratelimit/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_middleware_ratelimit` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_middleware_ratelimit` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `RateLimitMiddleware`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_middleware_ratelimit` is located in `standards` and owns rate limiting middleware for Swarmauri applications. Source-declared APIs include `RateLimitMiddleware`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_middleware_ratelimit`.

Source-declared exports or types: `RateLimitMiddleware`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/swarmauri_middleware_ratelimit/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.middlewares` → `RateLimitMiddleware` → `swarmauri_middleware_ratelimit:RateLimitMiddleware`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_middleware_ratelimit` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `starlette`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/swarmauri_middleware_ratelimit/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_middleware_ratelimit` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_middleware_ratelimit`, use the source-declared public interfaces (`RateLimitMiddleware`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_middleware_ratelimit` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_middleware_ratelimit`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/swarmauri_middleware_ratelimit/__init__.py). The `swarmauri_middleware_ratelimit` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_middleware_ratelimit` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_middleware_ratelimit` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/tests/example/test_readme_example.py)
- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_RateLimitMiddleware.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/tests/unit/test_RateLimitMiddleware.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_middleware_ratelimit` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/swarmauri_middleware_ratelimit/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_middleware_ratelimit` provides rate limiting middleware for Swarmauri applications; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_middleware_ratelimit`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/swarmauri_middleware_ratelimit/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_middleware_ratelimit` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/swarmauri_middleware_ratelimit/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml) provide the supporting context for `swarmauri_middleware_ratelimit`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_middleware_ratelimit](https://pypi.org/project/swarmauri_middleware_ratelimit/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_middleware_ratelimit` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_middleware_ratelimit` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_middleware_ratelimit` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_middleware_ratelimit` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_middleware_ratelimit` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_middleware_ratelimit/NOTICE) for attribution.
<!-- readme-standards:end notices -->
