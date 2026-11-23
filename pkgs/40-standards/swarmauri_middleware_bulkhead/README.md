# swarmauri_middleware_bulkhead

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_middleware_bulkhead</strong></p>
<p align="center">Bulkhead middleware implementation for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_bulkhead/"><img alt="pypi: swarmauri_middleware_bulkhead" src="https://img.shields.io/pypi/v/swarmauri_middleware_bulkhead"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_bulkhead/"><img alt="Monthly PyPI downloads: swarmauri_middleware_bulkhead" src="https://img.shields.io/pypi/dm/swarmauri_middleware_bulkhead"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/README.md"><img alt="README hits: swarmauri_middleware_bulkhead" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_middleware_bulkhead/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Concurrency isolation middleware for Starlette applications. Limit the number of simultaneous requests to protect resources from overload and ensure reliable service operation.

### Why This Package

`swarmauri_middleware_bulkhead` isolates this responsibility: Bulkhead middleware implementation for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/swarmauri_middleware_bulkhead/__init__.py) exposes `BulkheadMiddleware`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_middleware_bulkhead` when your integration needs bulkhead middleware implementation for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Concurrency control** restricts the number of in-flight requests using an `asyncio.Semaphore`.
- **Configurable limits** let you tune `max_concurrency` (default: 10) to match service capacity.
- **Fail-fast validation** guards against non-positive concurrency limits at initialization.
- **Structured logging** surfaces request flow and failure details for easier diagnostics.
- **ASGI integration** lets Starlette applications apply the concurrency limit to incoming requests.

### Non-Goals

`swarmauri_middleware_bulkhead` owns bulkhead middleware implementation for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml) declares runtime dependencies including `starlette`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_middleware_bulkhead

# Poetry
poetry add swarmauri_middleware_bulkhead

# uv
uv add swarmauri_middleware_bulkhead
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_middleware_bulkhead
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_middleware_bulkhead
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_middleware_bulkhead
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

The middleware wraps a `call_next` handler and ensures that no more than `max_concurrency` requests execute at once. Run the example below with `python quickstart.py` to see the concurrency ceiling in action.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/docs/readme/quick_start.py).

```python
import asyncio

from starlette.requests import Request

from swarmauri_middleware_bulkhead import BulkheadMiddleware


async def main() -> None:
    bulkhead = BulkheadMiddleware(max_concurrency=2)
    active_requests = 0
    peak_active_requests = 0
    lock = asyncio.Lock()

    async def call_next(request: Request):
        nonlocal active_requests, peak_active_requests
        async with lock:
            active_requests += 1
            peak_active_requests = max(peak_active_requests, active_requests)

        try:
            await asyncio.sleep(0.05)
            return {"path": request.scope.get("path"), "handled": True}
        finally:
            async with lock:
                active_requests -= 1

    async def simulate_request(idx: int):
        request = Request(scope={"type": "http", "path": f"/task/{idx}"})
        return await bulkhead.dispatch(request, call_next)

    responses = await asyncio.gather(*(simulate_request(i) for i in range(5)))

    assert peak_active_requests <= bulkhead.max_concurrency
    print("Peak concurrent requests:", peak_active_requests)
    print("Responses:", responses)


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_middleware_bulkhead` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/docs/readme/usage.py).

```python
import asyncio

from starlette.requests import Request

from swarmauri_middleware_bulkhead import BulkheadMiddleware


async def main() -> None:
    bulkhead = BulkheadMiddleware(max_concurrency=2)
    active_requests = 0
    peak_active_requests = 0
    lock = asyncio.Lock()

    async def call_next(request: Request):
        nonlocal active_requests, peak_active_requests
        async with lock:
            active_requests += 1
            peak_active_requests = max(peak_active_requests, active_requests)

        try:
            await asyncio.sleep(0.05)
            return {"path": request.scope.get("path"), "handled": True}
        finally:
            async with lock:
                active_requests -= 1

    async def simulate_request(idx: int):
        request = Request(scope={"type": "http", "path": f"/task/{idx}"})
        return await bulkhead.dispatch(request, call_next)

    responses = await asyncio.gather(*(simulate_request(i) for i in range(5)))

    assert peak_active_requests <= bulkhead.max_concurrency
    print("Peak concurrent requests:", peak_active_requests)
    print("Responses:", responses)


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_middleware_bulkhead` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/swarmauri_middleware_bulkhead/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_middleware_bulkhead` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_middleware_bulkhead` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `BulkheadMiddleware`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_middleware_bulkhead` is located in `standards` and owns bulkhead middleware implementation for Swarmauri. Source-declared APIs include `BulkheadMiddleware`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_middleware_bulkhead`.

Source-declared exports or types: `BulkheadMiddleware`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/swarmauri_middleware_bulkhead/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.middlewares` → `BulkheadMiddleware` → `swarmauri_middleware_bulkhead:BulkheadMiddleware`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_middleware_bulkhead` are `starlette`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/swarmauri_middleware_bulkhead/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_middleware_bulkhead` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_middleware_bulkhead`, use the source-declared public interfaces (`BulkheadMiddleware`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_middleware_bulkhead` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_middleware_bulkhead`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/swarmauri_middleware_bulkhead/__init__.py). The `swarmauri_middleware_bulkhead` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_middleware_bulkhead` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_middleware_bulkhead` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/tests/example/test_readme_example.py)
- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_BulkheadMiddleware.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/tests/unit/test_BulkheadMiddleware.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_middleware_bulkhead` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/swarmauri_middleware_bulkhead/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_middleware_bulkhead` provides bulkhead middleware implementation for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_middleware_bulkhead`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/swarmauri_middleware_bulkhead/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_middleware_bulkhead` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/swarmauri_middleware_bulkhead/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml) provide the supporting context for `swarmauri_middleware_bulkhead`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_middleware_bulkhead](https://pypi.org/project/swarmauri_middleware_bulkhead/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_middleware_bulkhead` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_middleware_bulkhead` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_middleware_bulkhead` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_middleware_bulkhead` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_middleware_bulkhead` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_bulkhead/NOTICE) for attribution.
<!-- readme-standards:end notices -->
