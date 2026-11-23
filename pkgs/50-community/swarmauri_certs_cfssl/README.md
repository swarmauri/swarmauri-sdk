# swarmauri_certs_cfssl

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_cfssl</strong></p>
<p align="center">CFSSL REST backed Swarmauri certificate service for CSR signing, bundle verification, PEM/DER conversion, and X.509 parsing.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_cfssl/"><img alt="pypi: swarmauri_certs_cfssl" src="https://img.shields.io/pypi/v/swarmauri_certs_cfssl?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_cfssl/"><img alt="Monthly PyPI downloads: swarmauri_certs_cfssl" src="https://img.shields.io/pypi/dm/swarmauri_certs_cfssl?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/README.md"><img alt="README hits: swarmauri_certs_cfssl" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_certs_cfssl/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certs_cfssl` provides `CfsslCertService`, a Swarmauri certificate-service adapter for Cloudflare CFSSL. It uses `httpx.AsyncClient` to call CFSSL REST endpoints for CSR signing and certificate bundling, and it uses `cryptography` to parse X.509 certificate metadata, convert PEM/DER encodings, and inspect certificate extensions.

### Why This Package

Use this package when Swarmauri applications need certificate signing through an existing CFSSL deployment. It keeps CFSSL profile routing, label routing, authentication headers, certificate parsing, verification, and connection reuse behind the common Swarmauri certificate-service interface.

### When to Use

Choose `swarmauri_certs_cfssl` when your integration needs cFSSL REST backed Swarmauri certificate service for CSR signing, bundle verification, PEM/DER conversion, and X.509 parsing. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `CfsslCertService` adapter that wraps the CFSSL REST API for signing, parsing, and verifying certificates.
- Supports RSA, ECDSA P-256/P-384, and Ed25519 capability metadata with profile and label routing.
- Optional certificate bundling during verification to ensure complete chains before deployment.
- Detailed parsing utilities that expose SANs, key usage, EKU, Subject/Authority Key Identifiers, and more.
- Bearer-token, custom auth-header, and custom-header support for protected CFSSL endpoints.
- Async connection reuse with explicit `aclose()` cleanup.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certs_cfssl` owns cFSSL REST backed Swarmauri certificate service for CSR signing, bundle verification, PEM/DER conversion, and X.509 parsing. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Python 3.10 or newer.
- A reachable CFSSL instance (standalone binary, Kubernetes deployment, or the Cloudflare Docker image).
- Valid CFSSL signing profile(s) configured for your use case (e.g., `www`, `client`, `code_signing`).
- If your CFSSL endpoint is protected, API credentials or access tokens for the headers you plan to use.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certs_cfssl
```

Install with `pip`:

```bash
pip install swarmauri_certs_cfssl
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_cfssl
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_cfssl
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_cfssl
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_certs_cfssl")
assert package.__name__ == "swarmauri_certs_cfssl"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_certs_cfssl`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_certs_cfssl")
assert package.__name__ == "swarmauri_certs_cfssl"
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_certs_cfssl` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/swarmauri_certs_cfssl/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_cfssl` source raises `ImportError`, `NotImplementedError`, `RuntimeError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Store CFSSL credentials outside source control (environment variables, secret stores, or Swarmauri state providers).
- Enable TLS on the CFSSL API and pin the certificate when connecting over untrusted networks.
- Use dedicated CFSSL profiles for each application tier and rotate them regularly.
- Capture verification results (e.g., bundle size, expiry) in metrics to stay ahead of certificate renewals.

---

## Package Boundary

### What It Owns

`swarmauri_certs_cfssl` is located in `community` and owns cFSSL REST backed Swarmauri certificate service for CSR signing, bundle verification, PEM/DER conversion, and X.509 parsing. Source-declared APIs include `CfsslCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_cfssl`.

Source-declared exports or types: `CfsslCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/swarmauri_certs_cfssl/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.cert_services` → `CfsslCertService` → `swarmauri_certs_cfssl.CfsslCertService:CfsslCertService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_cfssl` are `httpx`, `cryptography`, `pydantic`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/swarmauri_certs_cfssl/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_cfssl` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_cfssl`, use the source-declared public interfaces (`CfsslCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_cfssl` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_cfssl`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/swarmauri_certs_cfssl/__init__.py). The `swarmauri_certs_cfssl` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_cfssl` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_cfssl` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_cfssl_service_integration.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/tests/i9n/test_cfssl_service_integration.py)
- [tests/perf/test_cfssl_service_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/tests/perf/test_cfssl_service_perf.py)
- [tests/unit/test_registration.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/tests/unit/test_registration.py)
- [tests/unit/test_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/tests/unit/test_rfc5280.py)
- [tests/unit/test_rfc7468.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/tests/unit/test_rfc7468.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_cfssl` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/swarmauri_certs_cfssl/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package create CSRs?**

A: No. `CfsslCertService.create_csr()` raises `NotImplementedError`. Generate CSRs with `swarmauri_certs_x509`, `swarmauri_certs_acme`, another Swarmauri certificate service, or existing PKI tooling, then submit the CSR to CFSSL with `sign_cert()`.

**Q: Which CFSSL endpoints does it use?**

A: The runtime calls `/api/v1/cfssl/sign` for signing and `/api/v1/cfssl/bundle` for bundle-backed verification when `use_bundle_for_verify` is enabled.

**Q: What certificate details can it parse?**

A: `parse_cert()` returns subject, issuer, serial number, validity timestamps, basic constraints, SAN entries, key usage, extended key usage, subject key identifier, and authority key identifier when those extensions are present.

### How

**Q: How are CFSSL profiles and labels selected?**

A: Constructor defaults can set `default_profile` and `default_label`. Per-request `opts` or `KeyRef.tags` can override them when calling `sign_cert()`.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_cfssl` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/swarmauri_certs_cfssl/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/pyproject.toml) provide the supporting context for `swarmauri_certs_cfssl`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_azure](https://pypi.org/project/swarmauri_certs_azure/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_composite](https://pypi.org/project/swarmauri_certs_composite/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines the certificate-service interfaces and `KeyRef` types.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`, `ComponentBase`, and registration support.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components used alongside certificate workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certs_cfssl`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_certs_cfssl` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Quickstart: Issue a Certificate**

`CfsslCertService` consumes CSRs generated by other Swarmauri certificate services (for example, the Azure or ACME packages). The example below submits a CSR to CFSSL and saves the issued certificate:

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certs_cfssl import CfsslCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = CfsslCertService(
        base_url="https://cfssl.internal",
        default_profile="www",
        timeout_s=15.0,
        auth_header=("X-Auth-Key", "super-secret-token"),
    )

    csr_bytes = Path("site.csr").read_bytes()

    # KeyRef tags allow you to override CFSSL profile/label per request
    ca_key = KeyRef(material=b"", tags={"profile": "www", "label": "primary"})

    certificate_pem = await service.sign_cert(
        csr=csr_bytes,
        ca_key=ca_key,
        extensions={
            "subject_alt_name": {"dns": ["site.example.com", "www.site.example.com"]}
        },
        not_after=int((datetime.now(timezone.utc) + timedelta(days=90)).timestamp()),
    )

    Path("site.pem").write_bytes(certificate_pem)
    await service.aclose()


if __name__ == "__main__":
    asyncio.run(main())
```

**Verify and Parse Certificates**

Leverage CFSSL's bundling API to confirm a certificate's trust chain, then inspect the returned metadata:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_cfssl import CfsslCertService


async def verify_and_parse() -> None:
    service = CfsslCertService(
        base_url="https://cfssl.internal",
        use_bundle_for_verify=True,
    )

    cert_bytes = Path("site.pem").read_bytes()

    verification = await service.verify_cert(
        cert=cert_bytes,
        trust_roots=[Path("root.pem").read_bytes()],
    )
    print("Valid:", verification["valid"], "Chain length:", verification["chain_len"])

    parsed = await service.parse_cert(cert_bytes)
    print("Subject CN:", parsed["subject"].get("CN"))
    print("SAN entries:", parsed.get("san", {}))

    await service.aclose()


if __name__ == "__main__":
    asyncio.run(verify_and_parse())
```

- `CfsslCertService` focuses on signing and validation. Generate CSRs with other Swarmauri services (e.g., `swarmauri_certs_acme`, `swarmauri_certs_azure`) or your existing PKI tooling.
- The client uses `httpx.AsyncClient`; reuse a service instance for multiple operations and call `aclose()` when finished to release connections.
- Profile and label defaults can be set globally in the constructor or dynamically by attaching tags to the `KeyRef` passed into `sign_cert`.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_cfssl` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_cfssl` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_cfssl` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_cfssl/NOTICE) for attribution.
<!-- readme-standards:end notices -->
