![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://static.pepy.tech/badge/swarmauri_keyprovider_vaulttransit/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_vaulttransit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_keyprovider_vaulttransit.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_vaulttransit" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_vaulttransit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_vaulttransit?label=swarmauri_keyprovider_vaulttransit&color=green" alt="PyPI - swarmauri_keyprovider_vaulttransit"/></a>
</p>

# Swarmauri Vault Transit Key Provider

`swarmauri_keyprovider_vaulttransit` provides `VaultTransitKeyProvider`, a Swarmauri key provider for HashiCorp Vault Transit key lifecycle and public-key metadata workflows. It creates and rotates non-exportable Vault Transit keys, returns Swarmauri `KeyRef` objects, exports public JWK and JWKS metadata, uses Vault or local random bytes, and derives key material with HKDF-SHA256.

## Why Swarmauri Vault Transit Key Provider?

Use this package when Swarmauri applications need Vault Transit-managed keys behind the shared key-provider interface. It keeps Vault client setup, Transit mount configuration, key creation, rotation, metadata lookup, public-key export, JWKS formatting, random bytes, and HKDF derivation in one component that can be combined with Swarmauri signing, token, certificate, and verifier packages.

## FAQ

### Q: Does this provider export private key material?

A: No. Keys created by this provider are marked non-exportable and disallow plaintext backup. `KeyRef.material` remains `None`.

### Q: Which Vault Transit key types can it create?

A: The provider maps Swarmauri algorithms to Vault Transit types: `AES256_GCM` to `aes256-gcm96`, RSA OAEP and RSA PSS to `rsa-3072`, ECDSA P-256 to `ecdsa-p256`, and Ed25519 to `ed25519`.

### Q: Does this package perform Vault Transit encrypt, decrypt, sign, or verify calls?

A: Not in the current implementation. The provider focuses on key lifecycle, public metadata, random bytes, and HKDF. Use or add dedicated crypto/signing components for Transit cryptographic operations.

### Q: How does JWKS export work?

A: `get_public_jwk()` exports or reads public PEM material from Vault, converts RSA, P-256, and Ed25519 public keys into JWK dictionaries, and returns symmetric keys as `oct` metadata. `jwks()` lists keys from the configured mount and returns a JWKS document.

## Features

- `VaultTransitKeyProvider` registered under the `swarmauri.key_providers` entry point.
- HashiCorp Vault client setup through `hvac` or an injected client.
- Transit mount configuration with optional Vault Enterprise namespace support.
- Non-exportable key creation for AES, RSA, ECDSA P-256, and Ed25519 workflows.
- Key rotation through Vault Transit `rotate_key`.
- Full key deletion or specific key-version destruction.
- Key version listing and latest-version metadata.
- Public JWK conversion for RSA, P-256, and Ed25519 public keys.
- JWKS document creation with optional key ID prefix filtering.
- Vault RNG support through `sys.generate_random_bytes()` with local `os.urandom` fallback.
- HKDF-SHA256 derivation helper.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- A running HashiCorp Vault server.
- Transit secrets engine enabled at the configured mount path, usually `transit`.
- Vault token authenticated for the needed Transit paths.
- Capabilities for key lifecycle paths such as `transit/keys/*`, export or read access for public key metadata, and optional access to `sys/tools/random` or equivalent random-byte APIs when `prefer_vault_rng=True`.
- TLS verification configuration appropriate for the Vault endpoint.

## Installation

Install with `uv`:

```bash
uv add swarmauri_keyprovider_vaulttransit
```

Install with `pip`:

```bash
pip install swarmauri_keyprovider_vaulttransit
```

The package also exposes optional extras:

```bash
pip install "swarmauri_keyprovider_vaulttransit[vault]"
pip install "swarmauri_keyprovider_vaulttransit[crypto]"
```

## Usage

Create and rotate a Vault Transit signing key:

```python
import asyncio

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider
from swarmauri_core.key_providers.types import ExportPolicy, KeyAlg, KeySpec


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="https://vault.example.com:8200",
        token="vault-token",
        mount="transit",
        verify="/etc/ssl/vault-ca.pem",
    )
    spec = KeySpec(
        alg=KeyAlg.ED25519,
        export_policy=ExportPolicy.never_export_secret,
        label="agents-signing",
    )

    key_ref = await provider.create_key(spec)
    rotated = await provider.rotate_key(key_ref.kid)

    print(key_ref.kid, key_ref.version)
    print(rotated.kid, rotated.version)


asyncio.run(main())
```

Publish a public JWK and JWKS document:

```python
import asyncio

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="https://vault.example.com:8200",
        token="vault-token",
    )

    jwk = await provider.get_public_jwk("agents-signing", 1)
    jwks = await provider.jwks(prefix_kids="agents")

    print(jwk["kid"])
    print([entry["kid"] for entry in jwks["keys"]])


asyncio.run(main())
```

Generate random bytes and derive key material:

```python
import asyncio

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="https://vault.example.com:8200",
        token="vault-token",
        prefer_vault_rng=True,
    )

    ikm = await provider.random_bytes(32)
    derived = await provider.hkdf(
        ikm,
        salt=b"vault-salt",
        info=b"swarmauri/key-derivation",
        length=32,
    )

    print(len(derived))


asyncio.run(main())
```

## Related Packages

Key provider packages:

- [swarmauri_keyprovider_aws_kms](https://pypi.org/project/swarmauri_keyprovider_aws_kms/)
- [swarmauri_keyprovider_gcpkms](https://pypi.org/project/swarmauri_keyprovider_gcpkms/)
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

- Use Vault policies with the narrowest Transit mount and key capabilities required by the workload.
- Prefer TLS verification with a pinned CA bundle for production Vault endpoints.
- Keep key lifecycle operations separate from runtime cryptographic operation policies.
- Use Vault namespaces explicitly when running on Vault Enterprise.
- Treat full key deletion and version destruction as irreversible operational events.

## License

Apache-2.0
