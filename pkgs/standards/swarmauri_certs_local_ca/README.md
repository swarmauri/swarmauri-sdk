# swarmauri_certs_local_ca

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_local_ca</strong></p>
<p align="center">Local CA certificate service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_local_ca/"><img alt="pypi: swarmauri_certs_local_ca" src="https://img.shields.io/pypi/v/swarmauri_certs_local_ca"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_local_ca/"><img alt="Monthly PyPI downloads: swarmauri_certs_local_ca" src="https://img.shields.io/pypi/dm/swarmauri_certs_local_ca"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/README.md"><img alt="README hits: swarmauri_certs_local_ca" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_certs_local_ca/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A local certificate authority implementing the `ICertService` interface for issuing and verifying X.509 certificates. Useful for development and testing environments where you need to bootstrap a private PKI quickly.

### Why This Package

`swarmauri_certs_local_ca` isolates this responsibility: Local CA certificate service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py) exposes `LocalCaCertService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_certs_local_ca` when your integration needs local CA certificate service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Generate CSRs with optional subject alternative names and certificate extensions.
- Create self-signed CA certificates with sensible defaults (1-year validity, CA basic constraints).
- Sign CSRs to produce leaf certificates, returning PEM or DER output.
- Perform basic certificate verification that ensures the certificate is currently valid and reports issuer/subject metadata.
- Parse certificates to extract key metadata and extension object identifiers.

> **Note:** `verify_cert` only evaluates validity windows; it does not build trust chains or check revocation lists.

### Non-Goals

`swarmauri_certs_local_ca` owns local CA certificate service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_certs_local_ca
```

```bash
poetry add swarmauri_certs_local_ca
```

If you use [uv](https://docs.astral.sh/uv/), install it first (for example with `pip install uv`) and then add the package:

```bash
uv pip install swarmauri_certs_local_ca
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_local_ca
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_local_ca
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_local_ca
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/docs/readme/quick_start.py).

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_certs_local_ca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _key(name: str) -> KeyRef:
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid=name,
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


async def main() -> None:
    svc = LocalCaCertService()
    ca_key = _key("ca")
    leaf_key = _key("leaf")

    # Create a certificate signing request for the leaf key.
    csr = await svc.create_csr(leaf_key, {"CN": "leaf"})

    # Sign the CSR with the CA key to produce a leaf certificate.
    cert = await svc.sign_cert(csr, ca_key, issuer={"CN": "ca"})

    # Verify the newly issued certificate.
    result = await svc.verify_cert(cert)
    print(result["valid"], result["subject"], result["issuer"])


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_local_ca` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/docs/readme/usage.py).

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_certs_local_ca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _key(name: str) -> KeyRef:
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid=name,
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


async def main() -> None:
    svc = LocalCaCertService()
    ca_key = _key("ca")
    leaf_key = _key("leaf")

    # Create a certificate signing request for the leaf key.
    csr = await svc.create_csr(leaf_key, {"CN": "leaf"})

    # Sign the CSR with the CA key to produce a leaf certificate.
    cert = await svc.sign_cert(csr, ca_key, issuer={"CN": "ca"})

    # Verify the newly issued certificate.
    result = await svc.verify_cert(cert)
    print(result["valid"], result["subject"], result["issuer"])


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Below is a minimal end-to-end example that issues and verifies a leaf
certificate signed by a local certificate authority.  The helper function
`_key` creates the ``KeyRef`` objects required by the service.


`verify_cert` returns a dictionary containing the validity flag plus the RFC 4514
representations of the subject and issuer.  For CA bootstrapping you can call
`create_self_signed` to generate a root certificate and use `parse_cert` to
inspect serial numbers, validity windows, and extension object identifiers.

### Configuration

Configure `swarmauri_certs_local_ca` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_local_ca` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py).

### Best Practices

Use the explicit `swarmauri_certs_local_ca` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `LocalCaCertService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_certs_local_ca` is located in `standards` and owns local CA certificate service for Swarmauri. Source-declared APIs include `LocalCaCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_local_ca`.

Source-declared exports or types: `LocalCaCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.cert_services` → `localca` → `swarmauri_certs_local_ca:LocalCaCertService`
- `swarmauri.cert_services` → `LocalCaCertService` → `swarmauri_certs_local_ca:LocalCaCertService`
<!-- readme-standards:end entry-points -->

The service registers under the `swarmauri.cert_services` entry point as `LocalCaCertService`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_local_ca` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_local_ca` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_local_ca`, use the source-declared public interfaces (`LocalCaCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_local_ca` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_local_ca`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py). The `swarmauri_certs_local_ca` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_local_ca` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_local_ca` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_service_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/tests/functional/test_service_functional.py)
- [tests/functional/test_usage_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/tests/functional/test_usage_example.py)
- [tests/perf/test_service_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/tests/perf/test_service_perf.py)
- [tests/unit/test_rfc2986_csr.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/tests/unit/test_rfc2986_csr.py)
- [tests/unit/test_rfc5280_basic_constraints.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/tests/unit/test_rfc5280_basic_constraints.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_local_ca` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_certs_local_ca` provides local CA certificate service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_local_ca`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_local_ca` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/swarmauri_certs_local_ca/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml) provide the supporting context for `swarmauri_certs_local_ca`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_certs_local_ca` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Supported algorithms**

`LocalCaCertService.supports()` reports the following capabilities:

- **Key algorithms:** `RSA-2048`, `RSA-3072`, `EC-P256`, `Ed25519`
- **Signature algorithms:** `RSA-PSS-SHA256`, `ECDSA-P256-SHA256`, `Ed25519`
- **Features:** CSR creation, self-signed issuance, CSR signing, verification, and parsing

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_local_ca` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_local_ca` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_local_ca` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_local_ca/NOTICE) for attribution.
<!-- readme-standards:end notices -->
