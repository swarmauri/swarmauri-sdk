![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://static.pepy.tech/badge/swarmauri_keyprovider_aws_kms/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_aws_kms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_aws_kms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_aws_kms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_aws_kms?label=swarmauri_keyprovider_aws_kms&color=green" alt="PyPI - swarmauri_keyprovider_aws_kms"/></a>
</p>

# Swarmauri AWS KMS Key Provider

`swarmauri_keyprovider_aws_kms` provides `AwsKmsKeyProvider`, a Swarmauri key provider backed by [AWS Key Management Service](https://docs.aws.amazon.com/kms/latest/APIReference/). It creates non-exportable AWS KMS keys, maintains stable and versioned aliases, returns Swarmauri `KeyRef` metadata, publishes public JWK/JWKS material for asymmetric keys, and supports rotation and scheduled deletion workflows.

## Why Swarmauri AWS KMS Key Provider?

Use this package when Swarmauri applications need AWS-managed key material without returning private keys to application memory. The provider maps Swarmauri `KeySpec` values to AWS KMS `KeySpec` and `KeyUsage`, keeps versioned aliases for rotation, and exposes public key metadata in a shape that downstream token, signing, and verifier components can consume.

## FAQ

### Q: Does this provider export private key material?

A: No. AWS KMS keys created by this provider are represented as non-exportable `KeyRef` objects. `get_key(include_secret=True)` still returns metadata and public material where available, not private material.

### Q: Which AWS KMS key types are supported?

A: The provider supports symmetric AES-256-GCM through `SYMMETRIC_DEFAULT`, RSA OAEP SHA-256, RSA PSS SHA-256, and ECDSA P-256 SHA-256. RSA sizes map to AWS-supported 2048, 3072, or 4096 bit keys.

### Q: How does rotation work?

A: `rotate_key(kid)` creates a new KMS key with the same algorithm metadata, creates a new `alias/<prefix>/<kid>/vN` alias, and repoints `alias/<prefix>/<kid>` to the latest version. Older version aliases remain available.

### Q: Does this package call AWS KMS Sign, Encrypt, or Decrypt?

A: No. This package manages keys and public metadata. Use a signing, encryption, or envelope-encryption component for cryptographic operations that call KMS runtime APIs.

## Features

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

## Prerequisites

- AWS credentials resolvable by `boto3`.
- IAM permissions for the KMS operations you use, commonly `kms:CreateKey`, `kms:CreateAlias`, `kms:UpdateAlias`, `kms:ListAliases`, `kms:DescribeKey`, `kms:ListResourceTags`, `kms:GetPublicKey`, and `kms:ScheduleKeyDeletion`.
- An AWS region such as `us-east-1`.
- Optional custom key policy when account defaults are not enough for your access model.

## Installation

Install with `uv`:

```bash
uv add swarmauri_keyprovider_aws_kms
```

Install with `pip`:

```bash
pip install swarmauri_keyprovider_aws_kms
```

## Usage

Create and rotate a non-exportable AWS KMS key:

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

## Related Packages

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

## Best Practices

- Use narrow IAM permissions and explicit key policies for production accounts.
- Treat scheduled deletion as destructive; inspect `list_versions(kid)` before calling `destroy_key()`.
- Cache JWKS responses in verifier services, but refresh after planned rotations.
- Use clear `alias_prefix` values per environment to avoid mixing development and production keys.
- Keep cryptographic operations in dedicated signing or encryption components that can enforce operation-specific policy.

## License

Apache-2.0
