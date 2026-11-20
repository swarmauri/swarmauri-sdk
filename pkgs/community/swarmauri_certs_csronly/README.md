# swarmauri_certs_csronly

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_csronly</strong></p>
<p align="center">CSR-only Swarmauri certificate service for PKCS#10 request generation with SANs, challenge passwords, and PEM or DER output.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_csronly/"><img alt="pypi: swarmauri_certs_csronly" src="https://img.shields.io/pypi/v/swarmauri_certs_csronly"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_csronly/"><img alt="Monthly PyPI downloads: swarmauri_certs_csronly" src="https://img.shields.io/pypi/dm/swarmauri_certs_csronly"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/README.md"><img alt="README hits: swarmauri_certs_csronly" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_certs_csronly/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certs_csronly` provides `CsrOnlyService`, a focused Swarmauri certificate service for creating PKCS#10 certificate signing requests. It builds CSRs from PEM private key material in `KeyRef`, applies X.509 subject fields, optional subject alternative names, optional challenge passwords, and basic constraints, then returns PEM or DER CSR bytes.

### Why This Package

Use this package when certificate issuance is handled by another CA, but Swarmauri code still needs a standards-aligned CSR generator. It is useful for ACME, CFSSL, Azure, local CA, and enterprise PKI workflows where key generation and request construction are separated from certificate signing.

### When to Use

Choose `swarmauri_certs_csronly` when your integration needs cSR-only Swarmauri certificate service for PKCS#10 request generation with SANs, challenge passwords, and PEM or DER output. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `CsrOnlyService` class registered under the `swarmauri.certs` entry point.
- PKCS#10 CSR creation from PEM private keys stored in `KeyRef.material`.
- Subject support for CN, C, ST, L, O, OU, and emailAddress.
- Subject alternative name support for DNS names, IP addresses, URIs, and email addresses.
- Optional challenge password attribute support.
- Optional basic constraints extension support.
- PEM output by default with DER output available through `output_der=True`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certs_csronly` owns cSR-only Swarmauri certificate service for PKCS#10 request generation with SANs, challenge passwords, and PEM or DER output. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- PEM-encoded private key material available locally or through a `KeyRef` provider.
- Subject metadata for the certificate request.
- Optional SAN entries, basic constraints, and challenge passwords when required by the target CA.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certs_csronly
```

Install with `pip`:

```bash
pip install swarmauri_certs_csronly
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_csronly
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_csronly
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_csronly
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/docs/readme/quick_start.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = CsrOnlyService()
    key_ref = KeyRef(material=Path("example-key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "example.com", "O": "Example Inc"},
        san={"dns": ["example.com", "www.example.com"]},
    )
    Path("example.csr").write_bytes(csr)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_csronly` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/docs/readme/usage.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = CsrOnlyService()
    key_ref = KeyRef(material=Path("example-key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "example.com", "O": "Example Inc"},
        san={"dns": ["example.com", "www.example.com"]},
    )
    Path("example.csr").write_bytes(csr)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Generate a CSR for `example.com` with DNS SAN entries:


Create a DER-encoded CSR with a challenge password and basic constraints:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = CsrOnlyService()
    key_ref = KeyRef(material=Path("root-ca-key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "Example Root CA"},
        extensions={"basic_constraints": {"ca": True, "path_len": 0}},
        challenge_password="change-me",
        output_der=True,
    )
    Path("root-ca.csr.der").write_bytes(csr)


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certs_csronly` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/swarmauri_certs_csronly/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_csronly` source raises `NotImplementedError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Generate new key pairs and CSRs ahead of certificate expiry to allow review and approval time.
- Store private keys securely; `KeyRef` can reference hardware or cloud KMS backed material rather than local files.
- Keep SAN lists minimal and auditable to avoid overly broad certificate requests.
- Pair this service with a signing backend such as CFSSL, ACME, Azure, or a local CA package to form a complete issuance pipeline.

---

## Package Boundary

### What It Owns

`swarmauri_certs_csronly` is located in `community` and owns cSR-only Swarmauri certificate service for PKCS#10 request generation with SANs, challenge passwords, and PEM or DER output. Source-declared APIs include `CsrOnlyService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_csronly`.

Source-declared exports or types: `CsrOnlyService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/swarmauri_certs_csronly/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.certs` → `CsrOnlyService` → `swarmauri_certs_csronly:CsrOnlyService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_csronly` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/swarmauri_certs_csronly/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_csronly` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_csronly`, use the source-declared public interfaces (`CsrOnlyService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_csronly` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_csronly`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/swarmauri_certs_csronly/__init__.py). The `swarmauri_certs_csronly` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_csronly` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_csronly` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/certs/test_csronlyservice_rfc2986.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/tests/unit/certs/test_csronlyservice_rfc2986.py)
- [tests/unit/certs/test_csronlyservice_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/tests/unit/certs/test_csronlyservice_rfc5280.py)
- [tests/perf/certs/test_csronlyservice_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/tests/perf/certs/test_csronlyservice_perf.py)
- [tests/functional/certs/test_csronlyservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/tests/functional/certs/test_csronlyservice_functional.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_csronly` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/swarmauri_certs_csronly/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package issue certificates?**

A: No. `CsrOnlyService` does not create self-signed certificates, sign certificates, verify certificates, or parse certificates. Those methods intentionally raise `NotImplementedError`.

**Q: What key types does it support?**

A: `supports()` advertises RSA-2048, RSA-3072, RSA-4096, EC-P256, and Ed25519. Runtime signing uses `cryptography` private keys loaded from PEM bytes.

**Q: Which CSR features are implemented?**

A: CSR creation supports common subject fields, DNS/IP/URI/email SAN entries, PKCS#9 challenge password attributes, basic constraints, and DER or PEM output.

**Q: Which standards does it align with?**

A: The implementation targets PKCS#10 CSR generation from RFC 2986 and X.509 naming and extension semantics from RFC 5280.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_csronly`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/swarmauri_certs_csronly/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_csronly` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/swarmauri_certs_csronly/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/pyproject.toml) provide the supporting context for `swarmauri_certs_csronly`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_azure](https://pypi.org/project/swarmauri_certs_azure/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_csronly](https://pypi.org/project/swarmauri_certs_csronly/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certs_csronly`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_certs_csronly` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certs_csronly` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_csronly` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_csronly` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_csronly` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_certs_csronly/NOTICE) for attribution.
<!-- readme-standards:end notices -->
