# swarmauri_crypto_shamir

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
