# swarmauri_certs_azure

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_azure</strong></p>
<p align="center">Azure Key Vault oriented Swarmauri certificate service for PKCS#10 CSR generation, PEM formatting, and certificate workflow helpers.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_azure/"><img alt="pypi: swarmauri_certs_azure" src="https://img.shields.io/pypi/v/swarmauri_certs_azure"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_azure/"><img alt="Monthly PyPI downloads: swarmauri_certs_azure" src="https://img.shields.io/pypi/dm/swarmauri_certs_azure"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/README.md"><img alt="README hits: swarmauri_certs_azure" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_certs_azure/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certs_azure` provides `AzureKeyVaultCertService`, a Swarmauri certificate-service adapter for Azure-oriented certificate workflows. The current implementation authenticates with Azure credentials, prepares an Azure Key Vault key client, and creates PKCS#10 certificate signing requests from exportable PEM private key material supplied through Swarmauri `KeyRef` objects.

### Why This Package

Use this package when a Swarmauri deployment needs certificate request generation that fits Azure Key Vault operational patterns. It gives certificate code one Swarmauri interface while preserving Azure authentication through `DefaultAzureCredential` and keeping CSR construction, RFC 5280 serial helpers, and RFC 7468 PEM formatting in a package-local certificate service.

### When to Use

Choose `swarmauri_certs_azure` when your integration needs azure Key Vault oriented Swarmauri certificate service for PKCS#10 CSR generation, PEM formatting, and certificate workflow helpers. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `AzureKeyVaultCertService` class for Swarmauri certificate-service workflows.
- Azure Identity integration through `DefaultAzureCredential` or a caller-provided credential.
- Azure Key Vault key client construction for the configured vault URL.
- PKCS#10 CSR creation from PEM private keys.
- Common-name subject handling for CSR generation.
- RFC 5280-oriented serial number helper.
- RFC 7468 PEM certificate formatting helper.
- Capability metadata reporting RSA-2048, RSA-SHA256, and CSR support.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certs_azure` owns azure Key Vault oriented Swarmauri certificate service for PKCS#10 CSR generation, PEM formatting, and certificate workflow helpers. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `azure-identity`, `azure-keyvault-keys`, `cryptography`, `asn1crypto`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certs_azure
```

Install with `pip`:

```bash
pip install swarmauri_certs_azure
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_azure
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_azure
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_azure
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/docs/readme/quick_start.py).

```python
from azure.identity import DefaultAzureCredential

from swarmauri_certs_azure.certs import AzureKeyVaultCertService

service = AzureKeyVaultCertService(
    "https://example-vault.vault.azure.net/",
    credential=DefaultAzureCredential(),
)

print(service.supports()["features"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_azure` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/docs/readme/usage.py).

```python
from azure.identity import DefaultAzureCredential

from swarmauri_certs_azure.certs import AzureKeyVaultCertService

service = AzureKeyVaultCertService(
    "https://example-vault.vault.azure.net/",
    credential=DefaultAzureCredential(),
)

print(service.supports()["features"])
```
<!-- readme-standards:end example.usage -->

Create a service for an Azure Key Vault URL:


Generate a CSR from local exportable key material:

```python
import asyncio
from pathlib import Path

from azure.identity import DefaultAzureCredential

from swarmauri_certs_azure.certs import AzureKeyVaultCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AzureKeyVaultCertService(
        "https://example-vault.vault.azure.net/",
        credential=DefaultAzureCredential(),
    )
    key_ref = KeyRef(material=Path("app-private-key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "app.example.com"},
    )
    Path("app.csr").write_bytes(csr)


asyncio.run(main())
```

Check helper behavior for PEM output:

```python
from swarmauri_certs_azure.certs.AzureKeyVaultCertService import _serial_or_random

serial = _serial_or_random(None)
assert 0 < serial < 2**128
```

### Configuration

Configure `swarmauri_certs_azure` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/swarmauri_certs_azure/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_azure` source raises `NotImplementedError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Prefer managed identities or workload identity federation over long-lived client secrets.
- Keep Key Vault permissions scoped to the minimum operations required by the surrounding workflow.
- Store generated CSRs and issued certificate chains in auditable storage.
- Use a dedicated cloud CA or Azure certificate workflow for issuance/import operations outside this package.

---

## Package Boundary

### What It Owns

`swarmauri_certs_azure` is located in `community` and owns azure Key Vault oriented Swarmauri certificate service for PKCS#10 CSR generation, PEM formatting, and certificate workflow helpers. Source-declared APIs include `AzureKeyVaultCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_azure`.

Source-declared exports or types: `AzureKeyVaultCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/swarmauri_certs_azure/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_azure` are `swarmauri-core`, `swarmauri-base`, `azure-identity`, `azure-keyvault-keys`, `cryptography`, `asn1crypto`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/swarmauri_certs_azure/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_azure` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_azure`, use the source-declared public interfaces (`AzureKeyVaultCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_azure` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_azure`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/swarmauri_certs_azure/__init__.py). The `swarmauri_certs_azure` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_azure` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_azure` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_rfc2986_csr.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/tests/test_rfc2986_csr.py)
- [tests/test_rfc5280_serial.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/tests/test_rfc5280_serial.py)
- [tests/test_rfc7468_pem.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/tests/test_rfc7468_pem.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_azure` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/swarmauri_certs_azure/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package create certificates directly in Azure Key Vault?**

A: Not in the current runtime implementation. It creates CSRs from exportable private key material and prepares an Azure Key Vault key client. Azure certificate creation, import, and lifecycle operations should be handled by the surrounding Azure workflow.

**Q: What standards does it cover?**

A: The package includes PKCS#10 CSR creation, RFC 5280-style serial number generation helpers, and RFC 7468 PEM certificate formatting helpers.

**Q: What credential model does it use?**

A: `AzureKeyVaultCertService` uses a caller-provided Azure credential or falls back to `DefaultAzureCredential`, which supports local developer login, managed identity, workload identity, and service-principal flows supported by Azure Identity.

**Q: What key material is required?**

A: The implemented CSR path requires exportable PEM private key material in `KeyRef.material`. Non-exportable Key Vault signing is not implemented by this simplified service.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_azure`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/swarmauri_certs_azure/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_azure` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/swarmauri_certs_azure/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml) provide the supporting context for `swarmauri_certs_azure`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)
- [swarmauri_certservice_aws_kms](https://pypi.org/project/swarmauri_certservice_aws_kms/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_azure](https://pypi.org/project/swarmauri_certs_azure/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certs_azure`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_certs_azure` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certs_azure` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_azure` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_azure` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_azure` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certs_azure/NOTICE) for attribution.
<!-- readme-standards:end notices -->
