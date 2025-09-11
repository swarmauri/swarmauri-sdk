![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_shamir" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_shamir/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_shamir.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_mre_crypto_shamir" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/">
        <img src="https://img.shields.io/pypi/l/swarmauri_mre_crypto_shamir" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/">
        <img src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_shamir?label=swarmauri_mre_crypto_shamir&color=green" alt="PyPI - swarmauri_mre_crypto_shamir"/></a>

</p>

---

# swarmauri_mre_crypto_shamir

Shamir Secret Sharing based multi-recipient encryption (MRE) provider for the Swarmauri framework. The provider splits an AES-256-GCM content encryption key using Shamir's threshold scheme and distributes shares to recipients.

## Features
- AES-256-GCM payload encryption
- Threshold k-of-n key sharing via Shamir secret sharing
- Envelope rewrapping with optional payload rotation

## Extras
The plugin supports optional canonicalization extras:
- `cbor` – enables CBOR canonicalization via `cbor2`

## Installation
This package is part of the Swarmauri standards collection and is typically installed as part of the `swarmauri-sdk` workspace.

## License
Apache-2.0
