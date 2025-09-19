![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_mre_crypto_ecdh_es_kw/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_ecdh_es_kw" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_ecdh_es_kw/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_ecdh_es_kw.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_ecdh_es_kw/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_mre_crypto_ecdh_es_kw" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_ecdh_es_kw/">
        <img src="https://img.shields.io/pypi/l/swarmauri_mre_crypto_ecdh_es_kw" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_ecdh_es_kw/">
        <img src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_ecdh_es_kw?label=swarmauri_mre_crypto_ecdh_es_kw&color=green" alt="PyPI - swarmauri_mre_crypto_ecdh_es_kw"/></a>
</p>

---

## Swarmauri MRE Crypto ECDH-ES+A128KW

ECDH-ES+A128KW based multi-recipient encryption provider implementing the `IMreCrypto` contract.

### Capabilities

- Per-recipient ECDH-ES key agreement over `secp256r1`
- AES-128 Key Wrap (KW) of the derived content-encryption key
- AES-128-GCM payload encryption with optional additional authenticated data (AAD)
- Supported payload algorithm: `A128GCM`
- Supported recipient algorithm: `ECDH-ES+A128KW`
- Supported MRE mode: `MreMode.ENC_ONCE_HEADERS`
- Re-wrapping existing envelopes is not supported

### Installation

#### pip

```bash
pip install swarmauri_mre_crypto_ecdh_es_kw
```

#### Poetry

```bash
poetry add swarmauri_mre_crypto_ecdh_es_kw
```

#### uv

1. Install [`uv`](https://docs.astral.sh/uv/) if it is not already available:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Add the package to your environment:

   ```bash
   uv pip install swarmauri_mre_crypto_ecdh_es_kw
   ```

### Usage

The provider operates asynchronously. The example below demonstrates encrypting and decrypting a payload for a single
recipient whose key is provided as a `cryptography` object reference. The same `aad` (if provided) must be used for
both encryption and decryption.

```python
import asyncio

from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_mre_crypto_ecdh_es_kw import EcdhEsA128KwMreCrypto


async def main() -> None:
    crypto = EcdhEsA128KwMreCrypto()

    sk = ec.generate_private_key(ec.SECP256R1())
    pk = sk.public_key()
    recipient = {"kid": "1", "version": 1, "kind": "cryptography_obj", "obj": pk}

    envelope = await crypto.encrypt_for_many([recipient], b"secret", aad=b"metadata")
    plaintext = await crypto.open_for(
        {"kind": "cryptography_obj", "obj": sk}, envelope, aad=b"metadata"
    )

    assert plaintext == b"secret"


if __name__ == "__main__":
    asyncio.run(main())
```

### Entry point

The provider is registered under the `swarmauri.mre_cryptos` entry point as `EcdhEsA128KwMreCrypto`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.