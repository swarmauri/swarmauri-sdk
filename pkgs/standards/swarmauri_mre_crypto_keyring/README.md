<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


# Swarmauri MRE Crypto Keyring

Multi-recipient encryption provider using external keyrings/HSMs.

## Installation

```bash
pip install swarmauri_mre_crypto_keyring
```

## Usage

`KeyringMreCrypto` delegates CEK (content-encryption key) management to
user-provided keyring clients. Each client must implement `id`,
`wrap_cek`, and `unwrap_cek`. The example below shows how to register an
in-memory keyring and use it to encrypt and decrypt a payload.

```python
import asyncio
import secrets
from swarmauri_mre_crypto_keyring import KeyringMreCrypto


class MemoryKeyring:
    def __init__(self):
        self._store = {}

    def id(self) -> str:
        return "memory"

    async def wrap_cek(self, cek: bytes, *, context):
        token = secrets.token_bytes(8)
        self._store[token] = cek
        return token

    async def unwrap_cek(self, header: bytes, *, context):
        return self._store[header]


async def main():
    keyring = MemoryKeyring()
    keyref = {"kind": "keyring_client", "client": keyring}
    crypto = KeyringMreCrypto()
    env = await crypto.encrypt_for_many([keyref], b"sensitive data")
    recovered = await crypto.open_for(keyref, env)
    assert recovered == b"sensitive data"


asyncio.run(main())
```

The snippet encrypts `b"sensitive data"` for the memory keyring and
recovers the original plaintext using the same keyring client.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
