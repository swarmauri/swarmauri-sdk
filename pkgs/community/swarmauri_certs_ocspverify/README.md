# swarmauri_certs_ocspverify

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_ocspverify</strong></p>
<p align="center">OCSP-based Swarmauri certificate verification service for RFC 6960 revocation checks, responder lookup, and X.509 metadata parsing.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_ocspverify/"><img alt="pypi: swarmauri_certs_ocspverify" src="https://img.shields.io/pypi/v/swarmauri_certs_ocspverify"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_ocspverify/"><img alt="Monthly PyPI downloads: swarmauri_certs_ocspverify" src="https://img.shields.io/pypi/dm/swarmauri_certs_ocspverify"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/README.md"><img alt="README hits: swarmauri_certs_ocspverify" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_certs_ocspverify/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certs_ocspverify` provides `OcspVerifyService`, a Swarmauri certificate service for Online Certificate Status Protocol checks. It reads OCSP responder URLs from the certificate Authority Information Access extension, builds DER OCSP requests with the issuer certificate, posts them with `httpx`, and reports whether the responder returned a GOOD certificate status.

### Why This Package

Use this package when Swarmauri applications need live revocation checks for PEM X.509 certificates. It keeps OCSP request construction, responder lookup, HTTP submission, status parsing, and basic certificate metadata extraction behind the common Swarmauri certificate-service interface.

### When to Use

Choose `swarmauri_certs_ocspverify` when your integration needs oCSP-based Swarmauri certificate verification service for RFC 6960 revocation checks, responder lookup, and X.509 metadata parsing. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `OcspVerifyService` class registered under the `swarmauri.certs` entry point.
- OCSP responder URL extraction from the Authority Information Access extension.
- DER OCSP request construction with `cryptography.x509.ocsp.OCSPRequestBuilder`.
- Async HTTP OCSP responder calls through `httpx.AsyncClient`.
- GOOD-status mapping to `valid=True`.
- `this_update` and `next_update` timestamp reporting from OCSP responses.
- Certificate metadata parsing for subject, issuer, not-before, not-after, and OCSP URLs.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certs_ocspverify` owns oCSP-based Swarmauri certificate verification service for RFC 6960 revocation checks, responder lookup, and X.509 metadata parsing. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- PEM-encoded leaf certificate to inspect and validate.
- PEM-encoded issuer certificate supplied through `intermediates`.
- Network access to the OCSP responder URL embedded in the leaf certificate.
- Application-level retry, timeout, and cache policy for production revocation checks.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certs_ocspverify
```

Install with `pip`:

```bash
pip install swarmauri_certs_ocspverify
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_ocspverify
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_ocspverify
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_ocspverify
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/docs/readme/quick_start.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certs_ocspverify import OcspVerifyService


async def main() -> None:
    service = OcspVerifyService()
    verification = await service.verify_cert(
        cert=Path("leaf.pem").read_bytes(),
        intermediates=[Path("issuer.pem").read_bytes()],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate status: GOOD")
    else:
        print("Certificate status:", verification["reason"])
    print("Next update:", verification.get("next_update"))


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_ocspverify` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/docs/readme/usage.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certs_ocspverify import OcspVerifyService


async def main() -> None:
    service = OcspVerifyService()
    verification = await service.verify_cert(
        cert=Path("leaf.pem").read_bytes(),
        intermediates=[Path("issuer.pem").read_bytes()],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate status: GOOD")
    else:
        print("Certificate status:", verification["reason"])
    print("Next update:", verification.get("next_update"))


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Perform an OCSP status check for a leaf certificate using its issuer certificate:


Inspect certificate metadata and embedded OCSP responder URLs:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_ocspverify import OcspVerifyService


async def main() -> None:
    service = OcspVerifyService()
    metadata = await service.parse_cert(Path("leaf.pem").read_bytes())

    print("Subject:", metadata["subject"])
    print("Issuer:", metadata["issuer"])
    print("OCSP URLs:", metadata.get("ocsp_urls", []))


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certs_ocspverify` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/swarmauri_certs_ocspverify/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_ocspverify` source raises `NotImplementedError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Cache issuer certificates alongside leaf certificates so OCSP requests can be constructed quickly.
- Respect OCSP responder rate limits and cache GOOD responses until `next_update` when policy allows.
- Combine OCSP checks with CRL fallback for authorities that support multiple revocation mechanisms.
- Log `reason`, `ocsp_checked`, `this_update`, and `next_update` fields for incident response and compliance reporting.

---

## Package Boundary

### What It Owns

`swarmauri_certs_ocspverify` is located in `community` and owns oCSP-based Swarmauri certificate verification service for RFC 6960 revocation checks, responder lookup, and X.509 metadata parsing. Source-declared APIs include `OcspVerifyService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_ocspverify`.

Source-declared exports or types: `OcspVerifyService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/swarmauri_certs_ocspverify/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.certs` → `OcspVerifyService` → `swarmauri_certs_ocspverify.OcspVerifyService:OcspVerifyService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_ocspverify` are `cryptography`, `httpx`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/swarmauri_certs_ocspverify/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_ocspverify` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_ocspverify`, use the source-declared public interfaces (`OcspVerifyService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_ocspverify` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_ocspverify`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/swarmauri_certs_ocspverify/__init__.py). The `swarmauri_certs_ocspverify` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_ocspverify` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_ocspverify` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_ocspverify_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/tests/functional/test_ocspverify_functional.py)
- [tests/perf/test_ocspverify_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/tests/perf/test_ocspverify_perf.py)
- [tests/unit/test_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/tests/unit/test_rfc5280.py)
- [tests/unit/test_rfc6960.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/tests/unit/test_rfc6960.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_ocspverify` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/swarmauri_certs_ocspverify/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package issue or sign certificates?**

A: No. `create_csr()`, `create_self_signed()`, and `sign_cert()` intentionally raise `NotImplementedError`; this service is verification-only.

**Q: What input does OCSP verification require?**

A: `verify_cert()` requires the leaf certificate as PEM bytes and the issuer certificate as the first item in `intermediates`. The issuer certificate is required to build the OCSP request.

**Q: Which standards does this package target?**

A: The implementation documents RFC 6960 for OCSP behavior and RFC 5280 for X.509 certificate and Authority Information Access metadata.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_ocspverify`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/swarmauri_certs_ocspverify/__init__.py) for the exact types and signatures involved.

### When

**Q: What happens when a certificate has no OCSP URL?**

A: The service returns `valid=False`, `reason="no_ocsp_url"`, and `ocsp_checked=False`.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/swarmauri_certs_ocspverify/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/pyproject.toml) provide the supporting context for `swarmauri_certs_ocspverify`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate-service interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components for certificate-adjacent workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certs_ocspverify`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_certs_ocspverify` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certs_ocspverify` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_ocspverify` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_ocspverify` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_ocspverify` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_ocspverify/NOTICE) for attribution.
<!-- readme-standards:end notices -->
