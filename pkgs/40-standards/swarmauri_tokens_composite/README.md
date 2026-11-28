# swarmauri_tokens_composite

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tokens_composite</strong></p>
<p align="center">Algorithm-routing token service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_composite/"><img alt="pypi: swarmauri_tokens_composite" src="https://img.shields.io/pypi/v/swarmauri_tokens_composite?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_composite/"><img alt="Monthly PyPI downloads: swarmauri_tokens_composite" src="https://img.shields.io/pypi/dm/swarmauri_tokens_composite?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/README.md"><img alt="README hits: swarmauri_tokens_composite" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tokens_composite/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tokens_composite`: Algorithm-routing token service for Swarmauri

### Why This Package

`swarmauri_tokens_composite` isolates this responsibility: Algorithm-routing token service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/swarmauri_tokens_composite/__init__.py) exposes `Any`, `CompositeTokenService`, `Dict`, `Iterable`, `List`, `Literal`, `Mapping`, `Optional`, `Tuple`, `annotations`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tokens_composite` when your integration needs algorithm-routing token service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Compose multiple asynchronous `ITokenService` implementations behind a single `CompositeTokenService` facade.
- Dispatch mint requests by explicit service hints (`headers["svc"]`), token type headers (`headers["typ"]`), confirmation claims (`claims["cnf"]`), or requested algorithms.
- Detect verification routes from SSH certificate prefixes, JWT-style tokens (including DPoP and mTLS-bound variants), or fall back through each service until one succeeds.
- Merge child capability metadata and JWKS responses, de-duplicating keys by `kid` so downstream clients can rely on a single aggregated feed.

### Non-Goals

`swarmauri_tokens_composite` owns algorithm-routing token service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_tokens_composite
```

```bash
poetry add swarmauri_tokens_composite
```

If you use [uv](https://docs.astral.sh/uv/), install it (skip the first line if uv is already available) and then add the package:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install swarmauri_tokens_composite
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tokens_composite
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tokens_composite
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tokens_composite
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/docs/readme/quick_start.py).

```python
# README Example: CompositeTokenService basic routing
import asyncio
from typing import Any, Dict, Iterable

from swarmauri_tokens_composite import CompositeTokenService


class MemoryTokenService:
    """In-memory stand-in for an async ITokenService implementation."""

    def __init__(
        self, type_name: str, formats: Iterable[str], algs: Iterable[str]
    ):
        self.type = type_name
        self._formats = tuple(formats)
        self._algs = tuple(algs)

    def supports(self) -> Dict[str, Iterable[str]]:
        return {"formats": self._formats, "algs": self._algs}

    async def mint(
        self, claims: Dict[str, Any], *, alg: str, headers=None, **_: Any
    ) -> str:
        return f"{self.type}:{alg}:{claims['sub']}"

    async def verify(self, token: str, **kwargs) -> Dict[str, Any]:
        svc, alg, sub = token.split(":", 2)
        if svc != self.type:
            raise ValueError("routed to wrong service")
        return {"sub": sub, "alg": alg, "service": svc}

    async def jwks(self) -> Dict[str, Any]:
        return {"keys": [{"kid": f"{self.type}-kid"}]}


def build_composite() -> CompositeTokenService:
    jwt_service = MemoryTokenService("JWTTokenService", ["JWT"], ["HS256"])
    ssh_service = MemoryTokenService(
        "SshCertTokenService", ["SSH-CERT"], ["ssh-ed25519"]
    )
    return CompositeTokenService([jwt_service, ssh_service])


def describe_example(result: Dict[str, Any]) -> None:
    print("JWT token:", result["jwt_token"])
    print("SSH token:", result["ssh_token"])
    print("JWT service handled mint/verify:", result["jwt_claims"]["service"])
    print("SSH service handled mint/verify:", result["ssh_claims"]["service"])
    print("JWKS keys:", {entry["kid"] for entry in result["jwks"]["keys"]})


async def main() -> Dict[str, Any]:
    composite = build_composite()

    jwt_token = await composite.mint({"sub": "alice"}, alg="HS256")
    ssh_token = await composite.mint({"sub": "bob"}, alg="ssh-ed25519")

    jwt_claims = await composite.verify(jwt_token)
    ssh_claims = await composite.verify(ssh_token)
    jwks = await composite.jwks()

    return {
        "jwt_token": jwt_token,
        "ssh_token": ssh_token,
        "jwt_claims": jwt_claims,
        "ssh_claims": ssh_claims,
        "jwks": jwks,
    }


example_result = asyncio.run(main())
describe_example(example_result)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tokens_composite` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/docs/readme/usage.py).

```python
# README Example: CompositeTokenService basic routing
import asyncio
from typing import Any, Dict, Iterable

from swarmauri_tokens_composite import CompositeTokenService


class MemoryTokenService:
    """In-memory stand-in for an async ITokenService implementation."""

    def __init__(
        self, type_name: str, formats: Iterable[str], algs: Iterable[str]
    ):
        self.type = type_name
        self._formats = tuple(formats)
        self._algs = tuple(algs)

    def supports(self) -> Dict[str, Iterable[str]]:
        return {"formats": self._formats, "algs": self._algs}

    async def mint(
        self, claims: Dict[str, Any], *, alg: str, headers=None, **_: Any
    ) -> str:
        return f"{self.type}:{alg}:{claims['sub']}"

    async def verify(self, token: str, **kwargs) -> Dict[str, Any]:
        svc, alg, sub = token.split(":", 2)
        if svc != self.type:
            raise ValueError("routed to wrong service")
        return {"sub": sub, "alg": alg, "service": svc}

    async def jwks(self) -> Dict[str, Any]:
        return {"keys": [{"kid": f"{self.type}-kid"}]}


def build_composite() -> CompositeTokenService:
    jwt_service = MemoryTokenService("JWTTokenService", ["JWT"], ["HS256"])
    ssh_service = MemoryTokenService(
        "SshCertTokenService", ["SSH-CERT"], ["ssh-ed25519"]
    )
    return CompositeTokenService([jwt_service, ssh_service])


def describe_example(result: Dict[str, Any]) -> None:
    print("JWT token:", result["jwt_token"])
    print("SSH token:", result["ssh_token"])
    print("JWT service handled mint/verify:", result["jwt_claims"]["service"])
    print("SSH service handled mint/verify:", result["ssh_claims"]["service"])
    print("JWKS keys:", {entry["kid"] for entry in result["jwks"]["keys"]})


async def main() -> Dict[str, Any]:
    composite = build_composite()

    jwt_token = await composite.mint({"sub": "alice"}, alg="HS256")
    ssh_token = await composite.mint({"sub": "bob"}, alg="ssh-ed25519")

    jwt_claims = await composite.verify(jwt_token)
    ssh_claims = await composite.verify(ssh_token)
    jwks = await composite.jwks()

    return {
        "jwt_token": jwt_token,
        "ssh_token": ssh_token,
        "jwt_claims": jwt_claims,
        "ssh_claims": ssh_claims,
        "jwks": jwks,
    }


example_result = asyncio.run(main())
describe_example(example_result)
```
<!-- readme-standards:end example.usage -->

`CompositeTokenService` accepts a list of services implementing `ITokenService`.  It inspects headers, claims, and requested algorithms to choose the most appropriate delegate for `mint`, `verify`, and `jwks` calls.  The child services remain responsible for the actual cryptographic work, while the composite aggregates their capabilities and keys.


The example above shows how the composite selects different child services by algorithm while producing a merged JWKS response.  In production you would supply concrete implementations that speak to HSMs, remote signing services, or other secure key stores.

### Configuration

Configure `swarmauri_tokens_composite` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/swarmauri_tokens_composite/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tokens_composite` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tokens_composite` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `Any`, `CompositeTokenService`, `Dict`, `Iterable`, `List`, `Literal`, `Mapping`, `Optional`, `Tuple`, `annotations`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tokens_composite` is located in `standards` and owns algorithm-routing token service for Swarmauri. Source-declared APIs include `Any`, `CompositeTokenService`, `Dict`, `Iterable`, `List`, `Literal`, `Mapping`, `Optional`, `Tuple`, `annotations`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tokens_composite`.

Source-declared exports or types: `Any`, `CompositeTokenService`, `Dict`, `Iterable`, `List`, `Literal`, `Mapping`, `Optional`, `Tuple`, `annotations`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/swarmauri_tokens_composite/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.tokens` → `composite` → `swarmauri_tokens_composite:CompositeTokenService`
- `swarmauri.tokens` → `CompositeTokenService` → `swarmauri_tokens_composite:CompositeTokenService`
<!-- readme-standards:end entry-points -->

The provider is registered under the `swarmauri.tokens` entry-point as `CompositeTokenService`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_tokens_composite` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/swarmauri_tokens_composite/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tokens_composite` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tokens_composite`, use the source-declared public interfaces (`Any`, `CompositeTokenService`, `Dict`, `Iterable`, `List`, `Literal`, `Mapping`, `Optional`, `Tuple`, `annotations`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tokens_composite` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tokens_composite`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/swarmauri_tokens_composite/__init__.py). The `swarmauri_tokens_composite` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tokens_composite` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tokens_composite` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_composite_token_service.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/tests/test_composite_token_service.py)
- [tests/test_functional_composite_token_service.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/tests/test_functional_composite_token_service.py)
- [tests/test_perf_composite_token_service.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/tests/test_perf_composite_token_service.py)
- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/tests/test_readme_example.py)
- [tests/test_rfc4253_ssh.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/tests/test_rfc4253_ssh.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tokens_composite` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/swarmauri_tokens_composite/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tokens_composite` provides algorithm-routing token service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tokens_composite`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/swarmauri_tokens_composite/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tokens_composite` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/swarmauri_tokens_composite/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml) provide the supporting context for `swarmauri_tokens_composite`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tokens_composite](https://pypi.org/project/swarmauri_tokens_composite/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tokens_composite` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Token Composite**

Algorithm-routing token service delegating to child providers based on JWT headers, claims, or algorithms.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tokens_composite` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tokens_composite` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tokens_composite` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_composite/NOTICE) for attribution.
<!-- readme-standards:end notices -->
