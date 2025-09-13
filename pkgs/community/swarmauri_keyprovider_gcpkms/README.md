<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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
