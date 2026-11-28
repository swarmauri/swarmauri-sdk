# swarmauri_certs_self_signed

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_self_signed</strong></p>
<p align="center">Self-signed certificate builder for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_self_signed/"><img alt="pypi: swarmauri_certs_self_signed" src="https://img.shields.io/pypi/v/swarmauri_certs_self_signed?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_self_signed/"><img alt="Monthly PyPI downloads: swarmauri_certs_self_signed" src="https://img.shields.io/pypi/dm/swarmauri_certs_self_signed?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/README.md"><img alt="README hits: swarmauri_certs_self_signed" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_certs_self_signed/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Standalone plugin providing utilities to issue self-signed X.509 certificates using the `SelfSignedCertificate` builder.

### Why This Package

`swarmauri_certs_self_signed` isolates this responsibility: Self-signed certificate builder for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/swarmauri_certs_self_signed/__init__.py) exposes `SelfSignedCertificate`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_certs_self_signed` when your integration needs self-signed certificate builder for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Issue PEM (default) or DER encoded self-signed certificates from existing private keys.
- Populate subjects, subject alternative names, name constraints, and key usage extensions via simple dictionaries.
- Convenience constructors for common TLS server and mTLS client certificates.
- Automatically reuse a passphrase stored in `KeyRef.tags["passphrase"]` when loading encrypted keys.

### Non-Goals

`swarmauri_certs_self_signed` owns self-signed certificate builder for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_certs_self_signed

# Poetry
poetry add swarmauri_certs_self_signed

# uv
uv add swarmauri_certs_self_signed
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_self_signed
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_self_signed
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_self_signed
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

`SelfSignedCertificate` operates on a `KeyRef` whose `material` holds the PEM encoded private key. The example below generates an Ed25519 key, issues a TLS server certificate with DNS subject alternative names, and prints the PEM header of the resulting certificate.


The builder automatically mirrors the TLS server defaults: the subject common name is set from `common_name`, all DNS names are added to the SAN extension, and the certificate is valid for 397 days unless overridden. Set `output_der=True` on the builder to receive DER encoded bytes instead of PEM.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/docs/readme/quick_start.py).

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_certs_self_signed import SelfSignedCertificate

private_key = ed25519.Ed25519PrivateKey.generate()
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

key_ref = KeyRef(
    kid="example-ed25519",
    version=1,
    type=KeyType.ED25519,
    uses=(KeyUse.SIGN,),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=private_bytes,
)

builder = SelfSignedCertificate.tls_server(
    common_name="example.local",
    dns_names=["example.local", "api.example.local"],
)

certificate_pem = builder.issue(key_ref)
print(certificate_pem.decode().splitlines()[0])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_self_signed` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/docs/readme/usage.py).

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_certs_self_signed import SelfSignedCertificate

private_key = ed25519.Ed25519PrivateKey.generate()
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

key_ref = KeyRef(
    kid="example-ed25519",
    version=1,
    type=KeyType.ED25519,
    uses=(KeyUse.SIGN,),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=private_bytes,
)

builder = SelfSignedCertificate.tls_server(
    common_name="example.local",
    dns_names=["example.local", "api.example.local"],
)

certificate_pem = builder.issue(key_ref)
print(certificate_pem.decode().splitlines()[0])
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_certs_self_signed` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/swarmauri_certs_self_signed/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_self_signed` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_certs_self_signed` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SelfSignedCertificate`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_certs_self_signed` is located in `standards` and owns self-signed certificate builder for Swarmauri. Source-declared APIs include `SelfSignedCertificate`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_self_signed`.

Source-declared exports or types: `SelfSignedCertificate`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/swarmauri_certs_self_signed/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.cert_services` → `selfsigned` → `swarmauri_certs_self_signed:SelfSignedCertificate`
- `swarmauri.cert_services` → `SelfSignedCertificate` → `swarmauri_certs_self_signed:SelfSignedCertificate`
<!-- readme-standards:end entry-points -->

This package registers `SelfSignedCertificate` under both the `swarmauri.cert_services` and `peagen.plugins.cert_services` entry points.

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_self_signed` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/swarmauri_certs_self_signed/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_self_signed` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_self_signed`, use the source-declared public interfaces (`SelfSignedCertificate`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_self_signed` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_self_signed`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/swarmauri_certs_self_signed/__init__.py). The `swarmauri_certs_self_signed` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_self_signed` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_self_signed` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_quickstart.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/tests/example/test_readme_quickstart.py)
- [tests/functional/test_self_signed_certificate_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/tests/functional/test_self_signed_certificate_functional.py)
- [tests/perf/test_self_signed_certificate_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/tests/perf/test_self_signed_certificate_perf.py)
- [tests/unit/test_rfc5280_cert.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/tests/unit/test_rfc5280_cert.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_self_signed` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/swarmauri_certs_self_signed/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_certs_self_signed` provides self-signed certificate builder for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_self_signed`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/swarmauri_certs_self_signed/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_self_signed` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/swarmauri_certs_self_signed/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml) provide the supporting context for `swarmauri_certs_self_signed`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_certs_self_signed` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certs_self_signed` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_self_signed` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_self_signed` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_self_signed` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_self_signed/NOTICE) for attribution.
<!-- readme-standards:end notices -->
