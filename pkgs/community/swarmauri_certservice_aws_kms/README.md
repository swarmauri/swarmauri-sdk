# swarmauri_certservice_aws_kms

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certservice_aws_kms</strong></p>
<p align="center">AWS KMS backed Swarmauri certificate service for CSR signing, self-signed roots, X.509 parsing, and certificate verification.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_aws_kms/"><img alt="pypi: swarmauri_certservice_aws_kms" src="https://img.shields.io/pypi/v/swarmauri_certservice_aws_kms"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_aws_kms/"><img alt="Monthly PyPI downloads: swarmauri_certservice_aws_kms" src="https://img.shields.io/pypi/dm/swarmauri_certservice_aws_kms"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/README.md"><img alt="README hits: swarmauri_certservice_aws_kms" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_certservice_aws_kms/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certservice_aws_kms` provides `AwsKmsCertService`, a Swarmauri certificate service that signs X.509 certificate structures with AWS Key Management Service. It creates CSRs from exportable PEM keys, signs incoming PKCS#10 CSRs through AWS KMS `Sign`, creates self-signed CA certificates with KMS-backed keys, verifies issued certificates against trusted issuers, and parses X.509 metadata.

### Why This Package

Use this package when certificate private keys should remain in AWS KMS while Swarmauri applications still need certificate issuance and verification workflows. The service maps Swarmauri `KeyRef` objects to AWS KMS KeyIds, supports KMS public-key retrieval, assembles X.509 certificates locally, and delegates signing operations to KMS.

### When to Use

Choose `swarmauri_certservice_aws_kms` when your integration needs aWS KMS backed Swarmauri certificate service for CSR signing, self-signed roots, X.509 parsing, and certificate verification. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `AwsKmsCertService` class registered under the `swarmauri.cert_services` entry point.
- AWS KMS client creation with optional region, endpoint URL, and boto3 session.
- CSR creation from exportable PEM private keys.
- CSR signing with KMS-backed issuer keys.
- Self-signed certificate creation with KMS-backed keys.
- KMS public-key retrieval for issuer SubjectPublicKeyInfo, SKID, and AKID.
- KeyId resolution from Swarmauri `KeyRef` fields.
- PEM and DER certificate output.
- X.509 certificate parsing for subject, issuer, serial, validity, SANs, key usage, EKU, and CA metadata.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certservice_aws_kms` owns aWS KMS backed Swarmauri certificate service for CSR signing, self-signed roots, X.509 parsing, and certificate verification. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- AWS credentials available to boto3 through environment variables, profiles, IAM role, or workload identity.
- AWS KMS keys that allow `kms:GetPublicKey` and `kms:Sign`.
- KMS key specs compatible with the selected signature algorithm.
- Exportable PEM private key material when using `create_csr()`.
- Issuer subject metadata or CA certificate bytes when signing CSRs.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certservice_aws_kms
```

Install with `pip`:

```bash
pip install swarmauri_certservice_aws_kms
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certservice_aws_kms
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certservice_aws_kms
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certservice_aws_kms
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/docs/readme/quick_start.py).

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")
    kms_key = KeyRef(
        kid="arn:aws:kms:us-east-1:123456789012:key/abcd-1234",
    )

    certificate = await service.sign_cert(
        csr=Path("tenant.csr").read_bytes(),
        ca_key=kms_key,
        issuer={"CN": "Example KMS Issuing CA", "O": "Example Corp"},
        not_after=int(
            (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
        ),
    )
    Path("tenant.pem").write_bytes(certificate)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certservice_aws_kms` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/docs/readme/usage.py).

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")
    kms_key = KeyRef(
        kid="arn:aws:kms:us-east-1:123456789012:key/abcd-1234",
    )

    certificate = await service.sign_cert(
        csr=Path("tenant.csr").read_bytes(),
        ca_key=kms_key,
        issuer={"CN": "Example KMS Issuing CA", "O": "Example Corp"},
        not_after=int(
            (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
        ),
    )
    Path("tenant.pem").write_bytes(certificate)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Sign an incoming CSR using a customer-managed AWS KMS key:


Create a CSR from exportable key material:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")
    csr = await service.create_csr(
        key=KeyRef(material=Path("intermediate-key.pem").read_bytes()),
        subject={"CN": "Example Intermediate CA", "O": "Example Corp"},
        san={"dns": ["intermediate.example.com"]},
    )
    Path("intermediate.csr").write_bytes(csr)


asyncio.run(main())
```

Create a self-signed root with a KMS-backed key:

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")
    kms_key = KeyRef(kid="arn:aws:kms:us-east-1:123456789012:key/root-ca-key")

    root = await service.create_self_signed(
        key=kms_key,
        subject={"CN": "Example Root CA", "O": "Example Corp"},
        not_after=int((datetime.now(timezone.utc) + timedelta(days=3650)).timestamp()),
    )
    Path("root-ca.pem").write_bytes(root)


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certservice_aws_kms` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/swarmauri_certservice_aws_kms/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certservice_aws_kms` source raises `NotImplementedError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Grant the KMS key limited permissions: `kms:GetPublicKey`, `kms:DescribeKey`, and `kms:Sign`.
- Store KMS key ARNs in `KeyRef.tags["aws_kms_key_id"]` or `KeyRef.kid` instead of scattering ARNs through application code.
- Coordinate certificate validity with KMS key rotation and renew certificates before rotating customer-managed keys.
- Cache parsed certificate metadata and issued certificates to reduce repeated KMS signing calls.

---

## Package Boundary

### What It Owns

`swarmauri_certservice_aws_kms` is located in `community` and owns aWS KMS backed Swarmauri certificate service for CSR signing, self-signed roots, X.509 parsing, and certificate verification. Source-declared APIs include `AwsKmsCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certservice_aws_kms`.

Source-declared exports or types: `AwsKmsCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/swarmauri_certservice_aws_kms/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.cert_services` → `AwsKmsCertService` → `swarmauri_certservice_aws_kms.AwsKmsCertService:AwsKmsCertService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certservice_aws_kms` are `boto3`, `asn1crypto`, `cryptography`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/swarmauri_certservice_aws_kms/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certservice_aws_kms` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certservice_aws_kms`, use the source-declared public interfaces (`AwsKmsCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certservice_aws_kms` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certservice_aws_kms`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/swarmauri_certservice_aws_kms/__init__.py). The `swarmauri_certservice_aws_kms` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certservice_aws_kms` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certservice_aws_kms` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_awskmscertservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/tests/functional/test_awskmscertservice_functional.py)
- [tests/perf/test_awskmscertservice_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/tests/perf/test_awskmscertservice_perf.py)
- [tests/unit/test_awskmscertservice_rfc2986.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/tests/unit/test_awskmscertservice_rfc2986.py)
- [tests/unit/test_awskmscertservice_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/tests/unit/test_awskmscertservice_rfc5280.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certservice_aws_kms` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/swarmauri_certservice_aws_kms/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does CSR creation use AWS KMS?**

A: No. `create_csr()` requires exportable private key material in `KeyRef.material`. AWS KMS is used for certificate signing and self-signed certificate signatures.

**Q: Which signature algorithms are supported?**

A: The service supports RSA-PSS-SHA256, RSA-SHA256, and ECDSA-P256-SHA256 mappings to AWS KMS signing algorithms.

**Q: Can it verify certificates?**

A: Yes. `verify_cert()` checks the validity window and, when an issuer certificate is provided through `intermediates` or `trust_roots`, verifies RSA PKCS#1, RSA-PSS, or ECDSA signatures with the issuer public key.

### How

**Q: How does the service find the AWS KMS key?**

A: `sign_cert()` and `create_self_signed()` resolve the KMS KeyId from `KeyRef.tags["aws_kms_key_id"]`, `KeyRef.tags["kms_key_id"]`, or `KeyRef.kid`.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certservice_aws_kms` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/swarmauri_certservice_aws_kms/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/pyproject.toml) provide the supporting context for `swarmauri_certservice_aws_kms`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certservice_gcpkms](https://pypi.org/project/swarmauri_certservice_gcpkms/)
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
- [pypi: swarmauri_certservice_aws_kms](https://pypi.org/project/swarmauri_certservice_aws_kms/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certservice_aws_kms`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_certservice_aws_kms` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certservice_aws_kms` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certservice_aws_kms` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certservice_aws_kms` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certservice_aws_kms` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certservice_aws_kms/NOTICE) for attribution.
<!-- readme-standards:end notices -->
