# swarmauri_keyprovider_gcpkms

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyprovider_gcpkms</strong></p>
<p align="center">Google Cloud KMS-backed Swarmauri key provider for key metadata, encryption, signing, wrapping, public JWKS, and HKDF workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/"><img alt="pypi: swarmauri_keyprovider_gcpkms" src="https://img.shields.io/pypi/v/swarmauri_keyprovider_gcpkms"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/"><img alt="Monthly PyPI downloads: swarmauri_keyprovider_gcpkms" src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_gcpkms"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/README.md"><img alt="README hits: swarmauri_keyprovider_gcpkms" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_keyprovider_gcpkms/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_keyprovider_gcpkms` provides `GcpKmsKeyProvider`, a Swarmauri key provider for [Google Cloud Key Management Service](https://cloud.google.com/kms/docs/reference/rest). It wraps Cloud KMS REST operations for key metadata, symmetric encryption and decryption, asymmetric signing and verification, RSA-OAEP key wrapping, public JWK/JWKS publishing, random bytes, and HKDF derivation.

### Why This Package

Use this package when Swarmauri applications need Google Cloud managed key material behind the shared key-provider interface. It lets agents, token services, envelope-encryption flows, and verifier services work with Cloud KMS keys while keeping credentials, OAuth token refresh, REST requests, public-key caching, and Swarmauri `KeyRef` metadata in one component.

### When to Use

Choose `swarmauri_keyprovider_gcpkms` when your integration needs google Cloud KMS-backed Swarmauri key provider for key metadata, encryption, signing, wrapping, public JWKS, and HKDF workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `GcpKmsKeyProvider` registered under the `swarmauri.key_providers` entry point.
- Google Application Default Credentials and OAuth token refresh.
- Cloud KMS symmetric `encrypt` and `decrypt` REST calls.
- Cloud KMS asymmetric `asymmetricSign` calls.
- Local RSA and EC signature verification using public keys from Cloud KMS.
- RSA-OAEP `wrap_key()` with public keys and `unwrap_key()` through `asymmetricDecrypt`.
- RFC 7517 JWK conversion for RSA, P-256, P-384, and secp256k1 public keys.
- JWKS aggregation across enabled key versions in a key ring.
- Enabled-version listing and version-specific destroy calls.
- Local secure random bytes and HKDF helpers.
- Optional `cbor` extra for workflows that need canonical CBOR support.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_keyprovider_gcpkms` owns google Cloud KMS-backed Swarmauri key provider for key metadata, encryption, signing, wrapping, public JWKS, and HKDF workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Google Cloud project with the Cloud KMS API enabled.
- Existing key ring in the selected location.
- Application Default Credentials available to the runtime.
- IAM permissions for the operations you use, commonly `cloudkms.cryptoKeys.get`, `cloudkms.cryptoKeys.list`, `cloudkms.cryptoKeyVersions.list`, `cloudkms.cryptoKeyVersions.viewPublicKey`, `cloudkms.cryptoKeyVersions.useToSign`, `cloudkms.cryptoKeyVersions.useToDecrypt`, `cloudkms.cryptoKeys.encrypt`, `cloudkms.cryptoKeys.decrypt`, and `cloudkms.cryptoKeyVersions.destroy`.

### Installation

Install with `uv`:

```bash
uv add swarmauri_keyprovider_gcpkms
```

Install with `pip`:

```bash
pip install swarmauri_keyprovider_gcpkms
```

Install with CBOR extras:

```bash
pip install "swarmauri_keyprovider_gcpkms[cbor]"
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyprovider_gcpkms
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyprovider_gcpkms
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyprovider_gcpkms
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider


async def main() -> None:
    provider = GcpKmsKeyProvider(
        project_id="my-project",
        location_id="us-central1",
        key_ring_id="swarmauri",
    )
    key_ref = await provider.get_key("jwt-signing-key")
    jwk = await provider.get_public_jwk("jwt-signing-key", key_ref.version)

    print(key_ref.uses)
    print(jwk["kty"])


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyprovider_gcpkms` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/docs/readme/usage.py).

```python
import asyncio

from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider


async def main() -> None:
    provider = GcpKmsKeyProvider(
        project_id="my-project",
        location_id="us-central1",
        key_ring_id="swarmauri",
    )
    key_ref = await provider.get_key("jwt-signing-key")
    jwk = await provider.get_public_jwk("jwt-signing-key", key_ref.version)

    print(key_ref.uses)
    print(jwk["kty"])


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Inspect a Cloud KMS key and publish a public JWK:


Sign and verify with an asymmetric Cloud KMS key:

```python
import asyncio

from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider


async def main() -> None:
    provider = GcpKmsKeyProvider(
        project_id="my-project",
        location_id="us-central1",
        key_ring_id="swarmauri",
    )
    message = b"payload to sign"

    signature = await provider.sign("jwt-signing-key", message)
    verified = await provider.verify("jwt-signing-key", message, signature)

    print(verified)


asyncio.run(main())
```

Encrypt and decrypt with a symmetric Cloud KMS key:

```python
import asyncio

from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider


async def main() -> None:
    provider = GcpKmsKeyProvider(
        project_id="my-project",
        location_id="us-east1",
        key_ring_id="data-protection",
    )
    aad = b"swarmauri::tenant-a"

    ciphertext = await provider.encrypt(
        "documents",
        b"secret payload",
        aad=aad,
    )
    plaintext = await provider.decrypt(
        "documents",
        ciphertext,
        aad=aad,
    )

    print(plaintext)


asyncio.run(main())
```

Wrap and unwrap data keys with an RSA decrypt key:

```python
import asyncio

from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider


async def main() -> None:
    provider = GcpKmsKeyProvider(
        project_id="my-project",
        location_id="us-east1",
        key_ring_id="data-protection",
    )
    data_key = await provider.random_bytes(32)

    wrapped = await provider.wrap_key("rsa-wrapping-key", data_key)
    unwrapped = await provider.unwrap_key("rsa-wrapping-key", wrapped)

    print(unwrapped == data_key)


asyncio.run(main())
```

### Configuration

Configure `swarmauri_keyprovider_gcpkms` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/swarmauri_keyprovider_gcpkms/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyprovider_gcpkms` source raises `NotImplementedError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Prefer workload identity or managed service account credentials over long-lived local key files.
- Use version-specific operations when destroying key material.
- Refresh JWKS caches after rotation when verifier services need immediate key visibility.
- Keep Cloud KMS key creation and IAM policy setup in infrastructure code for repeatability.
- Use `wrap_key()` and `unwrap_key()` for envelope encryption keys, and `encrypt()`/`decrypt()` for symmetric Cloud KMS crypto keys.

---

## Package Boundary

### What It Owns

`swarmauri_keyprovider_gcpkms` is located in `community` and owns google Cloud KMS-backed Swarmauri key provider for key metadata, encryption, signing, wrapping, public JWKS, and HKDF workflows. Source-declared APIs include `GcpKmsKeyProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyprovider_gcpkms`.

Source-declared exports or types: `GcpKmsKeyProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/swarmauri_keyprovider_gcpkms/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.key_providers` → `GcpKmsKeyProvider` → `swarmauri_keyprovider_gcpkms.GcpKmsKeyProvider:GcpKmsKeyProvider`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyprovider_gcpkms` are `google-auth`, `httpx`, `cryptography`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/swarmauri_keyprovider_gcpkms/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_keyprovider_gcpkms` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_keyprovider_gcpkms`, use the source-declared public interfaces (`GcpKmsKeyProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyprovider_gcpkms` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyprovider_gcpkms`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/swarmauri_keyprovider_gcpkms/__init__.py). The `swarmauri_keyprovider_gcpkms` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyprovider_gcpkms` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyprovider_gcpkms` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_hkdf_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/tests/functional/test_hkdf_functional.py)
- [tests/perf/test_b64_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/tests/perf/test_b64_perf.py)
- [tests/unit/test_gcpkms_provider_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/tests/unit/test_gcpkms_provider_unit.py)
- [tests/unit/test_rfc7517_jwk.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/tests/unit/test_rfc7517_jwk.py)
- [tests/unit/test_rfc7518_algorithms.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/tests/unit/test_rfc7518_algorithms.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyprovider_gcpkms` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/swarmauri_keyprovider_gcpkms/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does create_key() create every Cloud KMS key type?**

A: No. The current `create_key()` helper creates a symmetric `ENCRYPT_DECRYPT` crypto key. Use Google Cloud KMS configuration or provisioning workflows for asymmetric signing and asymmetric decrypt keys, then reference them by `kid`.

**Q: What key operations are implemented?**

A: The provider implements `encrypt()`, `decrypt()`, `sign()`, `verify()`, `wrap_key()`, `unwrap_key()`, `get_key()`, `list_versions()`, `get_public_jwk()`, `jwks()`, `destroy_key()`, `random_bytes()`, and `hkdf()`.

### How

**Q: How does the provider authenticate to Google Cloud?**

A: The provider uses `google.auth.default(scopes=[cloud-platform])`, so it works with Application Default Credentials, workload identity, service account credentials, and other Google-supported credential sources.

**Q: How are public keys cached?**

A: Public PEM responses are cached per crypto key version for five minutes. JWKS generation and verification reuse that cache to reduce Cloud KMS API calls.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyprovider_gcpkms` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/swarmauri_keyprovider_gcpkms/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/pyproject.toml) provide the supporting context for `swarmauri_keyprovider_gcpkms`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Key provider packages:

- [swarmauri_keyprovider_aws_kms](https://pypi.org/project/swarmauri_keyprovider_aws_kms/)
- [swarmauri_keyprovider_vaulttransit](https://pypi.org/project/swarmauri_keyprovider_vaulttransit/)
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
- [pypi: swarmauri_keyprovider_gcpkms](https://pypi.org/project/swarmauri_keyprovider_gcpkms/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_keyprovider_gcpkms`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_keyprovider_gcpkms` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_keyprovider_gcpkms` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyprovider_gcpkms` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyprovider_gcpkms` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyprovider_gcpkms` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_keyprovider_gcpkms/NOTICE) for attribution.
<!-- readme-standards:end notices -->
