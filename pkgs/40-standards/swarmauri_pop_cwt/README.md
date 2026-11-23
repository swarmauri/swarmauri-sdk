# swarmauri_pop_cwt

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_pop_cwt</strong></p>
<p align="center">COSE Sign1 proof-of-possession helpers for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_pop_cwt/"><img alt="pypi: swarmauri_pop_cwt" src="https://img.shields.io/pypi/v/swarmauri_pop_cwt?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml"><img alt="Source version: 0.11.0.dev5" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev5&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_pop_cwt/"><img alt="Monthly PyPI downloads: swarmauri_pop_cwt" src="https://img.shields.io/pypi/dm/swarmauri_pop_cwt?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/README.md"><img alt="README hits: swarmauri_pop_cwt" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_pop_cwt/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_pop_cwt` delivers COSE Sign1 proof-of-possession helpers that align with
RFC 8392 and RFC 9449. The signer and verifier share the same Swarmauri PoP
contract so services can mix CWT- and JWT-backed access tokens without changing
validation logic.

### Why This Package

`swarmauri_pop_cwt` isolates this responsibility: COSE Sign1 proof-of-possession helpers for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/swarmauri_pop_cwt/__init__.py) exposes `CwtPoPSigner`, `CwtPoPVerifier`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_pop_cwt` when your integration needs cOSE Sign1 proof-of-possession helpers for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Provides `CwtPoPSigner` and `CwtPoPVerifier` implementations that honour the
  shared Swarmauri PoP contract
- Accepts asynchronous key resolution hooks for COSE thumbprint matching and
  supports nonce/replay protections consistent with the DPoP workflow
- Generates `cnf` bindings that can be embedded into OAuth access tokens or
  session metadata to enable downstream verification
- Normalises HTTP request parts before signing or verifying to ensure
  interoperable coverage across services and languages

### Non-Goals

`swarmauri_pop_cwt` owns cOSE Sign1 proof-of-possession helpers for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cose`, `cbor2`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred tooling:

```bash
pip install swarmauri_pop_cwt
```

```bash
uv add swarmauri_pop_cwt
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_pop_cwt
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_pop_cwt
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_pop_cwt
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/docs/readme/quick_start.py).

```python
import base64
from cose.algorithms import SignatureAlg
from cose.keys import CoseKey
from swarmauri_pop_cwt import CwtPoPSigner

private_key = CoseKey.from_dict(
    {
        1: 1,  # OKP
        -1: 6,  # Ed25519
        -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g=="),
    }
)
public_key = CoseKey.from_dict(
    {
        1: 1,
        -1: 6,
        -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g=="),
    }
)

signer = CwtPoPSigner(
    private_key=private_key,
    public_key=public_key,
    algorithm=SignatureAlg.EdDSA,
)

cwp_header = signer.sign_request("GET", "https://api.example.com/resource")
print("CWP header:", cwp_header)
print("cnf:", signer.cnf_binding())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_pop_cwt` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/docs/readme/usage.py).

```python
import base64
from cose.algorithms import SignatureAlg
from cose.keys import CoseKey
from swarmauri_pop_cwt import CwtPoPSigner

private_key = CoseKey.from_dict(
    {
        1: 1,  # OKP
        -1: 6,  # Ed25519
        -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g=="),
    }
)
public_key = CoseKey.from_dict(
    {
        1: 1,
        -1: 6,
        -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g=="),
    }
)

signer = CwtPoPSigner(
    private_key=private_key,
    public_key=public_key,
    algorithm=SignatureAlg.EdDSA,
)

cwp_header = signer.sign_request("GET", "https://api.example.com/resource")
print("CWP header:", cwp_header)
print("cnf:", signer.cnf_binding())
```
<!-- readme-standards:end example.usage -->

**Signing an outgoing HTTP request**


**Verifying an incoming HTTP request**

```python
import asyncio
from cose.keys import CoseKey
from swarmauri_core.pop import CnfBinding, HttpParts, VerifyPolicy
from swarmauri_pop_cwt import CwtPoPVerifier


def memory_key_resolver(thumb: CnfBinding) -> CoseKey:
    return public_key


class ThumbResolver:
    def by_kid(self, kid: bytes):
        return None

    def by_thumb(self, bind: CnfBinding):
        return memory_key_resolver(bind)


async def verify_request(header: str, cnf: CnfBinding, access_token: str) -> None:
    verifier = CwtPoPVerifier()
    req = HttpParts(method="GET", url="https://api.example.com/resource", headers={"CWP": header})
    await verifier.verify_http(
        req,
        cnf,
        policy=VerifyPolicy(require_ath=True),
        keys=ThumbResolver(),
        extras={"access_token": access_token},
    )


asyncio.run(verify_request(cwp_header, signer.cnf_binding(), "opaque-access-token"))
```

The verifier enforces COSE key thumbprints against the `cnf` binding and applies
the same replay and nonce strategies shared across Swarmauri PoP strategies.

### Configuration

Configure `swarmauri_pop_cwt` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/swarmauri_pop_cwt/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_pop_cwt` source raises `PoPBindingError`, `PoPParseError`, `PoPVerificationError`, `TypeError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_pop_cwt` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CwtPoPSigner`, `CwtPoPVerifier`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_pop_cwt` is located in `standards` and owns cOSE Sign1 proof-of-possession helpers for Swarmauri. Source-declared APIs include `CwtPoPSigner`, `CwtPoPVerifier`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_pop_cwt`.

Source-declared exports or types: `CwtPoPSigner`, `CwtPoPVerifier`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/swarmauri_pop_cwt/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_pop_cwt` are `swarmauri-core`, `swarmauri-base`, `cose`, `cbor2`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/swarmauri_pop_cwt/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_pop_cwt` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_pop_cwt`, use the source-declared public interfaces (`CwtPoPSigner`, `CwtPoPVerifier`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_pop_cwt` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_pop_cwt`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/swarmauri_pop_cwt/__init__.py). The `swarmauri_pop_cwt` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

- Python 3.10, 3.11, and 3.12
- Works alongside the shared `swarmauri_core.pop` abstractions and any
  asynchronous framework that can supply an `HttpParts` payload
- Designed to operate with HTTP gateways that forward method, URL, and header
  information for downstream validation

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_pop_cwt` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_cwt.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/tests/test_cwt.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_pop_cwt` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/swarmauri_pop_cwt/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_pop_cwt` provides cOSE Sign1 proof-of-possession helpers for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_pop_cwt`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/swarmauri_pop_cwt/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_pop_cwt` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/swarmauri_pop_cwt/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml) provide the supporting context for `swarmauri_pop_cwt`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [`swarmauri_pop_dpop`](../swarmauri_pop_dpop) for JWT-based Demonstration of
  Proof-of-Possession headers
- [`swarmauri_pop_x509`](../swarmauri_pop_x509) when mutual TLS confirmation is
  required
- [`swarmauri_core`](../../10-interfaces/swarmauri_core) for the shared PoP contract, HTTP primitives,
  and error hierarchy leveraged by all PoP implementations

### Project Links

<!-- readme-standards:begin project-links -->
- [Changelog](https://github.com/swarmauri/swarmauri-sdk/releases)
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_pop_cwt)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_pop_cwt)
- [Issue Tracker](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Source](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_pop_cwt](https://pypi.org/project/swarmauri_pop_cwt/)
<!-- readme-standards:end project-links -->

If you encounter issues integrating Swarmauri PoP CWT flows, please open a
[GitHub issue](https://github.com/swarmauri/swarmauri-sdk/issues) with details
about your environment and the expected versus observed behaviour. Security
concerns should be responsibly disclosed via the contact details in the
repository security policy.

---

## Contributing

### How to Contribute

Contributions are welcome through the
[Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk). Follow
the project style guide, run the formatting and linting commands noted in the
root `AGENTS.md`, and open pull requests with focused commits that describe the
improvement.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_pop_cwt` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_pop_cwt` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_pop_cwt` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_pop_cwt` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_pop_cwt` source version is `0.11.0.dev5`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/LICENSE).
<!-- readme-standards:end license -->

Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_pop_cwt/NOTICE) for attribution.
<!-- readme-standards:end notices -->
