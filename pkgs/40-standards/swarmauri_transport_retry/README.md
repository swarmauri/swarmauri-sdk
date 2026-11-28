# swarmauri_transport_retry

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_transport_retry</strong></p>
<p align="center">Policy-driven synchronous, asynchronous, and streaming HTTP retries for Swarmauri clients.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_transport_retry/"><img alt="pypi: swarmauri_transport_retry" src="https://img.shields.io/pypi/v/swarmauri_transport_retry?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_transport_retry/"><img alt="Monthly PyPI downloads: swarmauri_transport_retry" src="https://img.shields.io/pypi/dm/swarmauri_transport_retry?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/README.md"><img alt="README hits: swarmauri_transport_retry" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_transport_retry/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

[![PyPI version](https://img.shields.io/pypi/v/swarmauri_transport_retry.svg)](https://pypi.org/project/swarmauri_transport_retry/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_transport_retry.svg)](https://pypi.org/project/swarmauri_transport_retry/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_transport_retry)](https://pepy.tech/project/swarmauri_transport_retry) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg?path=pkgs%2Fstandards%2Fswarmauri_transport_retry)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

Policy-driven retries for any client implementing Swarmauri's `IHttpClient` contract.

### Why This Package

`swarmauri_transport_retry` isolates this responsibility: Policy-driven synchronous, asynchronous, and streaming HTTP retries for Swarmauri clients. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/swarmauri_transport_retry/ExponentialBackoffRetryPolicy.py) exposes `ExponentialBackoffRetryPolicy`, `RetryingHttpClient`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_transport_retry` when your integration needs policy-driven synchronous, asynchronous, and streaming HTTP retries for Swarmauri clients. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Bounded exponential backoff with optional jitter.
- `Retry-After` support for seconds and HTTP dates.
- Separate policy decisions from sync, async, and streaming execution.
- Protect non-idempotent methods from replay by default.
- Wrap any Swarmauri HTTP client without depending on its HTTP library.

### Non-Goals

`swarmauri_transport_retry` owns policy-driven synchronous, asynchronous, and streaming HTTP retries for Swarmauri clients. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml) declares runtime dependencies including `swarmauri-core`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_transport_retry
```

```bash
pip install swarmauri_transport_retry
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_transport_retry
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_transport_retry
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_transport_retry
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/docs/readme/quick_start.py).

```python
from swarmauri_transport_httpx import HttpxClient
from swarmauri_transport_retry import (
    ExponentialBackoffRetryPolicy,
    RetryingHttpClient,
)

client = RetryingHttpClient(
    client=HttpxClient(base_url="https://api.example.com"),
    policy=ExponentialBackoffRetryPolicy(max_attempts=3),
)
response = client.request("GET", "/models")
response.raise_for_status()
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_transport_retry` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/docs/readme/usage.py).

```python
from swarmauri_transport_httpx import HttpxClient
from swarmauri_transport_retry import (
    ExponentialBackoffRetryPolicy,
    RetryingHttpClient,
)

client = RetryingHttpClient(
    client=HttpxClient(base_url="https://api.example.com"),
    policy=ExponentialBackoffRetryPolicy(max_attempts=3),
)
response = client.request("GET", "/models")
response.raise_for_status()
```
<!-- readme-standards:end example.usage -->

The retry policy controls replay safety and delay. The wrapped transport remains responsible for moving HTTP requests and responses.

### Configuration

Configure `swarmauri_transport_retry` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/swarmauri_transport_retry/ExponentialBackoffRetryPolicy.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_transport_retry` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_transport_retry` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ExponentialBackoffRetryPolicy`, `RetryingHttpClient`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_transport_retry` is located in `standards` and owns policy-driven synchronous, asynchronous, and streaming HTTP retries for Swarmauri clients. Source-declared APIs include `ExponentialBackoffRetryPolicy`, `RetryingHttpClient`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_transport_retry`.

Source-declared exports or types: `ExponentialBackoffRetryPolicy`, `RetryingHttpClient`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/swarmauri_transport_retry/ExponentialBackoffRetryPolicy.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.transports` → `RetryingHttpClient` → `swarmauri_transport_retry:RetryingHttpClient`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_transport_retry` are `swarmauri-core`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/swarmauri_transport_retry/ExponentialBackoffRetryPolicy.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_llm_azureopenai`, `swarmauri_llm_cloudflare`, `swarmauri_llm_nvidia_nim`, `swarmauri_llm_openrouter`, `swarmauri_llm_xai`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_transport_retry`, use the source-declared public interfaces (`ExponentialBackoffRetryPolicy`, `RetryingHttpClient`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_transport_retry` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_transport_retry`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/swarmauri_transport_retry/ExponentialBackoffRetryPolicy.py). The `swarmauri_transport_retry` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_transport_retry` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_transport_retry` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_retrying_http_client.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/tests/unit/test_retrying_http_client.py)
- [tests/unit/test_retry_policy.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/tests/unit/test_retry_policy.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_transport_retry` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/swarmauri_transport_retry/ExponentialBackoffRetryPolicy.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_transport_retry` provides policy-driven synchronous, asynchronous, and streaming HTTP retries for Swarmauri clients; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_transport_retry`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/swarmauri_transport_retry/ExponentialBackoffRetryPolicy.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_transport_retry` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/swarmauri_transport_retry/ExponentialBackoffRetryPolicy.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml) provide the supporting context for `swarmauri_transport_retry`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_transport_retry](https://pypi.org/project/swarmauri_transport_retry/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_transport_retry`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_transport_retry` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_transport_retry` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_transport_retry` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_transport_retry` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_transport_retry` source version is `0.1.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/NOTICE) for attribution.
<!-- readme-standards:end notices -->
