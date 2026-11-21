# swarmauri_pop_dpop

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_pop_dpop</strong></p>
<p align="center">DPoP proof-of-possession tooling for Swarmauri services</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_pop_dpop/"><img alt="pypi: swarmauri_pop_dpop" src="https://img.shields.io/pypi/v/swarmauri_pop_dpop"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_pop_dpop/"><img alt="Monthly PyPI downloads: swarmauri_pop_dpop" src="https://img.shields.io/pypi/dm/swarmauri_pop_dpop"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/README.md"><img alt="README hits: swarmauri_pop_dpop" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_pop_dpop/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_pop_dpop` enables RFC 9449 Demonstrating Proof-of-Possession flows for
Swarmauri services. The signer and verifier reuse the shared Swarmauri PoP
contract so applications can mix DPoP, CWT, and X.509 strategies interchangeably.

### Why This Package

`swarmauri_pop_dpop` isolates this responsibility: DPoP proof-of-possession tooling for Swarmauri services. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/swarmauri_pop_dpop/__init__.py) exposes `DPoPSigner`, `DPoPVerifier`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_pop_dpop` when your integration needs dPoP proof-of-possession tooling for Swarmauri services. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Implements `DPoPSigner` and `DPoPVerifier` with consistent Swarmauri PoP
  semantics, including `cnf` generation and verification hooks
- Normalises HTTP method and URI handling to align with the DPoP
  specification, including support for query strings and ports
- Provides nonce and replay integration points so you can plug in
  application-specific storage to enforce single-use proofs
- Validates `ath` hashes for OAuth access tokens to ensure request binding when
  PoP is layered on bearer credentials

### Non-Goals

`swarmauri_pop_dpop` owns dPoP proof-of-possession tooling for Swarmauri services. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `pyjwt`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
pip install swarmauri_pop_dpop
```

```bash
uv add swarmauri_pop_dpop
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_pop_dpop
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_pop_dpop
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_pop_dpop
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/docs/readme/quick_start.py).

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

from swarmauri_pop_dpop import DPoPSigner

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

public_jwk = {
    "kty": "OKP",
    "crv": "Ed25519",
    "x": base64.urlsafe_b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )
    .rstrip(b"=")
    .decode("ascii"),
}

signer = DPoPSigner(
    private_key=private_key,
    public_jwk=public_jwk,
    algorithm="EdDSA",
)

dpop_header = signer.sign_request("GET", "https://api.example.com/resource")
print("DPoP header:", dpop_header)
print("cnf:", signer.cnf_binding())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_pop_dpop` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/docs/readme/usage.py).

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

from swarmauri_pop_dpop import DPoPSigner

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

public_jwk = {
    "kty": "OKP",
    "crv": "Ed25519",
    "x": base64.urlsafe_b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )
    .rstrip(b"=")
    .decode("ascii"),
}

signer = DPoPSigner(
    private_key=private_key,
    public_jwk=public_jwk,
    algorithm="EdDSA",
)

dpop_header = signer.sign_request("GET", "https://api.example.com/resource")
print("DPoP header:", dpop_header)
print("cnf:", signer.cnf_binding())
```
<!-- readme-standards:end example.usage -->

**Signing an outgoing HTTP request**


**Verifying an incoming HTTP request**

```python
import asyncio
from typing import Mapping

from swarmauri_core.pop import CnfBinding, HttpParts, VerifyPolicy
from swarmauri_pop_dpop import DPoPVerifier


class MemoryReplay:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def seen(self, scope: str, key: str) -> bool:
        return f"{scope}:{key}" in self._seen

    def mark(self, scope: str, key: str, ttl_s: int) -> None:
        self._seen.add(f"{scope}:{key}")


async def verify_request(headers: Mapping[str, str], cnf: CnfBinding, access_token: str) -> None:
    verifier = DPoPVerifier()
    req = HttpParts(method="GET", url="https://api.example.com/resource", headers=headers)
    await verifier.verify_http(
        req,
        cnf,
        policy=VerifyPolicy(require_ath=True),
        replay=MemoryReplay(),
        extras={"access_token": access_token},
    )


asyncio.run(verify_request({"DPoP": dpop_header}, signer.cnf_binding(), "opaque-access-token"))
```

The verifier enforces thumbprints for the provided JWK, checks nonce and replay
constraints, and validates `ath` hashes when bearer tokens are provided.

### Configuration

Configure `swarmauri_pop_dpop` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/swarmauri_pop_dpop/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_pop_dpop` source raises `PoPBindingError`, `PoPParseError`, `PoPVerificationError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_pop_dpop` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `DPoPSigner`, `DPoPVerifier`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_pop_dpop` is located in `standards` and owns dPoP proof-of-possession tooling for Swarmauri services. Source-declared APIs include `DPoPSigner`, `DPoPVerifier`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_pop_dpop`.

Source-declared exports or types: `DPoPSigner`, `DPoPVerifier`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/swarmauri_pop_dpop/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_pop_dpop` are `swarmauri-core`, `swarmauri-base`, `pyjwt`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/swarmauri_pop_dpop/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_pop_dpop` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_pop_dpop`, use the source-declared public interfaces (`DPoPSigner`, `DPoPVerifier`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_pop_dpop` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_pop_dpop`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/swarmauri_pop_dpop/__init__.py). The `swarmauri_pop_dpop` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

- Python 3.10, 3.11, and 3.12
- Asynchronous contexts that can dispatch `HttpParts` instances from
  `swarmauri_core`
- Intended for OAuth 2.0 servers, API gateways, and microservices that need to
  accept Demonstration of Proof-of-Possession headers

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_pop_dpop` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_dpop.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/tests/test_dpop.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_pop_dpop` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/swarmauri_pop_dpop/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_pop_dpop` provides dPoP proof-of-possession tooling for Swarmauri services; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_pop_dpop`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/swarmauri_pop_dpop/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_pop_dpop` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/swarmauri_pop_dpop/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml) provide the supporting context for `swarmauri_pop_dpop`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [`swarmauri_pop_cwt`](../swarmauri_pop_cwt) for COSE-based confirmation
- [`swarmauri_pop_x509`](../swarmauri_pop_x509) to validate mutual TLS
  thumbprints using the same `cnf` contract
- [`swarmauri_core`](../../core) which defines the PoP primitives consumed by all
  Swarmauri proof strategies

### Project Links

<!-- readme-standards:begin project-links -->
- [Changelog](https://github.com/swarmauri/swarmauri-sdk/releases)
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_dpop)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_dpop)
- [Issue Tracker](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Source](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_pop_dpop](https://pypi.org/project/swarmauri_pop_dpop/)
<!-- readme-standards:end project-links -->

Need help integrating DPoP in Swarmauri? File an
[issue on GitHub](https://github.com/swarmauri/swarmauri-sdk/issues) with
implementation details and reproduction steps. For security disclosures, use the
contact information listed in the repository security policy.

---

## Contributing

### How to Contribute

Please contribute improvements through the
[Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk). Ensure
tests, formatting, and linting match the root instructions and describe your
changes clearly in pull requests so reviewers understand the intended impact.

### Development Setup

Work from the `pkgs/standards/swarmauri_pop_dpop` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_pop_dpop` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_pop_dpop` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_pop_dpop` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_pop_dpop` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/LICENSE).
<!-- readme-standards:end license -->

Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_pop_dpop/NOTICE) for attribution.
<!-- readme-standards:end notices -->
