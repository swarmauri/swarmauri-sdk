# Swarmauri Vault Transit Key Provider

Community plugin providing a `KeyProvider` backed by the HashiCorp Vault Transit engine.

## Features
- Non-exportable secret keys managed by Vault
- JWKS export for RSA, EC P-256, and Ed25519 keys
- Local HKDF and RNG with optional Vault-backed randomness

## Installation
```bash
pip install swarmauri_keyprovider_vaulttransit
# or with optional CBOR canonicalization support
pip install swarmauri_keyprovider_vaulttransit[cbor]
```

## Usage
```python
from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, KeyUse, ExportPolicy

provider = VaultTransitKeyProvider(url="https://vault.example", token="s.xxxxx")
spec = KeySpec(
    klass=KeyClass.asymmetric,
    alg=KeyAlg.ED25519,
    uses=(KeyUse.SIGN, KeyUse.VERIFY),
    export_policy=ExportPolicy.PUBLIC_ONLY,
)
key_ref = await provider.create_key(spec)
```

## Testing
Unit, functional, and performance tests are located under `tests/` and
can be run with `pytest`.
