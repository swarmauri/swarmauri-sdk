# swarmauri_certs_remote_ca

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_remote_ca</strong></p>
<p align="center">Remote CA certificate service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_remote_ca/"><img alt="pypi: swarmauri_certs_remote_ca" src="https://img.shields.io/pypi/v/swarmauri_certs_remote_ca?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_remote_ca/"><img alt="Monthly PyPI downloads: swarmauri_certs_remote_ca" src="https://img.shields.io/pypi/dm/swarmauri_certs_remote_ca?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/README.md"><img alt="README hits: swarmauri_certs_remote_ca" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_certs_remote_ca/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A certificate enrollment bridge implementing the `ICertService` interface and
forwarding CSRs to a remote Certificate Authority.

### Why This Package

`swarmauri_certs_remote_ca` isolates this responsibility: Remote CA certificate service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/swarmauri_certs_remote_ca/__init__.py) exposes `RemoteCaCertService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_certs_remote_ca` when your integration needs remote CA certificate service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Posts CSRs to a remote endpoint and returns issued certificates.
- Minimal parsing helpers for certificate snippets.
- Designed around X.509 as defined in RFC 5280 and Enrollment over Secure
  Transport (EST) in RFC 7030.

### Non-Goals

`swarmauri_certs_remote_ca` owns remote CA certificate service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_certs_remote_ca
```

```bash
poetry add swarmauri_certs_remote_ca
```

```bash
uv pip install swarmauri_certs_remote_ca
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_remote_ca
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_remote_ca
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_remote_ca
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/docs/readme/quick_start.py).

```python
import asyncio
import base64
import json

import httpx

from swarmauri_certs_remote_ca import RemoteCaCertService

csr = b"example-csr"
cert_bytes = b"example-cert"


async def main() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.content)
        assert base64.b64decode(data["csr"]) == csr
        return httpx.Response(
            200,
            json={"cert": base64.b64encode(cert_bytes).decode("ascii")},
        )

    svc = RemoteCaCertService("https://ca.example/sign")

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        svc._client = client  # Inject mock transport for the example.
        certificate = await svc.sign_cert(csr, {"kind": "dummy"})
        print(certificate)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_remote_ca` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/docs/readme/usage.py).

```python
import asyncio
import base64
import json

import httpx

from swarmauri_certs_remote_ca import RemoteCaCertService

csr = b"example-csr"
cert_bytes = b"example-cert"


async def main() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.content)
        assert base64.b64decode(data["csr"]) == csr
        return httpx.Response(
            200,
            json={"cert": base64.b64encode(cert_bytes).decode("ascii")},
        )

    svc = RemoteCaCertService("https://ca.example/sign")

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        svc._client = client  # Inject mock transport for the example.
        certificate = await svc.sign_cert(csr, {"kind": "dummy"})
        print(certificate)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The service is asynchronous and expects an existing CSR (certificate signing
request) in PEM or DER form.  Configure the remote CA endpoint and submit the
CSR to receive the issued certificate:


The example above mocks a CA using `httpx.MockTransport`.  In real scenarios
`RemoteCaCertService` posts the CSR to the configured endpoint and returns the
certificate bytes supplied by the remote CA.

When used against a real service, provide any required authentication headers
through the `auth` argument and override request or response formats via the
`opts` parameter of `sign_cert`.

### Configuration

`RemoteCaCertService` accepts the following arguments:

- `endpoint` ? Base URL of the remote CA sign endpoint.
- `auth` ? Optional mapping of HTTP headers or an `httpx.Auth` instance for
  authentication.
- `timeout_s` ? HTTP timeout in seconds (default `10`).
- `ca_chain` ? Optional sequence of cached trust anchors exposed during
  verification and parsing.

### Error Handling

The inspected `swarmauri_certs_remote_ca` source raises `ImportError`, `NotImplementedError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_certs_remote_ca` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `RemoteCaCertService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_certs_remote_ca` is located in `standards` and owns remote CA certificate service for Swarmauri. Source-declared APIs include `RemoteCaCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_remote_ca`.

Source-declared exports or types: `RemoteCaCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/swarmauri_certs_remote_ca/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.certs` → `RemoteCaCertService` → `swarmauri_certs_remote_ca:RemoteCaCertService`
<!-- readme-standards:end entry-points -->

The service registers under the `swarmauri.certs` entry point as
`RemoteCaCertService`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_remote_ca` are `swarmauri-core`, `swarmauri-base`, `httpx`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/swarmauri_certs_remote_ca/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_remote_ca` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_remote_ca`, use the source-declared public interfaces (`RemoteCaCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_remote_ca` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_remote_ca`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/swarmauri_certs_remote_ca/__init__.py). The `swarmauri_certs_remote_ca` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_remote_ca` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_remote_ca` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/tests/example/test_readme_usage.py)
- [tests/functional/test_sign_cert_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/tests/functional/test_sign_cert_functional.py)
- [tests/perf/test_sign_cert_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/tests/perf/test_sign_cert_perf.py)
- [tests/unit/test_rfc5280_reference.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/tests/unit/test_rfc5280_reference.py)
- [tests/unit/test_rfc7030_reference.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/tests/unit/test_rfc7030_reference.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_remote_ca` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/swarmauri_certs_remote_ca/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_certs_remote_ca` provides remote CA certificate service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_remote_ca`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/swarmauri_certs_remote_ca/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_remote_ca` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/swarmauri_certs_remote_ca/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/pyproject.toml) provide the supporting context for `swarmauri_certs_remote_ca`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_remote_ca](https://pypi.org/project/swarmauri_certs_remote_ca/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_certs_remote_ca` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certs_remote_ca` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_remote_ca` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_remote_ca` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_remote_ca` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_remote_ca/NOTICE) for attribution.
<!-- readme-standards:end notices -->
