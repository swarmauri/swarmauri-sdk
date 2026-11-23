# swarmauri_certservice_stepca

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certservice_stepca</strong></p>
<p align="center">Asynchronous Swarmauri certificate service for smallstep step-ca CSR creation, one-time-token signing requests, and X.509 certificate parsing.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_stepca/"><img alt="pypi: swarmauri_certservice_stepca" src="https://img.shields.io/pypi/v/swarmauri_certservice_stepca"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certservice_stepca/"><img alt="Monthly PyPI downloads: swarmauri_certservice_stepca" src="https://img.shields.io/pypi/dm/swarmauri_certservice_stepca"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/README.md"><img alt="README hits: swarmauri_certservice_stepca" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_certservice_stepca/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_certservice_stepca` provides `StepCaCertService`, an asynchronous Swarmauri certificate service for [smallstep step-ca](https://smallstep.com/docs/step-ca). It creates PKCS#10 certificate signing requests, submits them to the step-ca `/1.0/sign` API with a one-time token, and returns PEM or DER certificate bytes for workload, device, service, and internal PKI enrollment.

### Why This Package

Use this package when a Swarmauri application needs step-ca certificate issuance without spreading CSR construction, token lookup, HTTP client handling, and certificate metadata parsing across application code. `StepCaCertService` keeps those operations behind the shared `CertServiceBase` interface so certificate automation can be composed with Swarmauri keys, verifiers, agents, and workflow components.

### When to Use

Choose `swarmauri_certservice_stepca` when your integration needs asynchronous Swarmauri certificate service for smallstep step-ca CSR creation, one-time-token signing requests, and X.509 certificate parsing. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `StepCaCertService` registered under the `swarmauri.cert_services` entry point.
- Async `httpx` client for step-ca `/1.0/sign` calls.
- CSR generation for RSA, EC, and Ed25519 private keys.
- Subject alternative names for DNS names, IP addresses, URIs, and email addresses.
- Challenge password, basic constraints, key usage, and extended key usage support.
- One-time-token handling through direct options or an async token provider.
- Optional provisioner, custom template data, extra request payload fields, and validity-window overrides.
- PEM response handling with optional DER conversion.
- Basic PEM and DER certificate verification and parsing helpers.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_certservice_stepca` owns asynchronous Swarmauri certificate service for smallstep step-ca CSR creation, one-time-token signing requests, and X.509 certificate parsing. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- A reachable step-ca instance exposing `/1.0/sign`.
- A provisioner configured for X.509 certificate signing.
- A one-time token for each signing request, or a token provider that can create or retrieve one.
- PEM private key material available through `KeyRef.material`.
- Trust configuration for the step-ca TLS endpoint when it uses a private root.

### Installation

Install with `uv`:

```bash
uv add swarmauri_certservice_stepca
```

Install with `pip`:

```bash
pip install swarmauri_certservice_stepca
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certservice_stepca
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certservice_stepca
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certservice_stepca
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/docs/readme/quick_start.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = StepCaCertService(
        ca_url="https://ca.example",
        provisioner="devices",
        verify_tls="/etc/ssl/step-ca-root.pem",
    )
    key_ref = KeyRef(material=Path("device.key.pem").read_bytes())

    csr = await service.create_csr(
        key_ref,
        {"O": "Example Corp", "CN": "device-001.example.com"},
        san={
            "dns": ["device-001.example.com"],
            "uri": ["spiffe://example/device-001"],
        },
    )
    cert = await service.sign_cert(
        csr,
        key_ref,
        opts={"ott": "step-ca-one-time-token"},
    )

    Path("device.crt").write_bytes(cert)
    await service.aclose()


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certservice_stepca` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/docs/readme/usage.py).

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = StepCaCertService(
        ca_url="https://ca.example",
        provisioner="devices",
        verify_tls="/etc/ssl/step-ca-root.pem",
    )
    key_ref = KeyRef(material=Path("device.key.pem").read_bytes())

    csr = await service.create_csr(
        key_ref,
        {"O": "Example Corp", "CN": "device-001.example.com"},
        san={
            "dns": ["device-001.example.com"],
            "uri": ["spiffe://example/device-001"],
        },
    )
    cert = await service.sign_cert(
        csr,
        key_ref,
        opts={"ott": "step-ca-one-time-token"},
    )

    Path("device.crt").write_bytes(cert)
    await service.aclose()


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Issue a certificate with an already issued one-time token:


Map CSR claims to a token provider:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService
from swarmauri_core.crypto.types import KeyRef


async def token_provider(claims: dict) -> str:
    common_name = claims["sub"]
    return Path(f"otts/{common_name}.txt").read_text().strip()


async def main() -> None:
    service = StepCaCertService(
        "https://ca.example",
        provisioner="workloads",
        token_provider=token_provider,
        timeout_s=10.0,
    )
    key_ref = KeyRef(material=Path("workload.key.pem").read_bytes())
    csr = await service.create_csr(key_ref, {"CN": "worker-17"})
    cert = await service.sign_cert(
        csr,
        key_ref,
        opts={"template_data": {"env": "prod", "role": "worker"}},
    )

    Path("worker-17.crt").write_bytes(cert)
    await service.aclose()


asyncio.run(main())
```

Parse certificate metadata:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService


async def main() -> None:
    service = StepCaCertService("https://ca.example")
    result = await service.verify_cert(Path("worker-17.crt").read_bytes())
    details = await service.parse_cert(Path("worker-17.crt").read_bytes())

    print(result["valid"])
    print(details["subject"])
    await service.aclose()


asyncio.run(main())
```

### Configuration

Configure `swarmauri_certservice_stepca` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/swarmauri_certservice_stepca/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certservice_stepca` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Retrieve one-time tokens just in time and avoid persisting them in source code or build logs.
- Use `verify_tls` with the step-ca root bundle when the CA is internal.
- Close the async client with `aclose()` after issuance bursts.
- Keep certificate issuance separate from revocation checking; pair this package with OCSP or CRL verification packages for lifecycle monitoring.

---

## Package Boundary

### What It Owns

`swarmauri_certservice_stepca` is located in `community` and owns asynchronous Swarmauri certificate service for smallstep step-ca CSR creation, one-time-token signing requests, and X.509 certificate parsing. Source-declared APIs include `StepCaCertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certservice_stepca`.

Source-declared exports or types: `StepCaCertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/swarmauri_certservice_stepca/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.cert_services` → `StepCaCertService` → `swarmauri_certservice_stepca.StepCaCertService:StepCaCertService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certservice_stepca` are `httpx`, `cryptography`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/swarmauri_certservice_stepca/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certservice_stepca` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certservice_stepca`, use the source-declared public interfaces (`StepCaCertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certservice_stepca` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certservice_stepca`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/swarmauri_certservice_stepca/__init__.py). The `swarmauri_certservice_stepca` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certservice_stepca` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certservice_stepca` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_stepca_sign_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/tests/i9n/test_stepca_sign_rfc5280.py)
- [tests/perf/test_stepca_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/tests/perf/test_stepca_perf.py)
- [tests/unit/test_stepca_rfc2986.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/tests/unit/test_stepca_rfc2986.py)
- [tests/unit/test_stepca_rfc5280.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/tests/unit/test_stepca_rfc5280.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certservice_stepca` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/swarmauri_certservice_stepca/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: What step-ca API does this package call?**

A: `sign_cert()` posts JSON to `/1.0/sign`, the step-ca certificate signing endpoint used for CSR-based X.509 issuance. The request includes the CSR and an authorization token supplied through `opts={"ott": "..."}` or a `token_provider`.

**Q: Does this package create one-time tokens?**

A: No. It consumes one-time tokens. Provide the token directly or pass an async `token_provider` that maps CSR claims to an issued token from your own step-ca, vault, identity, or provisioning layer.

**Q: Which certificate fields can create_csr() build?**

A: The CSR builder supports common X.509 subject attributes, DNS/IP/URI/email subject alternative names, challenge passwords, basic constraints, key usage, and extended key usage.

**Q: Does verify_cert() perform full PKI path validation?**

A: No. It loads PEM or DER certificates, checks the certificate validity window, and returns metadata. Use a dedicated verifier such as CRL or OCSP packages when you need revocation checks or chain policy enforcement.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certservice_stepca`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/swarmauri_certservice_stepca/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certservice_stepca` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/swarmauri_certservice_stepca/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/pyproject.toml) provide the supporting context for `swarmauri_certservice_stepca`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Certificate service packages:

- [swarmauri_certservice_scep](https://pypi.org/project/swarmauri_certservice_scep/)
- [swarmauri_certservice_ms_adcs](https://pypi.org/project/swarmauri_certservice_ms_adcs/)
- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)
- [swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri runtime components.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_certservice_stepca`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_certservice_stepca` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_certservice_stepca` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certservice_stepca` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certservice_stepca` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certservice_stepca` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_certservice_stepca/NOTICE) for attribution.
<!-- readme-standards:end notices -->
