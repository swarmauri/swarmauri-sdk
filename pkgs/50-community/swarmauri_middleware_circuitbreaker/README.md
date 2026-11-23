# swarmauri_middleware_circuitbreaker

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_middleware_circuitbreaker</strong></p>
<p align="center">Async circuit-breaker middleware for Swarmauri and Starlette request flows backed by pybreaker.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/"><img alt="pypi: swarmauri_middleware_circuitbreaker" src="https://img.shields.io/pypi/v/swarmauri_middleware_circuitbreaker?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/"><img alt="Monthly PyPI downloads: swarmauri_middleware_circuitbreaker" src="https://img.shields.io/pypi/dm/swarmauri_middleware_circuitbreaker?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/README.md"><img alt="README hits: swarmauri_middleware_circuitbreaker" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_middleware_circuitbreaker/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_middleware_circuitbreaker` is the Swarmauri middleware component for
protecting unstable request paths with a circuit-breaker policy backed by
`pybreaker`. It is designed for Starlette request middleware and prevents
repeated failures from repeatedly hitting unhealthy downstream services.

### Why This Package

- Stop sending traffic to failing upstream dependencies after repeated errors.
- Recover gradually by allowing a single half-open probe request before fully
  reopening traffic.
- Add resilience controls to Swarmauri or Starlette request flows without writing
  custom breaker logic.
- Pair with retry and observability middleware to build layered failure
  protection.

### When to Use

Choose `swarmauri_middleware_circuitbreaker` when your integration needs async circuit-breaker middleware for Swarmauri and Starlette request flows backed by pybreaker. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Circuit-breaker protection using `pybreaker`.
- Async `dispatch(request, call_next)` middleware surface.
- Configurable failure threshold and reset timing.
- Logging for open, half-open, and closed transitions.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_middleware_circuitbreaker` owns async circuit-breaker middleware for Swarmauri and Starlette request flows backed by pybreaker. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/pyproject.toml) declares runtime dependencies including `starlette`, `pybreaker`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_middleware_circuitbreaker
```

```bash
pip install swarmauri_middleware_circuitbreaker
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_middleware_circuitbreaker
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_middleware_circuitbreaker
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_middleware_circuitbreaker
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/docs/readme/quick_start.py).

```python
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from swarmauri_middleware_circuitbreaker import CircuitBreakerMiddleware

app = Starlette()
breaker = CircuitBreakerMiddleware(
    fail_max=5,
    reset_timeout=30,
    half_open_wait_time=10,
)


async def check_circuit(request, call_next):
    try:
        return await breaker.dispatch(request, call_next)
    except HTTPException as exc:
        return JSONResponse(
            {"detail": exc.detail},
            status_code=exc.status_code,
            headers=exc.headers,
        )


app.add_middleware(BaseHTTPMiddleware, dispatch=check_circuit)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_middleware_circuitbreaker` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/docs/readme/usage.py).

```python
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from swarmauri_middleware_circuitbreaker import CircuitBreakerMiddleware

app = Starlette()
breaker = CircuitBreakerMiddleware(
    fail_max=5,
    reset_timeout=30,
    half_open_wait_time=10,
)


async def check_circuit(request, call_next):
    try:
        return await breaker.dispatch(request, call_next)
    except HTTPException as exc:
        return JSONResponse(
            {"detail": exc.detail},
            status_code=exc.status_code,
            headers=exc.headers,
        )


app.add_middleware(BaseHTTPMiddleware, dispatch=check_circuit)
```
<!-- readme-standards:end example.usage -->

**Protect an unstable endpoint**

Add this route to the app above before serving requests.

```python
async def unstable(_request):
    raise RuntimeError("Simulated failure")


app.add_route("/unstable", unstable)
```

**Observe circuit transitions in logs**

```python
import logging

logging.basicConfig(level=logging.INFO)

# Expected messages include:
# "Circuit half-open: Waiting for test request to determine health"
# "Circuit opened: Excessive failures detected"
# "Circuit closed: Service is healthy again"
```

**Understand open and recovery flow**

```python
# Repeated failures increment the internal counter.
# Once the threshold is exceeded, the circuit opens.
# A later request is allowed as a half-open probe.
# Success closes the circuit; failure reopens protection.
```

### Configuration

Configure `swarmauri_middleware_circuitbreaker` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/swarmauri_middleware_circuitbreaker/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_middleware_circuitbreaker` source raises `HTTPException`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use targeted circuit breakers around unstable upstream dependencies rather
  than globally around every route.
- Tune `fail_max` and `reset_timeout` per dependency instead of reusing one
  threshold everywhere.
- Pair circuit breaking with retries carefully so one layer does not amplify
  the other.
- Verify your monitoring captures circuit state changes before relying on the
  breaker in production.

---

## Package Boundary

### What It Owns

`swarmauri_middleware_circuitbreaker` is located in `community` and owns async circuit-breaker middleware for Swarmauri and Starlette request flows backed by pybreaker. Source-declared APIs include `CircuitBreakerMiddleware`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_middleware_circuitbreaker`.

Source-declared exports or types: `CircuitBreakerMiddleware`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/swarmauri_middleware_circuitbreaker/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.middlewares` → `CircuitBreakerMiddleware` → `swarmauri_middleware_circuitbreaker:CircuitBreakerMiddleware`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_middleware_circuitbreaker` are `starlette`, `pybreaker`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/swarmauri_middleware_circuitbreaker/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_middleware_circuitbreaker` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_middleware_circuitbreaker`, use the source-declared public interfaces (`CircuitBreakerMiddleware`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_middleware_circuitbreaker` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_middleware_circuitbreaker`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/swarmauri_middleware_circuitbreaker/__init__.py). The `swarmauri_middleware_circuitbreaker` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_middleware_circuitbreaker` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_middleware_circuitbreaker` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_CircuitBreakerMiddleware.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/tests/unit/test_CircuitBreakerMiddleware.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_middleware_circuitbreaker` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/swarmauri_middleware_circuitbreaker/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What parameters does this middleware expose?**
> `fail_max`, `reset_timeout`, and `half_open_wait_time`.

> **What happens when the circuit is open?**
> The middleware raises HTTP 429 for additional requests until a half-open probe
> is allowed.

> **Is this middleware async?**
> Yes. The main `dispatch(request, call_next)` entry point is asynchronous.

> **What request type does it expect?**
> It is written for `starlette.requests.Request`.

### Why

**Why select this package?** `swarmauri_middleware_circuitbreaker` provides async circuit-breaker middleware for Swarmauri and Starlette request flows backed by pybreaker; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_middleware_circuitbreaker`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/swarmauri_middleware_circuitbreaker/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_middleware_circuitbreaker` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Starlette middleware docs](https://www.starlette.dev/middleware/)
- [pybreaker package information](https://pypi.org/project/pybreaker/)

### Related Packages

- [swarmauri_middleware_ratepolicy](https://pypi.org/project/swarmauri_middleware_ratepolicy/)
- [swarmauri_state_clipboard](https://pypi.org/project/swarmauri_state_clipboard/)
- [swarmauri_middleware_circuitbreaker](https://pypi.org/project/swarmauri_middleware_circuitbreaker/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_middleware_circuitbreaker](https://pypi.org/project/swarmauri_middleware_circuitbreaker/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_middleware_circuitbreaker`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_middleware_circuitbreaker` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_middleware_circuitbreaker` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_middleware_circuitbreaker` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_middleware_circuitbreaker` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_middleware_circuitbreaker/NOTICE) for attribution.
<!-- readme-standards:end notices -->
