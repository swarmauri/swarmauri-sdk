# Swarmauri GCP KMS Key Provider

GCP KMS-backed key provider for the Swarmauri framework. This plugin exposes
Google Cloud KMS keys through the common `IKeyProvider` interface, enabling
signing, verification, encryption and random byte generation.

## Optional Canonicalization Extras

- `cbor` – enables CBOR canonicalization utilities via `cbor2`.

## Features

- AES encryption and decryption using KMS-managed symmetric keys.
- RSA and EC signing backed by Cloud KMS.
- RSA wrapping and unwrapping of data encryption keys.
- JWKS export for asymmetric public keys.

## Installation

```bash
uv add swarmauri_keyprovider_gcpkms
```

Enable CBOR canonicalization support:

```bash
uv add swarmauri_keyprovider_gcpkms[cbor]
```

## Usage

```python
from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider

kp = GcpKmsKeyProvider(
    project_id="my-project",
    location_id="us-east1",
    key_ring_id="my-ring",
)
```
