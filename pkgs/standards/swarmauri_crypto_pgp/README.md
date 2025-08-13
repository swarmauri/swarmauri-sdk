## swarmauri_crypto_pgp

OpenPGP (GnuPG-backed) crypto provider for Swarmauri implementing the `ICrypto` contract.

- Symmetric AEAD: AES-256-GCM
- Key wrapping: OpenPGP public-key encryption (RSA keys recommended)
- Hybrid encrypt-for-many supported

### Key material expectations

- `encrypt`/`decrypt`: `KeyRef.material` must be 16/24/32 bytes for AES-GCM
- `wrap`/`encrypt_for_many`: `KeyRef.public` must be ASCII-armored OpenPGP public key bytes
- `unwrap`: `KeyRef.material` must be ASCII-armored OpenPGP private key bytes

### Entry point

This package registers the `PGPCrypto` provider in the `swarmauri.cryptos` entry-point group.
