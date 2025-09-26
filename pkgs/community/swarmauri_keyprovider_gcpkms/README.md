![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_gcpkms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_gcpkms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_gcpkms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_gcpkms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_gcpkms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_gcpkms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_gcpkms?label=swarmauri_keyprovider_gcpkms&color=green" alt="PyPI - swarmauri_keyprovider_gcpkms"/></a>

</p>

---

# Swarmauri GCP KMS Key Provider

Google Cloud KMS-backed key provider for the Swarmauri framework. It exposes Cloud KMS asymmetric and symmetric keys through the common `IKeyProvider` interface so agents can sign, verify, encrypt, decrypt, wrap, and unwrap data without leaving Swarmauri.

## Optional Canonicalization Extras

- `cbor` – installs `cbor2` to enable canonical CBOR utilities where workflows require deterministic binary encoding.

## Features

- Use Cloud KMS asymmetric keys for RSA/EC signing and verification while receiving RFC 7517 JWKS payloads for downstream services.
- Perform RSA-OAEP wrapping/unwrapping of data encryption keys and AES-256 encryption/decryption with hardware-backed material.
- Publish JWKS documents from Cloud KMS public keys, including caching and TTL-based refresh to minimize API calls.
- Generate random bytes and derive key material via HKDF with SHA-256 for envelope encryption scenarios.
- Destroy individual key versions via the Cloud KMS REST API when performing decommissioning workflows.

## Prerequisites

- Python 3.10 or newer.
- `google-auth` and `requests` (installed automatically) plus network access to Google Cloud KMS endpoints.
- A Google Cloud project with the KMS API enabled, along with a key ring (`key_ring_id`) in your chosen location (`location_id`).
- Service account or workload identity with permissions such as `cloudkms.cryptoKeys.get`, `cloudkms.cryptoKeyVersions.useToSign`, `cloudkms.cryptoKeyVersions.useToDecrypt`, `cloudkms.cryptoKeys.list`, and `cloudkms.keyRings.get`.
- Application Default Credentials available to the runtime (e.g., `GOOGLE_APPLICATION_CREDENTIALS`, workload identity, or Cloud Run default service account).

## Installation

```bash
# pip
pip install swarmauri_keyprovider_gcpkms

# poetry
poetry add swarmauri_keyprovider_gcpkms

# uv (pyproject-based projects)
uv add swarmauri_keyprovider_gcpkms

# Extras for CBOR canonicalization
pip install "swarmauri_keyprovider_gcpkms[cbor]"
```

## Quickstart: Sign and Verify with Cloud KMS

```python
import asyncio
from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyUse


async def main() -> None:
    provider = GcpKmsKeyProvider(
        project_id="my-project",
        location_id="us-central1",
        key_ring_id="swarmauri",
    )

    key_ref = await provider.get_key(
        kid="projects/my-project/locations/us-central1/keyRings/swarmauri/cryptoKeys/jwt-key",
        version=None,
    )

    message = b"payload to sign"
    signature = await provider.sign(key_ref.kid, message, alg=JWAAlg.RS256)
    await provider.verify(key_ref.kid, message, signature, alg=JWAAlg.RS256)

    jwk = await provider.get_public_jwk(key_ref.kid, key_ref.version)
    print("Public JWK", jwk)


if __name__ == "__main__":
    asyncio.run(main())
```

## Encrypt and Wrap Data Keys

```python
import asyncio
from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider


async def encrypt_documents() -> None:
    provider = GcpKmsKeyProvider(
        project_id="my-project",
        location_id="us-east1",
        key_ring_id="data-protection",
    )

    dek = await provider.random_bytes(32)
    aad = b"swarmauri::tenant-a"

    ciphertext = await provider.encrypt(
        kid="projects/my-project/locations/us-east1/keyRings/data-protection/cryptoKeys/primary",
        plaintext=b"secret payload",
        associated_data=aad,
    )

    wrapped = await provider.wrap(
        kid="projects/my-project/locations/us-east1/keyRings/data-protection/cryptoKeys/wrapping",
        plaintext=dek,
    )

    unwrapped = await provider.unwrap(
        kid="projects/my-project/locations/us-east1/keyRings/data-protection/cryptoKeys/wrapping",
        ciphertext=wrapped,
    )
    assert unwrapped == dek


# asyncio.run(encrypt_documents())
```

## Operational Tips

- The provider caches public keys (`_pub_cache`) for 5 minutes; call `get_public_jwk(..., force=True)` if you rotate Cloud KMS key versions and need instant propagation.
- Use explicit key version names when destroying or disabling keys: `projects/.../cryptoKeys/<name>/cryptoKeyVersions/<n>`.
- Cloud KMS rotation is controlled outside the provider (per key configuration). Combine the provider with IAM rotation settings to enforce regular key versioning.
- For auditability, inspect the `tags` field on returned `KeyRef` objects—they include algorithm purpose and key type hints derived from Cloud KMS metadata.
