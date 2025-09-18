![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_ecdh_es_a128kw/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_ecdh_es_a128kw" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_ecdh_es_a128kw/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_ecdh_es_a128kw.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_ecdh_es_a128kw/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_ecdh_es_a128kw" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_ecdh_es_a128kw/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_ecdh_es_a128kw" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_ecdh_es_a128kw/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_ecdh_es_a128kw?label=swarmauri_crypto_ecdh_es_a128kw&color=green" alt="PyPI - swarmauri_crypto_ecdh_es_a128kw"/></a>

</p>

---

# swarmauri_crypto_ecdh_es_a128kw

ECDH-ES+A128KW key wrapping provider for Swarmauri.

## Highlights

- Implements the JSON Web Encryption ECDH-ES key agreement combined with AES Key Wrap using a 128-bit KEK (`ECDH-ES+A128KW`).
- Accepts `KeyRef` objects whose `public` attribute carries an EC public key in PEM format for wrapping and whose `material` attribute provides the corresponding private key for unwrapping.
- Derives a one-time key-encryption key via Concat KDF with SHA-256 and serializes results as JSON containing the ephemeral public key (`epk`) and wrapped DEK (`kw`), both Base64URL encoded.
- Generates a fresh 16-byte DEK when one is not provided so you can delegate symmetric key generation to the provider.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_crypto_ecdh_es_a128kw

# Poetry
poetry add swarmauri_crypto_ecdh_es_a128kw

# uv
uv add swarmauri_crypto_ecdh_es_a128kw
```

## Quickstart

The example below creates a recipient EC key pair, wraps a deterministic 128-bit DEK, and then unwraps it again to demonstrate the round trip. Run it with `python quickstart.py` or paste it into a REPL.

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_crypto_ecdh_es_a128kw import ECDHESA128KWCrypto


def make_recipient_key() -> KeyRef:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    return KeyRef(
        kid="recipient-key",
        version=1,
        type=KeyType.EC,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        public=public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )


async def main() -> None:
    crypto = ECDHESA128KWCrypto()
    recipient = make_recipient_key()
    dek = b"0123456789ABCDEF"  # 16 byte content encryption key

    wrapped = await crypto.wrap(recipient, dek=dek)
    recovered = await crypto.unwrap(recipient, wrapped)

    print("Wrapped payload:", wrapped.wrapped.decode("utf-8"))
    assert recovered == dek


if __name__ == "__main__":
    asyncio.run(main())
```

### What to expect

- `wrap` derives an ephemeral ECDH shared secret with the recipient public key, hashes it with Concat KDF (SHA-256) to produce a 128-bit KEK, and AES-KW wraps the provided DEK.
- The returned `WrappedKey` stores a JSON document containing the ephemeral public key (`epk`) and the wrapped DEK (`kw`), both Base64URL encoded.
- `unwrap` repeats the derivation using the recipient private key (`KeyRef.material`) and returns the original DEK bytes.

## License

`swarmauri_crypto_ecdh_es_a128kw` is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/LICENSE) file for details.

## Entry point

The provider is registered under the `swarmauri.cryptos` entry point as `ECDHESA128KWCrypto`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.