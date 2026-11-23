# swarmauri_certservice_ms_adcs

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certservice_ms_adcs</strong></p>
<p align="center">Microsoft AD CS oriented Swarmauri certificate service for PKCS#10 CSR creation, local self-signed certificates, verification, parsing, and auth setup.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/"><img alt="pypi: swarmauri_certservice_ms_adcs" src="https://img.shields.io/pypi/v/swarmauri_certservice_ms_adcs?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/"><img alt="Monthly PyPI downloads: swarmauri_certservice_ms_adcs" src="https://img.shields.io/pypi/dm/swarmauri_certservice_ms_adcs?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/README.md"><img alt="README hits: swarmauri_certservice_ms_adcs" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_certservice_ms_adcs/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certservice_ms_adcs` provides `MsAdcsCertService`, a Swarmauri certificate service prepared for Microsoft Active Directory Certificate Services environments. The implemented runtime builds PKCS#10 CSRs from PEM private keys, creates local self-signed certificates, verifies issued certificates against supplied issuers, parses X.509 metadata, and configures HTTP authentication sessions for AD CS Web Enrollment endpoints.

### Why This Package

Use this package when Swarmauri workflows need AD CS-compatible certificate request generation and local certificate inspection while preserving room for NTLM, Kerberos, basic, or anonymous Web Enrollment access. It gives enterprise PKI code one `CertServiceBase` component for CSR creation, self-signed test certificates, verification, parsing, and authentication configuration.

### When to Use

Choose `swarmauri_certservice_ms_adcs` when your integration needs microsoft AD CS oriented Swarmauri certificate service for PKCS#10 CSR creation, local self-signed certificates, verification, parsing, and auth setup. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `MsAdcsCertService` class registered under the `swarmauri.cert_services` entry point.
- HTTP session setup for AD CS-style endpoints with configurable TLS verification.
- NTLM, Kerberos/SPNEGO, HTTP Basic, and anonymous authentication modes.
- PKCS#10 CSR creation from PEM private keys in `KeyRef.material`.
- Subject support for standard X.509 distinguished-name fields and custom RDNs.
- SAN support for DNS, IP, URI, email, and UPN entries.
- Key usage and extended key usage CSR extension support.
- Local self-signed certificate generation for development and tests.
- Certificate verification with validity-window checks and optional issuer signature verification.
- X.509 metadata parsing for audit and observability workflows.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certservice_ms_adcs` owns microsoft AD CS oriented Swarmauri certificate service for PKCS#10 CSR creation, local self-signed certificates, verification, parsing, and auth setup. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Network access to an AD CS Web Enrollment endpoint when integrating with a live CA.
- PEM private key material for CSR and self-signed certificate creation.
- Optional httpx-compatible adapters for NTLM or Kerberos/SPNEGO authentication.
- Issuer certificates when using signature verification.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certservice_ms_adcs
```

Install with `pip`:

```bash
pip install swarmauri_certservice_ms_adcs
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certservice_ms_adcs
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certservice_ms_adcs
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certservice_ms_adcs
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/docs/readme/quick_start.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = MsAdcsCertService(
        base_url="https://ca.example.com/certsrv",
        default_template="WebServer",
        auth=_AuthCfg(mode="none"),
    )
    key_ref = KeyRef(material=Path("webserver.key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"C": "US", "O": "Example Corp", "CN": "app.example.com"},
        san={"dns": ["app.example.com", "www.example.com"]},
    )
    Path("app.csr").write_bytes(csr)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certservice_ms_adcs` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/docs/readme/usage.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = MsAdcsCertService(
        base_url="https://ca.example.com/certsrv",
        default_template="WebServer",
        auth=_AuthCfg(mode="none"),
    )
    key_ref = KeyRef(material=Path("webserver.key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"C": "US", "O": "Example Corp", "CN": "app.example.com"},
        san={"dns": ["app.example.com", "www.example.com"]},
    )
    Path("app.csr").write_bytes(csr)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Build a CSR for AD CS enrollment:


Create and inspect a local self-signed certificate:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = MsAdcsCertService(
        base_url="https://ca.example.com/certsrv",
        auth=_AuthCfg(mode="none"),
    )
    key_ref = KeyRef(material=Path("dev.key.pem").read_bytes())

    cert = await service.create_self_signed(
        key=key_ref,
        subject={"CN": "dev.example.com"},
    )
    parsed = await service.parse_cert(cert)
    verification = await service.verify_cert(cert, trust_roots=[cert])

    print(parsed["subject"])
    print(verification["valid"])


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certservice_ms_adcs` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/swarmauri_certservice_ms_adcs/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certservice_ms_adcs` source raises `NotImplementedError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Store AD CS credentials in a secure secrets manager and inject them at runtime.
- Treat generated CSRs, issued certificates, verification results, and parsed metadata as auditable enrollment artifacts.
- Regenerate CSRs before certificate expiry to leave time for manual approvals.
- Combine this service with CRL and OCSP verification packages for revocation visibility.

---

## Package Boundary

### What It Owns

`swarmauri_certservice_ms_adcs` is located in `community` and owns microsoft AD CS oriented Swarmauri certificate service for PKCS#10 CSR creation, local self-signed certificates, verification, parsing, and auth setup. Source-declared APIs include `MsAdcsCertService`, `_AuthCfg`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certservice_ms_adcs`.

Source-declared exports or types: `MsAdcsCertService`, `_AuthCfg`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/swarmauri_certservice_ms_adcs/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.cert_services` → `MsAdcsCertService` → `swarmauri_certservice_ms_adcs.MsAdcsCertService:MsAdcsCertService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certservice_ms_adcs` are `httpx`, `cryptography`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/swarmauri_certservice_ms_adcs/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certservice_ms_adcs` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certservice_ms_adcs`, use the source-declared public interfaces (`MsAdcsCertService`, `_AuthCfg`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certservice_ms_adcs` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certservice_ms_adcs`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/swarmauri_certservice_ms_adcs/__init__.py). The `swarmauri_certservice_ms_adcs` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certservice_ms_adcs` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certservice_ms_adcs` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_self_signed_roundtrip.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/tests/functional/test_self_signed_roundtrip.py)
- [tests/perf/test_csr_creation_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/tests/perf/test_csr_creation_perf.py)
- [tests/unit/test_rfc2986_pkcs10.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/tests/unit/test_rfc2986_pkcs10.py)
- [tests/unit/test_rfc5280_x509.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/tests/unit/test_rfc5280_x509.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certservice_ms_adcs` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/swarmauri_certservice_ms_adcs/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package submit CSRs to AD CS today?**

A: Not yet. `sign_cert()` currently raises `NotImplementedError`. Use `create_csr()` to build the request, then submit it through your AD CS Web Enrollment workflow or a custom automation layer.

**Q: Which authentication modes are modeled?**

A: `_AuthCfg` supports `basic` and `none` with the built-in `httpx` client. NTLM and Kerberos require an httpx-compatible auth adapter before use.

**Q: What certificate operations are implemented?**

A: CSR creation, self-signed certificate creation, validity/signature verification with supplied issuer certificates, and metadata parsing are implemented.

**Q: What certificate metadata can it parse?**

A: `parse_cert()` returns serial, signature algorithm, issuer, subject, validity timestamps, SKID, AKID, SAN, EKU, key usage, and CA status when those extensions are present.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certservice_ms_adcs`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/swarmauri_certservice_ms_adcs/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certservice_ms_adcs` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/swarmauri_certservice_ms_adcs/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/pyproject.toml) provide the supporting context for `swarmauri_certservice_ms_adcs`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certservice_scep](https://pypi.org/project/swarmauri_certservice_scep/)
- [swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)
- [swarmauri_certservice_aws_kms](https://pypi.org/project/swarmauri_certservice_aws_kms/)
- [swarmauri_certservice_gcpkms](https://pypi.org/project/swarmauri_certservice_gcpkms/)
- [swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
- [swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components for certificate-adjacent workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certservice_ms_adcs](https://pypi.org/project/swarmauri_certservice_ms_adcs/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certservice_ms_adcs`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_certservice_ms_adcs` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Authentication Modes**

- `ntlm`: provide an httpx-compatible NTLM auth adapter before using `_AuthCfg(mode="ntlm", username="DOMAIN\\user", password="...")`.
- `kerberos`: provide an httpx-compatible Kerberos/SPNEGO auth adapter before using `_AuthCfg(mode="kerberos", spnego_delegate=True)` when delegation is required.
- `basic`: provide `_AuthCfg(mode="basic", username="...", password="...")`.
- `none`: provide `_AuthCfg(mode="none")` for anonymous, mTLS-fronted, or externally authenticated flows.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certservice_ms_adcs` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certservice_ms_adcs` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certservice_ms_adcs` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_ms_adcs/NOTICE) for attribution.
<!-- readme-standards:end notices -->
