# swarmauri_certs_acme

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_acme</strong></p>
<p align="center">ACME v2 certificate service for Swarmauri CSR creation, certificate issuance, PEM chain retrieval, and X.509 inspection.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_acme/"><img alt="pypi: swarmauri_certs_acme" src="https://img.shields.io/pypi/v/swarmauri_certs_acme?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_acme/"><img alt="Monthly PyPI downloads: swarmauri_certs_acme" src="https://img.shields.io/pypi/dm/swarmauri_certs_acme?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/README.md"><img alt="README hits: swarmauri_certs_acme" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_certs_acme/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certs_acme` provides `AcmeCertService`, a Swarmauri certificate service for ACME v2 certificate issuance. It uses the Python `acme` client and `cryptography` primitives to build PKCS#10 certificate signing requests, submit ACME orders, finalize issued certificates, return PEM or DER chains, and inspect X.509 certificate metadata.

### Why This Package

Use this package when Swarmauri workloads need automated certificate issuance through an ACME certificate authority such as Let's Encrypt. It keeps ACME directory discovery, account-key handling, CSR creation, order finalization, certificate parsing, and capability reporting behind the common Swarmauri certificate-service interface.

### When to Use

Choose `swarmauri_certs_acme` when your integration needs aCME v2 certificate service for Swarmauri CSR creation, certificate issuance, PEM chain retrieval, and X.509 inspection. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `AcmeCertService` class registered under the `swarmauri.certs` entry point.
- ACME v2 directory discovery and `ClientV2` order finalization.
- PEM account-key loading from Swarmauri `KeyRef` objects.
- PKCS#10 CSR creation with common-name and DNS subject alternative name support.
- PEM full-chain retrieval by default, with DER chain output available.
- X.509 certificate parsing and basic validity-window inspection.
- Capability metadata for supported key algorithms, signature algorithms, profiles, and features.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certs_acme` owns aCME v2 certificate service for Swarmauri CSR creation, certificate issuance, PEM chain retrieval, and X.509 inspection. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- ACME account private key material available as PEM bytes.
- A CSR or host private key material for CSR creation.
- Network access to the target ACME directory.
- External automation for ACME challenge presentation and validation.
- Awareness of CA staging and production rate limits before running automated issuance.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certs_acme
```

Install with `pip`:

```bash
pip install swarmauri_certs_acme
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_acme
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_acme
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_acme
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/docs/readme/quick_start.py).

```python
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef

account_key = KeyRef(material=Path("account-key.pem").read_bytes())
service = AcmeCertService(
    account_key=account_key,
    contact_emails=["admin@example.com"],
)

print(service.supports()["features"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_acme` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/docs/readme/usage.py).

```python
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef

account_key = KeyRef(material=Path("account-key.pem").read_bytes())
service = AcmeCertService(
    account_key=account_key,
    contact_emails=["admin@example.com"],
)

print(service.supports()["features"])
```
<!-- readme-standards:end example.usage -->

Create an ACME service with a PEM account key:


Build a CSR for a host key:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())
    host_key = KeyRef(material=Path("server-key.pem").read_bytes())
    service = AcmeCertService(account_key=account_key)

    csr = await service.create_csr(
        key=host_key,
        subject={"CN": "example.com"},
        san={"dns": ["example.com", "www.example.com"]},
    )
    Path("server.csr").write_bytes(csr)


asyncio.run(main())
```

Submit a CSR and persist the returned certificate chain:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())
    service = AcmeCertService(account_key=account_key)

    certificate_chain = await service.sign_cert(
        csr=Path("server.csr").read_bytes(),
        ca_key=account_key,
    )
    Path("server-fullchain.pem").write_bytes(certificate_chain)


asyncio.run(main())
```

Inspect an issued certificate:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())
    service = AcmeCertService(account_key=account_key)
    pem_chain = Path("server-fullchain.pem").read_bytes()

    verification = await service.verify_cert(pem_chain)
    parsed = await service.parse_cert(pem_chain)

    print(verification["valid"])
    print(parsed["subject"])


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certs_acme` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/swarmauri_certs_acme/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_acme` source raises `NotImplementedError`, `RuntimeError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use ACME staging endpoints during development and load tests.
- Store account and host private keys in a secure KMS or vault-backed `KeyRef` workflow.
- Automate challenge presentation outside this package before finalizing orders.
- Cache issued certificate chains and renew before `not_after` to avoid service interruptions.

---

## Package Boundary

### What It Owns

`swarmauri_certs_acme` is located in `community` and owns aCME v2 certificate service for Swarmauri CSR creation, certificate issuance, PEM chain retrieval, and X.509 inspection. Source-declared APIs include `AcmeCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_acme`.

Source-declared exports or types: `AcmeCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/swarmauri_certs_acme/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.certs` → `AcmeCertService` → `swarmauri_certs_acme.AcmeCertService:AcmeCertService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_acme` are `acme`, `cryptography`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/swarmauri_certs_acme/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_acme` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_acme`, use the source-declared public interfaces (`AcmeCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_acme` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_acme`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/swarmauri_certs_acme/__init__.py). The `swarmauri_certs_acme` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_acme` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_acme` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/certs/test_acmecertservice_rfc2986.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/tests/unit/certs/test_acmecertservice_rfc2986.py)
- [tests/unit/certs/test_acmecertservice_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/tests/unit/certs/test_acmecertservice_rfc5280.py)
- [tests/unit/certs/test_acmecertservice_rfc8555.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/tests/unit/certs/test_acmecertservice_rfc8555.py)
- [tests/perf/certs/test_acmecertservice_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/tests/perf/certs/test_acmecertservice_perf.py)
- [tests/functional/certs/test_acmecertservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/tests/functional/certs/test_acmecertservice_functional.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_acme` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/swarmauri_certs_acme/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: What standards does this package target?**

A: `AcmeCertService` targets ACME v2 from RFC 8555, PKCS#10 CSRs from RFC 2986, and X.509 certificate parsing semantics from RFC 5280.

**Q: Does this package solve ACME challenges?**

A: No. DNS-01 or HTTP-01 challenge automation must be handled by the caller or surrounding infrastructure. This service focuses on CSR construction, ACME order submission/finalization, and certificate retrieval.

**Q: What key algorithms does it advertise?**

A: `supports()` reports RSA-2048, RSA-3072, EC-P256, and EC-P384 key support with RS256, ES256, and ES384 signature algorithms.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_acme`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/swarmauri_certs_acme/__init__.py) for the exact types and signatures involved.

### When

**Q: When should I use another certificate package?**

A: Use local or self-signed certificate packages for offline development and internal test chains. Use cloud, enterprise CA, or verification-specific packages when certificate issuance or validation is owned by another provider.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/swarmauri_certs_acme/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/pyproject.toml) provide the supporting context for `swarmauri_certs_acme`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_azure](https://pypi.org/project/swarmauri_certs_azure/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)
- [swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines the certificate-service interfaces and `KeyRef` types.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components used alongside certificate workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certs_acme`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_certs_acme` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certs_acme` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_acme` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_acme` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_acme` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_acme/NOTICE) for attribution.
<!-- readme-standards:end notices -->
