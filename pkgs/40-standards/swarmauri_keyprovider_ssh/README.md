# swarmauri_keyprovider_ssh

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyprovider_ssh</strong></p>
<p align="center">SSH-based key provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img alt="pypi: swarmauri_keyprovider_ssh" src="https://img.shields.io/pypi/v/swarmauri_keyprovider_ssh?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img alt="Monthly PyPI downloads: swarmauri_keyprovider_ssh" src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_ssh?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/README.md"><img alt="README hits: swarmauri_keyprovider_ssh" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_keyprovider_ssh/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

An asynchronous `KeyProviderBase` implementation that keeps SSH key material in
memory and bridges it to Swarmauri's signing abstractions.

### Why This Package

`swarmauri_keyprovider_ssh` isolates this responsibility: SSH-based key provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/swarmauri_keyprovider_ssh/SshKeyProvider.py) exposes `SshKeyProvider`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_keyprovider_ssh` when your integration needs sSH-based key provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Generate new Ed25519, RSA-PSS (SHA-256), or ECDSA P-256 key pairs on demand.
- Import existing private keys (PEM) or public keys (OpenSSH) while respecting
  each key's `ExportPolicy`.
- Rotate keys, enumerate versions, and optionally destroy specific versions or
  entire key identifiers.
- Export public keys as RFC 7517-compliant JWKs/JWKS with OpenSSH fingerprints
  embedded in the `tags` metadata.
- Produce random bytes and derive keying material using the HKDF construction
  (RFC 5869).

### Non-Goals

`swarmauri_keyprovider_ssh` owns sSH-based key provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_keyprovider_ssh

# Poetry
poetry add swarmauri_keyprovider_ssh

# uv
uv add swarmauri_keyprovider_ssh
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyprovider_ssh
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyprovider_ssh
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyprovider_ssh
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/docs/readme/quick_start.py).

```python
import asyncio
from swarmauri_keyprovider_ssh import SshKeyProvider
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    ExportPolicy,
    KeyUse,
)


async def main() -> None:
    provider = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(ref.kid)
    print(jwk)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyprovider_ssh` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/docs/readme/usage.py).

```python
import asyncio
from swarmauri_keyprovider_ssh import SshKeyProvider
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    ExportPolicy,
    KeyUse,
)


async def main() -> None:
    provider = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(ref.kid)
    print(jwk)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The provider exposes an asynchronous interface for creating and managing
SSH-based signing keys.  The snippet below creates a new Ed25519 key and
exports its public component as a JSON Web Key (JWK):


Keys can also be rotated, and the provider will track key versions:

```python
ref = await provider.create_key(spec)
await provider.rotate_key(ref.kid)
assert await provider.list_versions(ref.kid) == (1, 2)
```

Use `destroy_key()` to remove an entire key identifier or just a single
version, and `jwks(prefix_kids=...)` when you need to emit a filtered JWKS for
downstream consumers.

Existing keys can be imported from PEM or OpenSSH data and exposed via JWKS:

```python
from pathlib import Path

pem = Path("id_ed25519").read_bytes()
ref = await provider.import_key(spec, pem)
jwks = await provider.jwks()
```

### Configuration

Configure `swarmauri_keyprovider_ssh` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/swarmauri_keyprovider_ssh/SshKeyProvider.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyprovider_ssh` source raises `KeyError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_keyprovider_ssh` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SshKeyProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_keyprovider_ssh` is located in `standards` and owns sSH-based key provider for Swarmauri. Source-declared APIs include `SshKeyProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyprovider_ssh`.

Source-declared exports or types: `SshKeyProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/swarmauri_keyprovider_ssh/SshKeyProvider.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.key_providers` → `ssh` → `swarmauri_keyprovider_ssh.SshKeyProvider:SshKeyProvider`
- `swarmauri.key_providers` → `SshKeyProvider` → `swarmauri_keyprovider_ssh.SshKeyProvider:SshKeyProvider`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyprovider_ssh` are `swarmauri-core`, `swarmauri-base`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/swarmauri_keyprovider_ssh/SshKeyProvider.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_keyprovider_ssh` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_keyprovider_ssh`, use the source-declared public interfaces (`SshKeyProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyprovider_ssh` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyprovider_ssh`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/swarmauri_keyprovider_ssh/SshKeyProvider.py). The `swarmauri_keyprovider_ssh` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyprovider_ssh` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyprovider_ssh` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_ssh_provider_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/tests/functional/test_ssh_provider_functional.py)
- [tests/perf/test_ssh_provider_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/tests/perf/test_ssh_provider_perf.py)
- [tests/unit/test_readme_examples.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/tests/unit/test_readme_examples.py)
- [tests/unit/test_rfc5869_hkdf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/tests/unit/test_rfc5869_hkdf.py)
- [tests/unit/test_rfc7517_jwk.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/tests/unit/test_rfc7517_jwk.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyprovider_ssh` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/swarmauri_keyprovider_ssh/SshKeyProvider.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_keyprovider_ssh` provides sSH-based key provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_keyprovider_ssh`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/swarmauri_keyprovider_ssh/SshKeyProvider.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyprovider_ssh` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/swarmauri_keyprovider_ssh/SshKeyProvider.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml) provide the supporting context for `swarmauri_keyprovider_ssh`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_keyprovider_ssh](https://pypi.org/project/swarmauri_keyprovider_ssh/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_keyprovider_ssh` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_keyprovider_ssh` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyprovider_ssh` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyprovider_ssh` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyprovider_ssh` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_ssh/NOTICE) for attribution.
<!-- readme-standards:end notices -->
