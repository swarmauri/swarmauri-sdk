![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_vaulttransit" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_vaulttransit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_vaulttransit.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_vaulttransit" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_vaulttransit" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_vaulttransit?label=swarmauri_keyprovider_vaulttransit&color=green" alt="PyPI - swarmauri_keyprovider_vaulttransit"/></a>
</p>

---

# Swarmauri Vault Transit Key Provider

HashiCorp Vault Transit engine integration for the Swarmauri key provider interface. Manage hardware-protected keys through Vault, expose public JWK(S) material, rotate versions, and consume Vault RNG and HKDF services without leaving Swarmauri.

## Features

- Create and rotate symmetric (`aes256-gcm96`) and asymmetric (`rsa-3072`, `ecdsa-p256`, `ed25519`) keys via Vault Transit.
- Export public keys in JWK/JWKS form using the built-in `get_public_jwk`/`jwks` helpers.
- Perform signing, verification, encryption, decryption, wrapping, and unwrapping through Vault's REST API.
- Generate cryptographically secure random bytes either from Vault's RNG or local entropy (configurable with `prefer_vault_rng`).
- Run HKDF derivations with SHA-256 to support envelope encryption or key diversification workflows.

## Prerequisites

- Python 3.10 or newer.
- Running HashiCorp Vault instance with the Transit secrets engine enabled and a mount path you can access (default `transit`).
- Vault token with capabilities such as `transit/keys/*` for `read`, `create`, `update`, `delete`, and `transit/random/*` if you plan to use Vault RNG.
- The [`hvac`](https://pypi.org/project/hvac/) client library (installed automatically with this package) unless you inject a custom Vault client.

## Installation

```bash
# pip
pip install swarmauri_keyprovider_vaulttransit

# poetry
poetry add swarmauri_keyprovider_vaulttransit

# uv (pyproject-based projects)
uv add swarmauri_keyprovider_vaulttransit
```

## Quickstart: Create and Rotate a Signing Key

```python
import asyncio
from swarmauri_core.keys.types import KeyAlg, KeySpec, ExportPolicy
from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="http://localhost:8200",
        token="swarmauri-dev-token",
        mount="transit",
        verify=False,
    )

    spec = KeySpec(
        alg=KeyAlg.ED25519,
        export_policy=ExportPolicy.never_export_secret,
        label="agents-signing",
    )

    key_ref = await provider.create_key(spec)
    print("Created key", key_ref.kid, "version", key_ref.version)

    jwk = await provider.get_public_jwk(key_ref.kid, key_ref.version)
    print("Public JWK", jwk)

    rotated = await provider.rotate_key(key_ref.kid)
    print("Rotated to version", rotated.version)

    jwks_payload = await provider.jwks()
    print("JWKS contains", [entry["kid"] for entry in jwks_payload["keys"]])


if __name__ == "__main__":
    asyncio.run(main())
```

## Encrypt, Wrap, and Derive Keys

```python
import asyncio
from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider


async def encrypt_and_wrap() -> None:
    provider = VaultTransitKeyProvider(
        url="http://localhost:8200",
        token="swarmauri-dev-token",
        prefer_vault_rng=True,
    )

    plaintext = b"vault keeps my secrets"
    aad = b"tenant::demo"

    ciphertext = await provider.encrypt("aes-encryption", plaintext, associated_data=aad)
    decrypted = await provider.decrypt("aes-encryption", ciphertext, associated_data=aad)
    assert decrypted == plaintext

    dek = await provider.random_bytes(32)
    wrapped = await provider.wrap("rsa-wrap-key", dek)
    unwrapped = await provider.unwrap("rsa-wrap-key", wrapped)
    assert unwrapped == dek

    derived = await provider.hkdf(
        ikm=dek,
        salt=b"vault-salt",
        info=b"swarmauri/derivation",
        length=32,
    )
    print("Derived key length", len(derived))


# asyncio.run(encrypt_and_wrap())
```

## Configuration Reference

- `url` – Vault server address (e.g., `https://vault.example.com:8200`).
- `token` – Vault token or wrapped token with permissions for the Transit mount.
- `mount` – Transit engine mount path; defaults to `transit`.
- `namespace` – Optional Vault Enterprise namespace header.
- `verify` – TLS verification flag or CA bundle path.
- `prefer_vault_rng` – When `True`, `random_bytes` uses Vault's RNG; otherwise falls back to `os.urandom`.
- `client` – Provide a pre-configured `hvac.Client` if you manage authentication externally.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).
