# swarmauri_keyprovider_vaulttransit

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyprovider_vaulttransit</strong></p>
<p align="center">HashiCorp Vault Transit-backed Swarmauri key provider for non-exportable key lifecycle, public JWKS metadata, Vault RNG, and HKDF.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/"><img alt="pypi: swarmauri_keyprovider_vaulttransit" src="https://img.shields.io/pypi/v/swarmauri_keyprovider_vaulttransit"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/"><img alt="Monthly PyPI downloads: swarmauri_keyprovider_vaulttransit" src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_vaulttransit"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/README.md"><img alt="README hits: swarmauri_keyprovider_vaulttransit" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_keyprovider_vaulttransit/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_keyprovider_vaulttransit` provides `VaultTransitKeyProvider`, a Swarmauri key provider for HashiCorp Vault Transit key lifecycle and public-key metadata workflows. It creates and rotates non-exportable Vault Transit keys, returns Swarmauri `KeyRef` objects, exports public JWK and JWKS metadata, uses Vault or local random bytes, and derives key material with HKDF-SHA256.

### Why This Package

Use this package when Swarmauri applications need Vault Transit-managed keys behind the shared key-provider interface. It keeps Vault client setup, Transit mount configuration, key creation, rotation, metadata lookup, public-key export, JWKS formatting, random bytes, and HKDF derivation in one component that can be combined with Swarmauri signing, token, certificate, and verifier packages.

### When to Use

Choose `swarmauri_keyprovider_vaulttransit` when your integration needs hashiCorp Vault Transit-backed Swarmauri key provider for non-exportable key lifecycle, public JWKS metadata, Vault RNG, and HKDF. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `VaultTransitKeyProvider` registered under the `swarmauri.key_providers` entry point.
- HashiCorp Vault client setup through `hvac` or an injected client.
- Transit mount configuration with optional Vault Enterprise namespace support.
- Non-exportable key creation for AES, RSA, ECDSA P-256, and Ed25519 workflows.
- Key rotation through Vault Transit `rotate_key`.
- Full key deletion or specific key-version destruction.
- Key version listing and latest-version metadata.
- Public JWK conversion for RSA, P-256, and Ed25519 public keys.
- JWKS document creation with optional key ID prefix filtering.
- Vault RNG support through `sys.generate_random_bytes()` with local `os.urandom` fallback.
- HKDF-SHA256 derivation helper.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_keyprovider_vaulttransit` owns hashiCorp Vault Transit-backed Swarmauri key provider for non-exportable key lifecycle, public JWKS metadata, Vault RNG, and HKDF. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- A running HashiCorp Vault server.
- Transit secrets engine enabled at the configured mount path, usually `transit`.
- Vault token authenticated for the needed Transit paths.
- Capabilities for key lifecycle paths such as `transit/keys/*`, export or read access for public key metadata, and optional access to `sys/tools/random` or equivalent random-byte APIs when `prefer_vault_rng=True`.
- TLS verification configuration appropriate for the Vault endpoint.

### Installation

Install with `uv`:

```bash
uv add swarmauri_keyprovider_vaulttransit
```

Install with `pip`:

```bash
pip install swarmauri_keyprovider_vaulttransit
```

The package also exposes optional extras:

```bash
pip install "swarmauri_keyprovider_vaulttransit[vault]"
pip install "swarmauri_keyprovider_vaulttransit[crypto]"
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyprovider_vaulttransit
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyprovider_vaulttransit
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyprovider_vaulttransit
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider
from swarmauri_core.key_providers.types import ExportPolicy, KeyAlg, KeySpec


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="https://vault.example.com:8200",
        token="vault-token",
        mount="transit",
        verify="/etc/ssl/vault-ca.pem",
    )
    spec = KeySpec(
        alg=KeyAlg.ED25519,
        export_policy=ExportPolicy.never_export_secret,
        label="agents-signing",
    )

    key_ref = await provider.create_key(spec)
    rotated = await provider.rotate_key(key_ref.kid)

    print(key_ref.kid, key_ref.version)
    print(rotated.kid, rotated.version)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyprovider_vaulttransit` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/docs/readme/usage.py).

```python
import asyncio

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider
from swarmauri_core.key_providers.types import ExportPolicy, KeyAlg, KeySpec


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="https://vault.example.com:8200",
        token="vault-token",
        mount="transit",
        verify="/etc/ssl/vault-ca.pem",
    )
    spec = KeySpec(
        alg=KeyAlg.ED25519,
        export_policy=ExportPolicy.never_export_secret,
        label="agents-signing",
    )

    key_ref = await provider.create_key(spec)
    rotated = await provider.rotate_key(key_ref.kid)

    print(key_ref.kid, key_ref.version)
    print(rotated.kid, rotated.version)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Create and rotate a Vault Transit signing key:


Publish a public JWK and JWKS document:

```python
import asyncio

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="https://vault.example.com:8200",
        token="vault-token",
    )

    jwk = await provider.get_public_jwk("agents-signing", 1)
    jwks = await provider.jwks(prefix_kids="agents")

    print(jwk["kid"])
    print([entry["kid"] for entry in jwks["keys"]])


asyncio.run(main())
```

Generate random bytes and derive key material:

```python
import asyncio

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="https://vault.example.com:8200",
        token="vault-token",
        prefer_vault_rng=True,
    )

    ikm = await provider.random_bytes(32)
    derived = await provider.hkdf(
        ikm,
        salt=b"vault-salt",
        info=b"swarmauri/key-derivation",
        length=32,
    )

    print(len(derived))


asyncio.run(main())
```

### Configuration

Configure `swarmauri_keyprovider_vaulttransit` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/swarmauri_keyprovider_vaulttransit/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyprovider_vaulttransit` source raises `ImportError`, `NotImplementedError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use Vault policies with the narrowest Transit mount and key capabilities required by the workload.
- Prefer TLS verification with a pinned CA bundle for production Vault endpoints.
- Keep key lifecycle operations separate from runtime cryptographic operation policies.
- Use Vault namespaces explicitly when running on Vault Enterprise.
- Treat full key deletion and version destruction as irreversible operational events.

---

## Package Boundary

### What It Owns

`swarmauri_keyprovider_vaulttransit` is located in `community` and owns hashiCorp Vault Transit-backed Swarmauri key provider for non-exportable key lifecycle, public JWKS metadata, Vault RNG, and HKDF. Source-declared APIs include `VaultTransitKeyProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyprovider_vaulttransit`.

Source-declared exports or types: `VaultTransitKeyProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/swarmauri_keyprovider_vaulttransit/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.key_providers` → `VaultTransitKeyProvider` → `swarmauri_keyprovider_vaulttransit.VaultTransitKeyProvider:VaultTransitKeyProvider`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyprovider_vaulttransit` are `hvac`, `cryptography`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/swarmauri_keyprovider_vaulttransit/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_keyprovider_vaulttransit` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_keyprovider_vaulttransit`, use the source-declared public interfaces (`VaultTransitKeyProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyprovider_vaulttransit` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyprovider_vaulttransit`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/swarmauri_keyprovider_vaulttransit/__init__.py). The `swarmauri_keyprovider_vaulttransit` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyprovider_vaulttransit` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyprovider_vaulttransit` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/tests/test_functional.py)
- [tests/test_performance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/tests/test_performance.py)
- [tests/test_rfc5869_hkdf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/tests/test_rfc5869_hkdf.py)
- [tests/test_rfc7517_jwk.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/tests/test_rfc7517_jwk.py)
- [tests/test_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/tests/test_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyprovider_vaulttransit` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/swarmauri_keyprovider_vaulttransit/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this provider export private key material?**

A: No. Keys created by this provider are marked non-exportable and disallow plaintext backup. `KeyRef.material` remains `None`.

**Q: Which Vault Transit key types can it create?**

A: The provider maps Swarmauri algorithms to Vault Transit types: `AES256_GCM` to `aes256-gcm96`, RSA OAEP and RSA PSS to `rsa-3072`, ECDSA P-256 to `ecdsa-p256`, and Ed25519 to `ed25519`.

**Q: Does this package perform Vault Transit encrypt, decrypt, sign, or verify calls?**

A: Not in the current implementation. The provider focuses on key lifecycle, public metadata, random bytes, and HKDF. Use or add dedicated crypto/signing components for Transit cryptographic operations.

### How

**Q: How does JWKS export work?**

A: `get_public_jwk()` exports or reads public PEM material from Vault, converts RSA, P-256, and Ed25519 public keys into JWK dictionaries, and returns symmetric keys as `oct` metadata. `jwks()` lists keys from the configured mount and returns a JWKS document.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyprovider_vaulttransit` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/swarmauri_keyprovider_vaulttransit/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/pyproject.toml) provide the supporting context for `swarmauri_keyprovider_vaulttransit`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Key provider packages:

- [swarmauri_keyprovider_aws_kms](https://pypi.org/project/swarmauri_keyprovider_aws_kms/)
- [swarmauri_keyprovider_gcpkms](https://pypi.org/project/swarmauri_keyprovider_gcpkms/)
- [swarmauri_keyprovider_file](https://pypi.org/project/swarmauri_keyprovider_file/)
- [swarmauri_keyprovider_local](https://pypi.org/project/swarmauri_keyprovider_local/)
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/)
- [swarmauri_keyprovider_remote_jwks](https://pypi.org/project/swarmauri_keyprovider_remote_jwks/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines key provider types.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `KeyProviderBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_keyprovider_vaulttransit](https://pypi.org/project/swarmauri_keyprovider_vaulttransit/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_keyprovider_vaulttransit`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_keyprovider_vaulttransit` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_keyprovider_vaulttransit` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyprovider_vaulttransit` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyprovider_vaulttransit` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyprovider_vaulttransit` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_vaulttransit/NOTICE) for attribution.
<!-- readme-standards:end notices -->
