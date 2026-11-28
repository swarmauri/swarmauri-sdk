# swarmauri_keyprovider_remote_jwks

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyprovider_remote_jwks</strong></p>
<p align="center">Remote JWKS-backed key provider for verification-only use</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_remote_jwks/"><img alt="pypi: swarmauri_keyprovider_remote_jwks" src="https://img.shields.io/pypi/v/swarmauri_keyprovider_remote_jwks?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_remote_jwks/"><img alt="Monthly PyPI downloads: swarmauri_keyprovider_remote_jwks" src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_remote_jwks?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/README.md"><img alt="README hits: swarmauri_keyprovider_remote_jwks" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Key provider backed by a remote JWKS endpoint with local key management.

### Why This Package

`swarmauri_keyprovider_remote_jwks` isolates this responsibility: Remote JWKS-backed key provider for verification-only use. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/swarmauri_keyprovider_remote_jwks/__init__.py) exposes `RemoteJwksKeyProvider`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_keyprovider_remote_jwks` when your integration needs remote JWKS-backed key provider for verification-only use. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Accepts either a direct JWKS URL or an OpenID Connect issuer and resolves the
  discovery document automatically.
- Caches the remote JWKS in memory with TTL support, conditional requests, and
  thread-safe refreshes through `refresh(force=True)`.
- Supports versioned key identifiers such as `kid.version` when discovering
  remote public keys.
- Embeds the standard `LocalKeyProvider` so that services can create, rotate,
  import, and destroy local keys without leaving memory.
- Exposes convenience helpers like `random_bytes()` and `hkdf()` for local
  cryptographic operations alongside the remote verification flow.

### Non-Goals

`swarmauri_keyprovider_remote_jwks` owns remote JWKS-backed key provider for verification-only use. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-local`, `cryptography`, `pydantic`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_keyprovider_remote_jwks
```

```bash
poetry add swarmauri_keyprovider_remote_jwks
```

```bash
uv pip install swarmauri_keyprovider_remote_jwks
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyprovider_remote_jwks
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyprovider_remote_jwks
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyprovider_remote_jwks
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/docs/readme/quick_start.py).

```python
import asyncio
from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider


async def main() -> None:
    provider = RemoteJwksKeyProvider(
        jwks_url="https://example.com/.well-known/jwks.json"
    )

    # Optional: pre-fetch the JWKS; otherwise the first key lookup triggers it
    provider.refresh(force=True)

    jwk = await provider.get_public_jwk("test", version=1)
    print(jwk)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyprovider_remote_jwks` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/docs/readme/usage.py).

```python
import asyncio
from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider


async def main() -> None:
    provider = RemoteJwksKeyProvider(
        jwks_url="https://example.com/.well-known/jwks.json"
    )

    # Optional: pre-fetch the JWKS; otherwise the first key lookup triggers it
    provider.refresh(force=True)

    jwk = await provider.get_public_jwk("test", version=1)
    print(jwk)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The provider fetches verification keys from a remote JWKS URL or through an
OpenID Connect (OIDC) issuer.  It also embeds an in-memory key provider to
create and manage local keys.  The example below fetches a JWK from a JWKS
endpoint and prints its public fields:


You can also construct the provider from an OIDC issuer.  The provider resolves
the issuer's discovery document to find the JWKS URL:

```python
RemoteJwksKeyProvider(issuer="https://issuer.example.com")
```

Locally created keys are available via the standard key provider APIs and are
included alongside remote keys when calling `jwks()`.

**Local vs remote keys**

Remote keys and locally created keys serve different purposes:

- **Remote keys** are read-only public keys discovered from the JWKS endpoint.
  They normally belong to an external identity provider and are used only for
  verification. The provider never has access to their private material.
- **Local keys** are generated by the embedded `LocalKeyProvider`. They include
  secret material (when permitted by the `ExportPolicy`) and can be used for
  signing, encryption, or key agreement. These keys live only in memory unless
  you export them.

The following examples illustrate both flows.

**Working with remote keys**

```python
import asyncio
import jwt
from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider


async def main() -> None:
    provider = RemoteJwksKeyProvider(
        jwks_url="https://example.com/.well-known/jwks.json",
    )

    # Fetch a remote public key
    jwk = await provider.get_public_jwk("remote-kid")
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

    token = "..."  # JWT issued by the remote service
    payload = jwt.decode(token, public_key, algorithms=["RS256"], audience="api")
    print(payload)


asyncio.run(main())
```

**Managing local keys**

Local keys can be created, rotated, and destroyed without network calls. They are
ideal when your service needs to issue tokens or perform encryption.

The snippet below signs and verifies a JWT using an HMAC key that never leaves
memory:

```python
import asyncio
import jwt
from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyClass, KeyAlg, ExportPolicy
from swarmauri_core.crypto.types import KeyUse


async def main() -> None:
    provider = RemoteJwksKeyProvider(
        jwks_url="https://example.com/.well-known/jwks.json",
    )

    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.HMAC_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    key = await provider.create_key(spec)
    ref = await provider.get_key(key.kid, include_secret=True)

    token = jwt.encode({"sub": "123"}, ref.material, algorithm="HS256")
    decoded = jwt.decode(token, ref.material, algorithms=["HS256"])
    print(decoded)


asyncio.run(main())
```

Locally generated keys appear next to remote keys when exporting a JWKS:

```python
jwks = await provider.jwks()
print(jwks)
```

**Refreshing remote keys**

Remote keys are cached for `cache_ttl_s` seconds. Call `refresh(force=True)` to
fetch the latest JWKS before a latency-sensitive operation:

```python
provider = RemoteJwksKeyProvider(
    jwks_url="https://example.com/.well-known/jwks.json",
    cache_ttl_s=60,            # default: 300 seconds
    request_timeout_s=2,       # default: 5 seconds
    user_agent="MyGateway/1.0",
)

# Block until the JWKS has been refreshed
provider.refresh(force=True)
```

### Configuration

Configure `swarmauri_keyprovider_remote_jwks` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/swarmauri_keyprovider_remote_jwks/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyprovider_remote_jwks` source raises `KeyError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_keyprovider_remote_jwks` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `RemoteJwksKeyProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_keyprovider_remote_jwks` is located in `standards` and owns remote JWKS-backed key provider for verification-only use. Source-declared APIs include `RemoteJwksKeyProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyprovider_remote_jwks`.

Source-declared exports or types: `RemoteJwksKeyProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/swarmauri_keyprovider_remote_jwks/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.key_providers` → `remote_jwks` → `swarmauri_keyprovider_remote_jwks.RemoteJwksKeyProvider:RemoteJwksKeyProvider`
- `swarmauri.key_providers` → `RemoteJwksKeyProvider` → `swarmauri_keyprovider_remote_jwks.RemoteJwksKeyProvider:RemoteJwksKeyProvider`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyprovider_remote_jwks` are `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-local`, `cryptography`, `pydantic`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/swarmauri_keyprovider_remote_jwks/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_keyprovider_remote_jwks` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_keyprovider_remote_jwks`, use the source-declared public interfaces (`RemoteJwksKeyProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyprovider_remote_jwks` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyprovider_remote_jwks`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/swarmauri_keyprovider_remote_jwks/__init__.py). The `swarmauri_keyprovider_remote_jwks` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyprovider_remote_jwks` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyprovider_remote_jwks` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_remote_jwks_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/tests/test_remote_jwks_functional.py)
- [tests/test_remote_jwks_performance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/tests/test_remote_jwks_performance.py)
- [tests/test_remote_jwks_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/tests/test_remote_jwks_unit.py)
- [tests/test_rfc7517_jwks_compliance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/tests/test_rfc7517_jwks_compliance.py)
- [tests/test_rfc8414_oidc_discovery.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/tests/test_rfc8414_oidc_discovery.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyprovider_remote_jwks` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/swarmauri_keyprovider_remote_jwks/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_keyprovider_remote_jwks` provides remote JWKS-backed key provider for verification-only use; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_keyprovider_remote_jwks`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/swarmauri_keyprovider_remote_jwks/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyprovider_remote_jwks` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/swarmauri_keyprovider_remote_jwks/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml) provide the supporting context for `swarmauri_keyprovider_remote_jwks`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_keyprovider_local](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_local/README.md): In-memory key provider for development and testing

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_keyprovider_remote_jwks](https://pypi.org/project/swarmauri_keyprovider_remote_jwks/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_keyprovider_remote_jwks` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_keyprovider_remote_jwks` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyprovider_remote_jwks` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyprovider_remote_jwks` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyprovider_remote_jwks` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_remote_jwks/NOTICE) for attribution.
<!-- readme-standards:end notices -->
