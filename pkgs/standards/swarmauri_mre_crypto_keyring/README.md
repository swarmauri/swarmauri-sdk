![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_mre_crypto_keyring/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_keyring" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_keyring/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_keyring.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_keyring/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_mre_crypto_keyring" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_keyring/">
        <img src="https://img.shields.io/pypi/l/swarmauri_mre_crypto_keyring" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_keyring/">
        <img src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_keyring?label=swarmauri_mre_crypto_keyring&color=green" alt="PyPI - swarmauri_mre_crypto_keyring"/></a>
</p>

---

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
