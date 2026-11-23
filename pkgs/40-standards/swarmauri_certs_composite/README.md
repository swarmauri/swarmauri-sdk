# swarmauri_certs_composite

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_composite</strong></p>
<p align="center">Feature-routing certificate service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_composite/"><img alt="pypi: swarmauri_certs_composite" src="https://img.shields.io/pypi/v/swarmauri_certs_composite?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_composite/"><img alt="Monthly PyPI downloads: swarmauri_certs_composite" src="https://img.shields.io/pypi/dm/swarmauri_certs_composite?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/README.md"><img alt="README hits: swarmauri_certs_composite" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_certs_composite/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certs_composite`: Feature-routing certificate service for Swarmauri

### Why This Package

`swarmauri_certs_composite` isolates this responsibility: Feature-routing certificate service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/swarmauri_certs_composite/__init__.py) exposes `CompositeCertService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_certs_composite` when your integration needs feature-routing certificate service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Compose any `ICertService` implementations into one entry point.
- Route automatically by declared capability or override explicitly per call.
- Inspect supported features at runtime to drive UI/UX decisions.
- Ship as the default `swarmauri.certs` plugin named `CompositeCertService`.

### Non-Goals

`swarmauri_certs_composite` owns feature-routing certificate service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_certs_composite

# Poetry
poetry add swarmauri_certs_composite

# uv
uv add swarmauri_certs_composite
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_composite
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_composite
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_composite
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

The composite accepts a sequence of certificate service implementations and
routes each call to the first provider that advertises a matching capability.
Below is a self-contained example that you can run with `python quickstart.py`.


`supports()` aggregates the advertised features of all child providers so callers
can inspect available capabilities before invoking them. Passing
`opts={"backend": "ProviderType"}` overrides the automatic routing when you
need to target a specific provider.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_certs_composite import CompositeCertService
from swarmauri_base.certs.CertServiceBase import CertServiceBase


class SelfSignedOnly(CertServiceBase):
    def supports(self):
        return {"features": ("self_signed",)}

    async def create_self_signed(self, key, subject, **kw):
        return b"self-signed-cert"


class PrimaryCSR(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"primary-csr"


class SecondaryCSR(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"secondary-csr"


async def main():
    svc = CompositeCertService(
        [SelfSignedOnly(), PrimaryCSR(), SecondaryCSR()]
    )

    features = svc.supports()["features"]
    print("Advertised features:", sorted(features))

    cert = await svc.create_self_signed("key", {"CN": "example"})
    print("Self-signed cert:", cert)

    csr = await svc.create_csr("key", {"CN": "example"})
    print("CSR from primary provider:", csr)

    csr_override = await svc.create_csr(
        "key", {"CN": "example"}, opts={"backend": "SecondaryCSR"}
    )
    print("CSR via explicit backend override:", csr_override)


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_composite` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/docs/readme/usage.py).

```python
import asyncio

from swarmauri_certs_composite import CompositeCertService
from swarmauri_base.certs.CertServiceBase import CertServiceBase


class SelfSignedOnly(CertServiceBase):
    def supports(self):
        return {"features": ("self_signed",)}

    async def create_self_signed(self, key, subject, **kw):
        return b"self-signed-cert"


class PrimaryCSR(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"primary-csr"


class SecondaryCSR(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"secondary-csr"


async def main():
    svc = CompositeCertService(
        [SelfSignedOnly(), PrimaryCSR(), SecondaryCSR()]
    )

    features = svc.supports()["features"]
    print("Advertised features:", sorted(features))

    cert = await svc.create_self_signed("key", {"CN": "example"})
    print("Self-signed cert:", cert)

    csr = await svc.create_csr("key", {"CN": "example"})
    print("CSR from primary provider:", csr)

    csr_override = await svc.create_csr(
        "key", {"CN": "example"}, opts={"backend": "SecondaryCSR"}
    )
    print("CSR via explicit backend override:", csr_override)


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_certs_composite` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/swarmauri_certs_composite/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_composite` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_certs_composite` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CompositeCertService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_certs_composite` is located in `standards` and owns feature-routing certificate service for Swarmauri. Source-declared APIs include `CompositeCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_composite`.

Source-declared exports or types: `CompositeCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/swarmauri_certs_composite/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.certs` → `composite` → `swarmauri_certs_composite:CompositeCertService`
- `swarmauri.certs` → `CompositeCertService` → `swarmauri_certs_composite:CompositeCertService`
<!-- readme-standards:end entry-points -->

The provider is registered under the `swarmauri.certs` entry-point as `CompositeCertService`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_composite` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/swarmauri_certs_composite/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_composite` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_composite`, use the source-declared public interfaces (`CompositeCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_composite` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_composite`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/swarmauri_certs_composite/__init__.py). The `swarmauri_certs_composite` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_composite` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_composite` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_usage_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/tests/example/test_usage_example.py)
- [tests/functional/test_compositecertservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/tests/functional/test_compositecertservice_functional.py)
- [tests/perf/test_compositecertservice_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/tests/perf/test_compositecertservice_perf.py)
- [tests/unit/test_compositecertservice_rfc2986.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/tests/unit/test_compositecertservice_rfc2986.py)
- [tests/unit/test_compositecertservice_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/tests/unit/test_compositecertservice_rfc5280.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_composite` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/swarmauri_certs_composite/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_certs_composite` provides feature-routing certificate service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_composite`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/swarmauri_certs_composite/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_composite` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/swarmauri_certs_composite/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml) provide the supporting context for `swarmauri_certs_composite`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_composite](https://pypi.org/project/swarmauri_certs_composite/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certs_composite`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_certs_composite` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Certs Composite**

`CompositeCertService` is a lightweight router that coordinates multiple
certificate providers behind a single facade. Configure it with the services
you already have (self-signed, ACME, Vault, PKCS#11, etc.) and the composite
chooses the right backend based on the feature you request.

**For Contributors**

If you want to contribute to `swarmauri_certs_composite`, please read our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
and
[style guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/STYLE_GUIDE.md)
to get started.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_composite` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_composite` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_composite` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/LICENSE).
<!-- readme-standards:end license -->

`swarmauri_certs_composite` is licensed under the Apache License 2.0. See the
[LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/LICENSE) file
for details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_composite/NOTICE) for attribution.
<!-- readme-standards:end notices -->
