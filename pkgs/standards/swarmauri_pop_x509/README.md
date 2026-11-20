# swarmauri_pop_x509

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_pop_x509</strong></p>
<p align="center">X.509 mutual TLS proof-of-possession verifier for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_pop_x509/"><img alt="pypi: swarmauri_pop_x509" src="https://img.shields.io/pypi/v/swarmauri_pop_x509"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_pop_x509/"><img alt="Monthly PyPI downloads: swarmauri_pop_x509" src="https://img.shields.io/pypi/dm/swarmauri_pop_x509"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/README.md"><img alt="README hits: swarmauri_pop_x509" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_pop_x509/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_pop_x509` validates mutual TLS certificate bindings for Swarmauri PoP
workflows. It matches presented client certificates against access-token
confirmation claims so downstream components can trust mTLS-provided identities.

### Why This Package

`swarmauri_pop_x509` isolates this responsibility: X.509 mutual TLS proof-of-possession verifier for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/swarmauri_pop_x509/__init__.py) exposes `X509PoPVerifier`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_pop_x509` when your integration needs x.509 mutual TLS proof-of-possession verifier for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Implements `X509PoPVerifier` that matches SHA-256 thumbprints against `cnf`
  values for RFC 8705-style confirmation
- Reuses the shared Swarmauri PoP contract, allowing X.509 proofs to be
  interchanged with JWT- and COSE-based strategies
- Accepts asynchronous HTTP request parts and extra context so you can forward
  peer certificate material from proxies or API gateways
- Provides clear error messaging for missing certificates, mismatched thumbprints,
  or unsupported binding types

### Non-Goals

`swarmauri_pop_x509` owns x.509 mutual TLS proof-of-possession verifier for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
pip install swarmauri_pop_x509
```

```bash
uv add swarmauri_pop_x509
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_pop_x509
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_pop_x509
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_pop_x509
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/docs/readme/quick_start.py).

```python
import asyncio
import ssl
from swarmauri_core.pop import CnfBinding, HttpParts, VerifyPolicy, BindType
from swarmauri_pop_x509 import X509PoPVerifier


async def main() -> None:
    verifier = X509PoPVerifier()
    cnf = CnfBinding(BindType.X5T_S256, "<thumbprint-from-token>")
    request = HttpParts(
        method="GET", url="https://api.example.com/resource", headers={}
    )

    peer_cert_der = ssl.PEM_cert_to_DER_cert(
        open("client.pem", "r", encoding="utf-8").read()
    )

    await verifier.verify_http(
        request,
        cnf,
        policy=VerifyPolicy(),
        extras={"peer_cert_der": peer_cert_der},
    )


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_pop_x509` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/docs/readme/usage.py).

```python
import asyncio
import ssl
from swarmauri_core.pop import CnfBinding, HttpParts, VerifyPolicy, BindType
from swarmauri_pop_x509 import X509PoPVerifier


async def main() -> None:
    verifier = X509PoPVerifier()
    cnf = CnfBinding(BindType.X5T_S256, "<thumbprint-from-token>")
    request = HttpParts(
        method="GET", url="https://api.example.com/resource", headers={}
    )

    peer_cert_der = ssl.PEM_cert_to_DER_cert(
        open("client.pem", "r", encoding="utf-8").read()
    )

    await verifier.verify_http(
        request,
        cnf,
        policy=VerifyPolicy(),
        extras={"peer_cert_der": peer_cert_der},
    )


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The verifier consumes the normalised HTTP request alongside the `cnf` binding
from the access token. Provide the peer certificate in DER form via the
`extras` mapping when invoking `verify_http`.


`X509PoPVerifier` does not parse any detached proof artefact; the TLS handshake
supplies the evidence. Only the certificate thumbprint comparison is performed,
mirroring the behaviour of OAuth 2.0 mutual TLS confirmation.

### Configuration

Configure `swarmauri_pop_x509` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/swarmauri_pop_x509/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_pop_x509` source raises `PoPBindingError`, `PoPParseError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_pop_x509` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `X509PoPVerifier`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_pop_x509` is located in `standards` and owns x.509 mutual TLS proof-of-possession verifier for Swarmauri. Source-declared APIs include `X509PoPVerifier`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_pop_x509`.

Source-declared exports or types: `X509PoPVerifier`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/swarmauri_pop_x509/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_pop_x509` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/swarmauri_pop_x509/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_pop_x509` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_pop_x509`, use the source-declared public interfaces (`X509PoPVerifier`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_pop_x509` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_pop_x509`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/swarmauri_pop_x509/__init__.py). The `swarmauri_pop_x509` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

- Python 3.10, 3.11, and 3.12
- Works with TLS termination layers that can forward peer certificates into the
  verification context
- Built on the same asynchronous verification contract exposed by
  `swarmauri_core`

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_pop_x509` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_x509_verifier.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/tests/test_x509_verifier.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_pop_x509` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/swarmauri_pop_x509/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_pop_x509` provides x.509 mutual TLS proof-of-possession verifier for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_pop_x509`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/swarmauri_pop_x509/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_pop_x509` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/swarmauri_pop_x509/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml) provide the supporting context for `swarmauri_pop_x509`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [`swarmauri_pop_cwt`](../swarmauri_pop_cwt) for COSE Sign1 confirmation
- [`swarmauri_pop_dpop`](../swarmauri_pop_dpop) for Demonstrating Proof-of-
  Possession JWT headers
- [`swarmauri_core`](../../core) for the PoP abstractions and helpers that power
  all verification implementations

### Project Links

<!-- readme-standards:begin project-links -->
- [Changelog](https://github.com/swarmauri/swarmauri-sdk/releases)
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_x509)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_x509)
- [Issue Tracker](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Source](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_pop_x509](https://pypi.org/project/swarmauri_pop_x509/)
<!-- readme-standards:end project-links -->

For integration questions or bug reports, open an
[issue on GitHub](https://github.com/swarmauri/swarmauri-sdk/issues). Sensitive
security matters should follow the disclosure guidance referenced in the
repository security policy.

---

## Contributing

### How to Contribute

Changes and documentation updates should be proposed through the
[Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk). Run the
formatting, linting, and targeted tests outlined in the repository guides before
submitting pull requests.

### Development Setup

Work from the `pkgs/standards/swarmauri_pop_x509` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_pop_x509` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_pop_x509` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_pop_x509` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_pop_x509` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/LICENSE).
<!-- readme-standards:end license -->

Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_x509/NOTICE) for attribution.
<!-- readme-standards:end notices -->
