# swarmauri_certs_crlverifyservice

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_crlverifyservice</strong></p>
<p align="center">CRL-based Swarmauri certificate verification service for RFC 5280 revocation checks and X.509 metadata parsing.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/"><img alt="pypi: swarmauri_certs_crlverifyservice" src="https://img.shields.io/pypi/v/swarmauri_certs_crlverifyservice"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/"><img alt="Monthly PyPI downloads: swarmauri_certs_crlverifyservice" src="https://img.shields.io/pypi/dm/swarmauri_certs_crlverifyservice"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/README.md"><img alt="README hits: swarmauri_certs_crlverifyservice" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_certs_crlverifyservice/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certs_crlverifyservice` provides `CrlVerifyService`, a Swarmauri certificate service for Certificate Revocation List based X.509 verification. It validates certificate validity windows, compares CRL issuers with certificate issuers, detects revoked serial numbers, and parses certificate metadata for audit and observability workflows.

### Why This Package

Use this package when Swarmauri applications need a lightweight revocation-aware certificate verifier without delegating to an external OCSP responder or CA API. It gives PKI monitoring, certificate deployment checks, and compliance workflows a direct Swarmauri interface for CRL-based RFC 5280 verification.

### When to Use

Choose `swarmauri_certs_crlverifyservice` when your integration needs cRL-based Swarmauri certificate verification service for RFC 5280 revocation checks and X.509 metadata parsing. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `CrlVerifyService` adapter dedicated to revocation-aware verification and parsing.
- Certificate validity-window checks using caller-provided `check_time` or current UTC time.
- CRL issuer matching before revoked serial lookup.
- PEM certificate parsing and PEM/DER CRL parsing through `cryptography`.
- Structured validity metadata, revocation flags, issuers, and extension details.
- Verification-only design that delegates CSR and signing flows to other Swarmauri services.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certs_crlverifyservice` owns cRL-based Swarmauri certificate verification service for RFC 5280 revocation checks and X.509 metadata parsing. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Access to current CRLs for the certificate authorities being checked.
- PEM-encoded leaf certificates.
- PEM or DER CRLs.
- Optional trusted root or intermediate certificates when the caller wants to record issuer context alongside revocation checks.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certs_crlverifyservice
```

Install with `pip`:

```bash
pip install swarmauri_certs_crlverifyservice
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_crlverifyservice
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_crlverifyservice
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_crlverifyservice
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/docs/readme/quick_start.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certs_crlverifyservice import CrlVerifyService


async def main() -> None:
    service = CrlVerifyService()
    verification = await service.verify_cert(
        cert=Path("leaf.pem").read_bytes(),
        crls=[Path("issuer.crl").read_bytes()],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate is valid.")
    elif verification.get("revoked"):
        print("Certificate was revoked:", verification["reason"])
    else:
        print("Certificate failed validation:", verification["reason"])


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_crlverifyservice` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/docs/readme/usage.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certs_crlverifyservice import CrlVerifyService


async def main() -> None:
    service = CrlVerifyService()
    verification = await service.verify_cert(
        cert=Path("leaf.pem").read_bytes(),
        crls=[Path("issuer.crl").read_bytes()],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate is valid.")
    elif verification.get("revoked"):
        print("Certificate was revoked:", verification["reason"])
    else:
        print("Certificate failed validation:", verification["reason"])


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Load a certificate and its corresponding CRL, then validate the revocation status and validity window:


Parse certificate metadata for logging, auditing, or dashboards:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_crlverifyservice import CrlVerifyService


async def main() -> None:
    service = CrlVerifyService()
    metadata = await service.parse_cert(Path("leaf.pem").read_bytes())

    print("Subject:", metadata["subject"])
    print("Valid until:", metadata["not_after"])
    print("Key usage:", metadata.get("key_usage"))


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certs_crlverifyservice` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/swarmauri_certs_crlverifyservice/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_crlverifyservice` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/swarmauri_certs_crlverifyservice/__init__.py).

### Best Practices

- Refresh CRLs frequently; RFC 5280 `nextUpdate` dictates how long a CRL should be considered valid.
- Combine this service with Swarmauri signing services to perform a full lifecycle check from issue to deploy to monitor.
- Cache CRLs in memory or a fast datastore to avoid repeatedly loading or downloading them when calling `verify_cert`.
- Log verification outputs, especially `reason` and `revoked`, to your observability pipeline to catch trust issues early.

---

## Package Boundary

### What It Owns

`swarmauri_certs_crlverifyservice` is located in `community` and owns cRL-based Swarmauri certificate verification service for RFC 5280 revocation checks and X.509 metadata parsing. Source-declared APIs include `CrlVerifyService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_crlverifyservice`.

Source-declared exports or types: `CrlVerifyService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/swarmauri_certs_crlverifyservice/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.cert_services` → `CrlVerifyService` → `swarmauri_certs_crlverifyservice.CrlVerifyService:CrlVerifyService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_crlverifyservice` are `cryptography`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/swarmauri_certs_crlverifyservice/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_crlverifyservice` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_crlverifyservice`, use the source-declared public interfaces (`CrlVerifyService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_crlverifyservice` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_crlverifyservice`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/swarmauri_certs_crlverifyservice/__init__.py). The `swarmauri_certs_crlverifyservice` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_crlverifyservice` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_crlverifyservice` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_crlverifyservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/tests/functional/test_crlverifyservice_functional.py)
- [tests/perf/test_verify_cert_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/tests/perf/test_verify_cert_perf.py)
- [tests/unit/test_crlverifyservice.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/tests/unit/test_crlverifyservice.py)
- [tests/unit/test_crlverifyservice_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/tests/unit/test_crlverifyservice_rfc5280.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_crlverifyservice` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/swarmauri_certs_crlverifyservice/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package issue or sign certificates?**

A: No. CSR creation, self-signed certificate creation, and certificate signing are intentionally outside this service. Use Swarmauri certificate packages such as `swarmauri_certs_x509`, `swarmauri_certs_local_ca`, `swarmauri_certs_acme`, or `swarmauri_certs_cfssl` for issuance workflows.

**Q: What encodings does it accept?**

A: The implemented certificate path expects PEM-encoded certificates. CRLs may be PEM or DER because `verify_cert()` falls back to DER CRL loading when PEM CRL parsing fails.

**Q: What does verification return?**

A: `verify_cert()` returns validity, reason, subject, issuer, not-before, not-after, and revoked fields. Revoked certificates return `valid=False`, `revoked=True`, and `reason="revoked"`.

**Q: What metadata does parsing return?**

A: `parse_cert()` returns serial number, subject, issuer, validity timestamps, signature algorithm, and selected extensions such as basic constraints and key usage when present.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_crlverifyservice`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/swarmauri_certs_crlverifyservice/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_crlverifyservice` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/swarmauri_certs_crlverifyservice/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/pyproject.toml) provide the supporting context for `swarmauri_certs_crlverifyservice`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate-service interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides certificate service base behavior.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certs_crlverifyservice`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_certs_crlverifyservice` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certs_crlverifyservice` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_crlverifyservice` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_crlverifyservice` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_crlverifyservice` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_crlverifyservice/NOTICE) for attribution.
<!-- readme-standards:end notices -->
