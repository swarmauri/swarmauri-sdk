# swarmauri_middleware_jsonrpc

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_middleware_jsonrpc</strong></p>
<p align="center">Middleware for validating basic JSON-RPC requests</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/"><img alt="pypi: swarmauri_middleware_jsonrpc" src="https://img.shields.io/pypi/v/swarmauri_middleware_jsonrpc?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/"><img alt="Monthly PyPI downloads: swarmauri_middleware_jsonrpc" src="https://img.shields.io/pypi/dm/swarmauri_middleware_jsonrpc?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/README.md"><img alt="README hits: swarmauri_middleware_jsonrpc" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_middleware_jsonrpc/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Middleware that performs simple validation of JSON-RPC requests.

### Why This Package

`swarmauri_middleware_jsonrpc` isolates this responsibility: Middleware for validating basic JSON-RPC requests. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py) exposes `JsonRpcMiddleware`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_middleware_jsonrpc` when your integration needs middleware for validating basic JSON-RPC requests. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Validates JSON request bodies for JSON-RPC payloads when the
  `Content-Type` header starts with `application/json`.
- Returns `400 Bad Request` with a plain-text error when the body contains
  invalid JSON.
- Ensures JSON object payloads define a `jsonrpc` field, responding with
  `400 Bad Request` if it is missing.

### Non-Goals

`swarmauri_middleware_jsonrpc` owns middleware for validating basic JSON-RPC requests. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml) declares runtime dependencies including `starlette`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

Install the middleware with your preferred Python packaging workflow:

```bash
pip install swarmauri_middleware_jsonrpc
```

```bash
poetry add swarmauri_middleware_jsonrpc
```

```bash
uv add swarmauri_middleware_jsonrpc
```

```bash
uv pip install swarmauri_middleware_jsonrpc
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_middleware_jsonrpc
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_middleware_jsonrpc
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_middleware_jsonrpc
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/docs/readme/quick_start.py).

```python
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from swarmauri_middleware_jsonrpc import JsonRpcMiddleware

app = Starlette()
app.add_middleware(BaseHTTPMiddleware, dispatch=JsonRpcMiddleware().dispatch)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_middleware_jsonrpc` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/docs/readme/usage.py).

```python
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from swarmauri_middleware_jsonrpc import JsonRpcMiddleware

app = Starlette()
app.add_middleware(BaseHTTPMiddleware, dispatch=JsonRpcMiddleware().dispatch)
```
<!-- readme-standards:end example.usage -->

The middleware uses Starlette’s `BaseHTTPMiddleware` and is
compatible with the `MiddlewareBase` ecosystem.  Once registered, every incoming
JSON request is validated before reaching subsequent middleware or route
handlers.

### Configuration

Configure `swarmauri_middleware_jsonrpc` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_middleware_jsonrpc` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py).

### Best Practices

Use the explicit `swarmauri_middleware_jsonrpc` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `JsonRpcMiddleware`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_middleware_jsonrpc` is located in `standards` and owns middleware for validating basic JSON-RPC requests. Source-declared APIs include `JsonRpcMiddleware`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_middleware_jsonrpc`.

Source-declared exports or types: `JsonRpcMiddleware`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.middlewares` → `JsonRpcMiddleware` → `swarmauri_middleware_jsonrpc:JsonRpcMiddleware`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_middleware_jsonrpc` are `starlette`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_middleware_jsonrpc` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_middleware_jsonrpc`, use the source-declared public interfaces (`JsonRpcMiddleware`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_middleware_jsonrpc` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_middleware_jsonrpc`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py). The `swarmauri_middleware_jsonrpc` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_middleware_jsonrpc` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_middleware_jsonrpc` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/tests/test_readme_example.py)
- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/tests/i9n/test_i9n__init__.py)
- [tests/i9n/test_starlette_integration.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/tests/i9n/test_starlette_integration.py)
- [tests/unit/test_JsonRpcMiddleware.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/tests/unit/test_JsonRpcMiddleware.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_middleware_jsonrpc` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_middleware_jsonrpc` provides middleware for validating basic JSON-RPC requests; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_middleware_jsonrpc`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_middleware_jsonrpc` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/swarmauri_middleware_jsonrpc/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml) provide the supporting context for `swarmauri_middleware_jsonrpc`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_middleware_jsonrpc](https://pypi.org/project/swarmauri_middleware_jsonrpc/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_middleware_jsonrpc` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Request Validation**

- Requests without an `application/json` content type bypass the middleware.
- Malformed JSON bodies are rejected with a `400` response containing the
  message `Invalid JSON`.
- JSON objects missing the `jsonrpc` key are rejected with a `400` response and
  the message `Missing jsonrpc field`.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_middleware_jsonrpc` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_middleware_jsonrpc` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_middleware_jsonrpc` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_jsonrpc/NOTICE) for attribution.
<!-- readme-standards:end notices -->
