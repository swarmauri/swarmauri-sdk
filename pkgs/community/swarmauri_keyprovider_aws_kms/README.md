![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_aws_kms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_aws_kms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_aws_kms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_aws_kms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_aws_kms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_aws_kms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_aws_kms?label=swarmauri_keyprovider_aws_kms&color=green" alt="PyPI - swarmauri_keyprovider_aws_kms"/></a>

</p>

---

# Swarmauri AWS KMS Key Provider

Community plugin providing an AWS Key Management Service (KMS) backed `KeyProvider` for Swarmauri. It manages non-exportable customer managed keys (CMKs), exposes JWKS for downstream services, and handles key rotation workflows aligned with AWS best practices.

## Features

- Create RSA, ECC, and AES-256 keys in AWS KMS with deterministic aliasing per `kid` and version.
- Rotate keys by minting new KMS key versions and updating aliases, while preserving previous versions for auditing or staged cutovers.
- Describe keys through `KeyRef` objects, including public PEM material when the key spec allows export, and RFC 7517-compliant JWKs via `get_public_jwk`/`jwks`.
- Generate cryptographically secure random bytes and perform HKDF expansion with SHA-256 to support envelope encryption and symmetric derivation flows.
- Destroy keys by scheduling deletion through the KMS API, maintaining Swarmauri tagging metadata for traceability.

## Prerequisites

- Python 3.10 or newer.
- `boto3` (installed automatically with this package) and network access to the target AWS region.
- AWS credentials with permissions such as `kms:CreateKey`, `kms:CreateAlias`, `kms:UpdateAlias`, `kms:DescribeKey`, `kms:GetPublicKey`, `kms:ListAliases`, `kms:ListResourceTags`, and `kms:ScheduleKeyDeletion`.
- Optional: a custom key policy if you need to delegate key administration to non-root principals; pass it through the `key_policy` constructor argument.

## Installation

```bash
# pip
pip install swarmauri_keyprovider_aws_kms

# poetry
poetry add swarmauri_keyprovider_aws_kms

# uv (pyproject-based projects)
uv add swarmauri_keyprovider_aws_kms
```

## Quickstart: Create, Rotate, and Publish Keys

```python
import asyncio
from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec, ExportPolicy


async def main() -> None:
    provider = AwsKmsKeyProvider(region="us-east-1", alias_prefix="swarmauri-demo")

    rsa_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        size_bits=3072,
        export_policy=ExportPolicy.never_export_secret,
        label="api-signing",
    )

    # Create the initial version (aliases: alias/swarmauri-demo/<kid> and .../v1)
    key_ref = await provider.create_key(rsa_spec)
    print("KID", key_ref.kid, "version", key_ref.version)

    # Surface the public JWK for JWT signing or JWKS endpoints
    jwk = await provider.get_public_jwk(key_ref.kid)
    print("Public JWK", jwk)

    # Rotate the key – new CMK in KMS, version alias bump, old alias retained
    rotated = await provider.rotate_key(key_ref.kid)
    print("Rotated to version", rotated.version)

    # Publish the aggregate JWKS (includes the latest version per kid)
    jwks_payload = await provider.jwks()
    print("JWKS keys", [k["kid"] for k in jwks_payload["keys"]])


if __name__ == "__main__":
    asyncio.run(main())
```

## Symmetric Utilities: Random Bytes and HKDF

```python
import asyncio
from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider


async def derive_data_key() -> bytes:
    provider = AwsKmsKeyProvider(region="us-east-1")

    master_salt = await provider.random_bytes(32)
    info = b"swarmauri/example"

    pseudo_random_key = await provider.random_bytes(32)
    derived = await provider.hkdf(
        pseudo_random_key,
        salt=master_salt,
        info=info,
        length=32,
    )
    return derived


# asyncio.run(derive_data_key())
```

## Operational Tips

- `list_versions(kid)` inspects versioned aliases (`alias/<prefix>/<kid>/vN`); use it before destructive actions to ensure you capture all active CMKs.
- Destroying a key schedules deletion for 7 days. Plan rotations ahead of time so dependent systems can migrate to the new version before you call `destroy_key`.
- Tag metadata persisted by the provider (`saur:kid`, `saur:version`, `saur:alg`, optional `saur:label`) enables inventory checks—query them from the AWS console or CLI when auditing.
- For high-throughput signing, ensure your IAM policies, KMS quotas, and region placement match latency expectations; consider caching public JWKs from `jwks()` in your verifier services.
