# swarmauri_keyprovider_aws_kms

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyprovider_aws_kms</strong></p>
<p align="center">AWS KMS-backed Swarmauri key provider for non-exportable key creation, alias-based rotation, KeyRef metadata, and public JWKS publishing.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/"><img alt="pypi: swarmauri_keyprovider_aws_kms" src="https://img.shields.io/pypi/v/swarmauri_keyprovider_aws_kms?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/"><img alt="Monthly PyPI downloads: swarmauri_keyprovider_aws_kms" src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_aws_kms?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/README.md"><img alt="README hits: swarmauri_keyprovider_aws_kms" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_keyprovider_aws_kms/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_keyprovider_aws_kms` provides `AwsKmsKeyProvider`, a Swarmauri key provider backed by [AWS Key Management Service](https://docs.aws.amazon.com/kms/latest/APIReference/). It creates non-exportable AWS KMS keys, maintains stable and versioned aliases, returns Swarmauri `KeyRef` metadata, publishes public JWK/JWKS material for asymmetric keys, and supports rotation and scheduled deletion workflows.

### Why This Package

Use this package when Swarmauri applications need AWS-managed key material without returning private keys to application memory. The provider maps Swarmauri `KeySpec` values to AWS KMS `KeySpec` and `KeyUsage`, keeps versioned aliases for rotation, and exposes public key metadata in a shape that downstream token, signing, and verifier components can consume.

### When to Use

Choose `swarmauri_keyprovider_aws_kms` when your integration needs aWS KMS-backed Swarmauri key provider for non-exportable key creation, alias-based rotation, KeyRef metadata, and public JWKS publishing. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `AwsKmsKeyProvider` registered under the `swarmauri.key_providers` entry point.
- AWS KMS key creation through `boto3`.
- Stable latest aliases and version aliases per `kid`.
- Rotation by creating a new KMS key version and updating aliases.
- `KeyRef` metadata with KMS key ID, region, label, algorithm, version, public PEM when supported, and fingerprint.
- Public JWK conversion for RSA and P-256 public keys.
- JWKS aggregation for latest key versions.
- Scheduled key deletion with AWS KMS deletion windows.
- Local `random_bytes()` and HKDF helpers.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_keyprovider_aws_kms` owns aWS KMS-backed Swarmauri key provider for non-exportable key creation, alias-based rotation, KeyRef metadata, and public JWKS publishing. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- AWS credentials resolvable by `boto3`.
- IAM permissions for the KMS operations you use, commonly `kms:CreateKey`, `kms:CreateAlias`, `kms:UpdateAlias`, `kms:ListAliases`, `kms:DescribeKey`, `kms:ListResourceTags`, `kms:GetPublicKey`, and `kms:ScheduleKeyDeletion`.
- An AWS region such as `us-east-1`.
- Optional custom key policy when account defaults are not enough for your access model.

### Installation

Install with `uv`:

```bash
uv add swarmauri_keyprovider_aws_kms
```

Install with `pip`:

```bash
pip install swarmauri_keyprovider_aws_kms
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyprovider_aws_kms
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyprovider_aws_kms
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyprovider_aws_kms
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)


async def main() -> None:
    provider = AwsKmsKeyProvider(
        region="us-east-1",
        alias_prefix="swarmauri-prod",
    )
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        size_bits=3072,
        export_policy=ExportPolicy.never_export_secret,
        label="jwt-signing",
    )

    key_ref = await provider.create_key(spec)
    rotated = await provider.rotate_key(key_ref.kid)

    print(key_ref.kid, key_ref.version)
    print(rotated.kid, rotated.version)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyprovider_aws_kms` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/docs/readme/usage.py).

```python
import asyncio

from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)


async def main() -> None:
    provider = AwsKmsKeyProvider(
        region="us-east-1",
        alias_prefix="swarmauri-prod",
    )
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        size_bits=3072,
        export_policy=ExportPolicy.never_export_secret,
        label="jwt-signing",
    )

    key_ref = await provider.create_key(spec)
    rotated = await provider.rotate_key(key_ref.kid)

    print(key_ref.kid, key_ref.version)
    print(rotated.kid, rotated.version)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Create and rotate a non-exportable AWS KMS key:


Publish public JWK metadata for verifiers:

```python
import asyncio

from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider


async def main() -> None:
    provider = AwsKmsKeyProvider(region="us-east-1", alias_prefix="swarmauri-prod")

    jwk = await provider.get_public_jwk("jwt-signing-kid")
    jwks = await provider.jwks(prefix_kids="jwt")

    print(jwk["kid"])
    print([key["kid"] for key in jwks["keys"]])


asyncio.run(main())
```

Use local random bytes and HKDF helpers:

```python
import asyncio

from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider


async def main() -> None:
    provider = AwsKmsKeyProvider(region="us-east-1")
    salt = await provider.random_bytes(32)
    secret = await provider.random_bytes(32)
    derived = await provider.hkdf(
        secret,
        salt=salt,
        info=b"swarmauri/aws-kms/example",
        length=32,
    )

    print(len(derived))


asyncio.run(main())
```

### Configuration

Configure `swarmauri_keyprovider_aws_kms` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/swarmauri_keyprovider_aws_kms/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyprovider_aws_kms` source raises `ImportError`, `KeyError`, `NotImplementedError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use narrow IAM permissions and explicit key policies for production accounts.
- Treat scheduled deletion as destructive; inspect `list_versions(kid)` before calling `destroy_key()`.
- Cache JWKS responses in verifier services, but refresh after planned rotations.
- Use clear `alias_prefix` values per environment to avoid mixing development and production keys.
- Keep cryptographic operations in dedicated signing or encryption components that can enforce operation-specific policy.

---

## Package Boundary

### What It Owns

`swarmauri_keyprovider_aws_kms` is located in `community` and owns aWS KMS-backed Swarmauri key provider for non-exportable key creation, alias-based rotation, KeyRef metadata, and public JWKS publishing. Source-declared APIs include `AwsKmsKeyProvider`, `_b64u`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyprovider_aws_kms`.

Source-declared exports or types: `AwsKmsKeyProvider`, `_b64u`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/swarmauri_keyprovider_aws_kms/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.key_providers` → `AwsKmsKeyProvider` → `swarmauri_keyprovider_aws_kms.AwsKmsKeyProvider:AwsKmsKeyProvider`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyprovider_aws_kms` are `boto3`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/swarmauri_keyprovider_aws_kms/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_keyprovider_aws_kms` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_keyprovider_aws_kms`, use the source-declared public interfaces (`AwsKmsKeyProvider`, `_b64u`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyprovider_aws_kms` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyprovider_aws_kms`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/swarmauri_keyprovider_aws_kms/__init__.py). The `swarmauri_keyprovider_aws_kms` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyprovider_aws_kms` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyprovider_aws_kms` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/rfc/test_rfc7515.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/tests/rfc/test_rfc7515.py)
- [tests/rfc/test_rfc7517.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/tests/rfc/test_rfc7517.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyprovider_aws_kms` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/swarmauri_keyprovider_aws_kms/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this provider export private key material?**

A: No. AWS KMS keys created by this provider are represented as non-exportable `KeyRef` objects. `get_key(include_secret=True)` still returns metadata and public material where available, not private material.

**Q: Which AWS KMS key types are supported?**

A: The provider supports symmetric AES-256-GCM through `SYMMETRIC_DEFAULT`, RSA OAEP SHA-256, RSA PSS SHA-256, and ECDSA P-256 SHA-256. RSA sizes map to AWS-supported 2048, 3072, or 4096 bit keys.

**Q: Does this package call AWS KMS Sign, Encrypt, or Decrypt?**

A: No. This package manages keys and public metadata. Use a signing, encryption, or envelope-encryption component for cryptographic operations that call KMS runtime APIs.

### How

**Q: How does rotation work?**

A: `rotate_key(kid)` creates a new KMS key with the same algorithm metadata, creates a new `alias/<prefix>/<kid>/vN` alias, and repoints `alias/<prefix>/<kid>` to the latest version. Older version aliases remain available.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyprovider_aws_kms` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/swarmauri_keyprovider_aws_kms/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/pyproject.toml) provide the supporting context for `swarmauri_keyprovider_aws_kms`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Key provider packages:

- [swarmauri_keyprovider_gcpkms](https://pypi.org/project/swarmauri_keyprovider_gcpkms/)
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
- [pypi: swarmauri_keyprovider_aws_kms](https://pypi.org/project/swarmauri_keyprovider_aws_kms/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_keyprovider_aws_kms`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_keyprovider_aws_kms` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_keyprovider_aws_kms` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyprovider_aws_kms` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyprovider_aws_kms` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyprovider_aws_kms` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_keyprovider_aws_kms/NOTICE) for attribution.
<!-- readme-standards:end notices -->
