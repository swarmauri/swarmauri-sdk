# swarmauri_certservice_gcpkms

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certservice_gcpkms</strong></p>
<p align="center">Google Cloud KMS oriented Swarmauri certificate service for CSR creation, CSR signing, self-signed certificates, verification, and X.509 parsing.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_gcpkms/"><img alt="pypi: swarmauri_certservice_gcpkms" src="https://img.shields.io/pypi/v/swarmauri_certservice_gcpkms?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_gcpkms/"><img alt="Monthly PyPI downloads: swarmauri_certservice_gcpkms" src="https://img.shields.io/pypi/dm/swarmauri_certservice_gcpkms?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/README.md"><img alt="README hits: swarmauri_certservice_gcpkms" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_certservice_gcpkms/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certservice_gcpkms` provides `GcpKmsCertService`, a Swarmauri certificate service for Google Cloud KMS oriented certificate workflows. It creates CSRs, creates self-signed certificates, signs CSRs, verifies certificate validity and signatures, and parses X.509 metadata while resolving signing keys from Google Cloud KMS key-version references.

### Why This Package

Use this package when Swarmauri certificate workflows need to integrate with Google Cloud KMS key versions while preserving the common `CertServiceBase` interface. The service accepts a caller-provided KMS client or creates `KeyManagementServiceClient`, resolves key versions from `KeyRef`, and uses `cryptography` certificate builders for X.509 output.

### When to Use

Choose `swarmauri_certservice_gcpkms` when your integration needs google Cloud KMS oriented Swarmauri certificate service for CSR creation, CSR signing, self-signed certificates, verification, and X.509 parsing. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `GcpKmsCertService` class registered under the `swarmauri.cert_services` entry point.
- Optional Google Cloud KMS client creation through `google-cloud-kms`.
- Caller-provided client support for tests and custom runtimes.
- Key-version resolution from Swarmauri `KeyRef`.
- CSR creation with subject and DNS/IP SAN support.
- Self-signed certificate creation with KMS-backed private-key adapter.
- CSR signing with issuer metadata and optional extensions.
- Certificate verification against validity window and optional trust root.
- Certificate parsing for version, serial, signature algorithm, issuer, subject, validity, and CA status.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certservice_gcpkms` owns google Cloud KMS oriented Swarmauri certificate service for CSR creation, CSR signing, self-signed certificates, verification, and X.509 parsing. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Google Cloud project with the Cloud KMS API enabled.
- Application credentials available to Google client libraries.
- KMS key versions with asymmetric signing capability.
- `google-cloud-kms` installed through the `gcp` extra when using the default client.
- A runtime adapter for `_make_kms_private_key` when using live KMS signing.

### Installation

Install with `uv`:

```bash
uv add "swarmauri_certservice_gcpkms[gcp]"
```

Install with `pip`:

```bash
pip install "swarmauri_certservice_gcpkms[gcp]"
```

Install the package without the Google Cloud client when injecting a test or custom client:

```bash
uv add swarmauri_certservice_gcpkms
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certservice_gcpkms
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certservice_gcpkms
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certservice_gcpkms
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/docs/readme/quick_start.py).

```python
from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef

service = GcpKmsCertService()
key = KeyRef(
    kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/root/cryptoKeyVersions/1"
)

print(service.supports()["features"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certservice_gcpkms` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/docs/readme/usage.py).

```python
from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef

service = GcpKmsCertService()
key = KeyRef(
    kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/root/cryptoKeyVersions/1"
)

print(service.supports()["features"])
```
<!-- readme-standards:end example.usage -->

Create a service and resolve a KMS key version from `KeyRef`:


Generate a CSR:

```python
import asyncio

from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = GcpKmsCertService()
    key = KeyRef(
        kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/leaf/cryptoKeyVersions/1"
    )

    csr = await service.create_csr(
        key=key,
        subject={"CN": "leaf.example.com", "O": "Example Corp"},
        san={"dns": ["leaf.example.com"]},
    )
    print(csr[:40])


asyncio.run(main())
```

Sign a CSR after providing a KMS-compatible signing adapter:

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = GcpKmsCertService()
    ca_key = KeyRef(
        kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/issuing-ca/cryptoKeyVersions/1"
    )

    certificate = await service.sign_cert(
        csr=Path("leaf.csr").read_bytes(),
        ca_key=ca_key,
        issuer={"CN": "Example GCP Issuing CA", "O": "Example Corp"},
        not_after=int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),
    )
    Path("leaf.pem").write_bytes(certificate)


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certservice_gcpkms` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/swarmauri_certservice_gcpkms/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certservice_gcpkms` source raises `ImportError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use least-privilege IAM roles for Cloud KMS signing operations.
- Store fully qualified key-version names in `KeyRef.kid` or `KeyRef.tags`.
- Validate that the signing adapter matches the KMS key algorithm before issuing certificates.
- Log certificate serials, issuer metadata, and key-version references for auditability.

---

## Package Boundary

### What It Owns

`swarmauri_certservice_gcpkms` is located in `community` and owns google Cloud KMS oriented Swarmauri certificate service for CSR creation, CSR signing, self-signed certificates, verification, and X.509 parsing. Source-declared APIs include `GcpKmsCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certservice_gcpkms`.

Source-declared exports or types: `GcpKmsCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/swarmauri_certservice_gcpkms/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.cert_services` → `GcpKmsCertService` → `swarmauri_certservice_gcpkms.GcpKmsCertService:GcpKmsCertService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certservice_gcpkms` are `cryptography`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/swarmauri_certservice_gcpkms/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certservice_gcpkms` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certservice_gcpkms`, use the source-declared public interfaces (`GcpKmsCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certservice_gcpkms` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certservice_gcpkms`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/swarmauri_certservice_gcpkms/__init__.py). The `swarmauri_certservice_gcpkms` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certservice_gcpkms` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certservice_gcpkms` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_functional_service.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/tests/test_functional_service.py)
- [tests/test_perf_service.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/tests/test_perf_service.py)
- [tests/test_rfc2986_csr.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/tests/test_rfc2986_csr.py)
- [tests/test_rfc5280_basic_constraints.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/tests/test_rfc5280_basic_constraints.py)
- [tests/test_unit_service.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/tests/test_unit_service.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certservice_gcpkms` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/swarmauri_certservice_gcpkms/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package install Google Cloud KMS by default?**

A: No. The base package keeps Google Cloud KMS optional. Install `swarmauri_certservice_gcpkms[gcp]` when the runtime should create a real `KeyManagementServiceClient`.

**Q: What is the current KMS signing boundary?**

A: Certificate operations use an internal `_make_kms_private_key(client, version)` hook to obtain a `cryptography`-compatible private-key object. Tests can patch this hook; production use should provide or extend that adapter for the selected Google Cloud KMS signing flow.

**Q: What certificate operations are implemented?**

A: The service implements CSR creation, self-signed certificate creation, CSR signing, signature and validity-window verification, and certificate metadata parsing.

### How

**Q: How does the service find the Google Cloud KMS key version?**

A: Key versions are resolved from `KeyRef.tags["gcp_kms_key_version"]`, `KeyRef.tags["kms_key_version"]`, or `KeyRef.kid`.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certservice_gcpkms` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/swarmauri_certservice_gcpkms/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/pyproject.toml) provide the supporting context for `swarmauri_certservice_gcpkms`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certservice_aws_kms](https://pypi.org/project/swarmauri_certservice_aws_kms/)
- [swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)
- [swarmauri_certs_azure](https://pypi.org/project/swarmauri_certs_azure/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase` and component registration.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components for certificate-adjacent workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certservice_gcpkms](https://pypi.org/project/swarmauri_certservice_gcpkms/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certservice_gcpkms`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_certservice_gcpkms` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certservice_gcpkms` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certservice_gcpkms` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certservice_gcpkms` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certservice_gcpkms` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_gcpkms/NOTICE) for attribution.
<!-- readme-standards:end notices -->
