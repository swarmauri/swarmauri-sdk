![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_keyprovider_gcpkms/">
        <img src="https://static.pepy.tech/badge/swarmauri_keyprovider_gcpkms/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_gcpkms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_gcpkms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_gcpkms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_gcpkms?label=swarmauri_keyprovider_gcpkms&color=green" alt="PyPI - swarmauri_keyprovider_gcpkms"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri GCP KMS Key Provider

`swarmauri_keyprovider_gcpkms` provides `GcpKmsKeyProvider`, a Swarmauri key provider for [Google Cloud Key Management Service](https://cloud.google.com/kms/docs/reference/rest). It wraps Cloud KMS REST operations for key metadata, symmetric encryption and decryption, asymmetric signing and verification, RSA-OAEP key wrapping, public JWK/JWKS publishing, random bytes, and HKDF derivation.

## Why Swarmauri GCP KMS Key Provider?

Use this package when Swarmauri applications need Google Cloud managed key material behind the shared key-provider interface. It lets agents, token services, envelope-encryption flows, and verifier services work with Cloud KMS keys while keeping credentials, OAuth token refresh, REST requests, public-key caching, and Swarmauri `KeyRef` metadata in one component.

## FAQ

### Q: How does the provider authenticate to Google Cloud?

A: The provider uses `google.auth.default(scopes=[cloud-platform])`, so it works with Application Default Credentials, workload identity, service account credentials, and other Google-supported credential sources.

### Q: Does `create_key()` create every Cloud KMS key type?

A: No. The current `create_key()` helper creates a symmetric `ENCRYPT_DECRYPT` crypto key. Use Google Cloud KMS configuration or provisioning workflows for asymmetric signing and asymmetric decrypt keys, then reference them by `kid`.

### Q: What key operations are implemented?

A: The provider implements `encrypt()`, `decrypt()`, `sign()`, `verify()`, `wrap_key()`, `unwrap_key()`, `get_key()`, `list_versions()`, `get_public_jwk()`, `jwks()`, `destroy_key()`, `random_bytes()`, and `hkdf()`.

### Q: How are public keys cached?

A: Public PEM responses are cached per crypto key version for five minutes. JWKS generation and verification reuse that cache to reduce Cloud KMS API calls.

## Features

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

## Prerequisites

- Google Cloud project with the Cloud KMS API enabled.
- Existing key ring in the selected location.
- Application Default Credentials available to the runtime.
- IAM permissions for the operations you use, commonly `cloudkms.cryptoKeys.get`, `cloudkms.cryptoKeys.list`, `cloudkms.cryptoKeyVersions.list`, `cloudkms.cryptoKeyVersions.viewPublicKey`, `cloudkms.cryptoKeyVersions.useToSign`, `cloudkms.cryptoKeyVersions.useToDecrypt`, `cloudkms.cryptoKeys.encrypt`, `cloudkms.cryptoKeys.decrypt`, and `cloudkms.cryptoKeyVersions.destroy`.

## Installation

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

## Usage

Inspect a Cloud KMS key and publish a public JWK:

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

## Related Packages

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

## Best Practices

- Prefer workload identity or managed service account credentials over long-lived local key files.
- Use version-specific operations when destroying key material.
- Refresh JWKS caches after rotation when verifier services need immediate key visibility.
- Keep Cloud KMS key creation and IAM policy setup in infrastructure code for repeatability.
- Use `wrap_key()` and `unwrap_key()` for envelope encryption keys, and `encrypt()`/`decrypt()` for symmetric Cloud KMS crypto keys.

## License

Apache-2.0


