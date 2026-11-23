# swarmauri_certservice_scep

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certservice_scep</strong></p>
<p align="center">SCEP-oriented Swarmauri certificate service for PKCS#10 CSR creation, challenge-password enrollment requests, response capture, and X.509 parsing.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_scep/"><img alt="pypi: swarmauri_certservice_scep" src="https://img.shields.io/pypi/v/swarmauri_certservice_scep?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_scep/"><img alt="Monthly PyPI downloads: swarmauri_certservice_scep" src="https://img.shields.io/pypi/dm/swarmauri_certservice_scep?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/README.md"><img alt="README hits: swarmauri_certservice_scep" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_certservice_scep/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certservice_scep` provides `ScepCertService`, a Swarmauri certificate service for Simple Certificate Enrollment Protocol style workflows. The implemented service creates PKCS#10 CSRs, optionally embeds a challenge password, posts CSR bytes to a SCEP `PKIOperation` endpoint, and parses returned X.509 certificate metadata.

### Why This Package

Use this package when Swarmauri applications need a small SCEP-oriented enrollment adapter without embedding enrollment URL construction and CSR creation in application code. It keeps CSR generation, challenge-password handling, SCEP endpoint submission, and certificate metadata extraction behind `CertServiceBase`.

### When to Use

Choose `swarmauri_certservice_scep` when your integration needs sCEP-oriented Swarmauri certificate service for PKCS#10 CSR creation, challenge-password enrollment requests, response capture, and X.509 parsing. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `ScepCertService` class registered under the `swarmauri.cert_services` entry point.
- PKCS#10 CSR creation from PEM private keys in `KeyRef.material`.
- DNS subject alternative name support.
- Challenge password support through the constructor or per-call argument.
- SCEP `PKIOperation` HTTP submission through `httpx`.
- PEM and DER certificate loading for verification and parsing.
- Basic certificate metadata extraction for issuer, subject, serial, validity, and CA status.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certservice_scep` owns sCEP-oriented Swarmauri certificate service for PKCS#10 CSR creation, challenge-password enrollment requests, response capture, and X.509 parsing. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Reachable SCEP endpoint such as `https://mdm.example.com/scep`.
- PEM private key material for each device, service, or workload enrolling.
- RA challenge password when required by the SCEP service.
- Additional CMS/PKCS#7 handling in the caller when required by the SCEP responder.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certservice_scep
```

Install with `pip`:

```bash
pip install swarmauri_certservice_scep
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certservice_scep
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certservice_scep
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certservice_scep
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/docs/readme/quick_start.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = ScepCertService(
        "https://scep.example.test",
        challenge_password="enroll-secret",
    )
    key_ref = KeyRef(material=Path("device.key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "device-001.example.com"},
        san={"dns": ["device-001.example.com", "device-001"]},
    )
    Path("device.csr").write_bytes(csr)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certservice_scep` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/docs/readme/usage.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = ScepCertService(
        "https://scep.example.test",
        challenge_password="enroll-secret",
    )
    key_ref = KeyRef(material=Path("device.key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "device-001.example.com"},
        san={"dns": ["device-001.example.com", "device-001"]},
    )
    Path("device.csr").write_bytes(csr)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Create a CSR with a challenge password:


Submit a CSR to a SCEP endpoint:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = ScepCertService("https://scep.example.test")
    response_bytes = await service.sign_cert(
        Path("device.csr").read_bytes(),
        ca_key=KeyRef(kid="scep-ca"),
    )
    Path("device-response.bin").write_bytes(response_bytes)


asyncio.run(main())
```

Parse a returned certificate:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService


async def main() -> None:
    service = ScepCertService("https://scep.example.test")
    details = await service.parse_cert(Path("device.pem").read_bytes())

    print("Serial:", details["serial"])
    print("Subject:", details["subject"])


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certservice_scep` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/swarmauri_certservice_scep/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certservice_scep` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Store challenge passwords and enrollment secrets in a secure vault.
- Treat SCEP responses as opaque until decoded by a response parser appropriate for your responder.
- Generate distinct key pairs per device or workload.
- Pair SCEP enrollment with CRL or OCSP verification packages for lifecycle monitoring.

---

## Package Boundary

### What It Owns

`swarmauri_certservice_scep` is located in `community` and owns sCEP-oriented Swarmauri certificate service for PKCS#10 CSR creation, challenge-password enrollment requests, response capture, and X.509 parsing. Source-declared APIs include `ScepCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certservice_scep`.

Source-declared exports or types: `ScepCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/swarmauri_certservice_scep/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.cert_services` → `ScepCertService` → `swarmauri_certservice_scep.ScepCertService:ScepCertService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certservice_scep` are `httpx`, `cryptography`, `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/swarmauri_certservice_scep/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certservice_scep` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certservice_scep`, use the source-declared public interfaces (`ScepCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certservice_scep` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certservice_scep`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/swarmauri_certservice_scep/__init__.py). The `swarmauri_certservice_scep` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certservice_scep` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certservice_scep` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_scepcertservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/tests/functional/test_scepcertservice_functional.py)
- [tests/perf/test_scepcertservice_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/tests/perf/test_scepcertservice_perf.py)
- [tests/unit/test_scepcertservice_rfc2986.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/tests/unit/test_scepcertservice_rfc2986.py)
- [tests/unit/test_scepcertservice_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/tests/unit/test_scepcertservice_rfc5280.py)
- [tests/unit/test_scepcertservice_rfc8894.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/tests/unit/test_scepcertservice_rfc8894.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certservice_scep` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/swarmauri_certservice_scep/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package build complete CMS or PKCS#7 SCEP envelopes?**

A: No. The current implementation posts CSR bytes directly to `pkiclient.exe?operation=PKIOperation` and returns the responder content. If your responder requires full SCEP CMS wrapping or PKCS#7 response extraction, handle that in the surrounding enrollment layer.

**Q: What CSR fields are supported?**

A: `create_csr()` currently builds a CSR with the common name from `subject["CN"]`, DNS SAN entries, and a challenge password from the call or service constructor.

**Q: What does verify_cert() check?**

A: The current verifier loads PEM or DER certificates and returns issuer, subject, serial, validity timestamps, and CA status. It does not perform chain validation or revocation checking.

**Q: Which standards does the package document?**

A: The service docstring references SCEP from RFC 8894, PKCS#10 CSR creation from RFC 2986, and X.509 certificate metadata from RFC 5280.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certservice_scep`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/swarmauri_certservice_scep/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certservice_scep` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/swarmauri_certservice_scep/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/pyproject.toml) provide the supporting context for `swarmauri_certservice_scep`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certservice_ms_adcs](https://pypi.org/project/swarmauri_certservice_ms_adcs/)
- [swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)
- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
- [swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certservice_scep](https://pypi.org/project/swarmauri_certservice_scep/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certservice_scep`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_certservice_scep` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certservice_scep` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certservice_scep` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certservice_scep` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certservice_scep` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_scep/NOTICE) for attribution.
<!-- readme-standards:end notices -->
