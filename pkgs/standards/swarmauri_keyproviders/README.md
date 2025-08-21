![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Key Providers

Collection of key provider implementations for the Swarmauri SDK.  These
providers implement the `IKeyProvider` interface for managing symmetric and
asymmetric keys and exporting public material via JWK/JWKS.

## Providers

- `LocalKeyProvider` – local key generation and storage
- `SshKeyProvider` – interface to local SSH keys
- `Pkcs11KeyProvider` – PKCS#11 hardware-backed keys
- `RemoteJwksKeyProvider` – verification-only provider backed by remote JWKS

## Installation

```bash
pip install swarmauri_keyproviders
```

Optional extras are provided for specific key provider canons:

```bash
pip install swarmauri_keyproviders[pkcs11]  # enable PKCS#11 support
```
