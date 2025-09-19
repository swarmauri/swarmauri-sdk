![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_paramiko/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_paramiko" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_paramiko/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_paramiko.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_paramiko/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_paramiko" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_paramiko/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_paramiko" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_paramiko/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_paramiko?label=swarmauri_crypto_paramiko&color=green" alt="PyPI - swarmauri_crypto_paramiko"/></a>
</p>

---

## Swarmauri Crypto Paramiko

Paramiko-backed crypto provider implementing the `ICrypto` contract via
`CryptoBase`. Built on top of [`paramiko`](https://www.paramiko.org/) and
[`cryptography`](https://cryptography.io/), it exposes an asynchronous API for
several cryptographic primitives using OpenSSH-formatted public keys and
PEM-encoded private keys supplied through `KeyRef` objects.

### Features

- AES-256-GCM symmetric encrypt/decrypt (16/24/32 byte keys)
- RSA-OAEP(SHA-256) wrap/unwrap for OpenSSH RSA key pairs
- AES-256-GCM key wrap/unwrap when the KEK is symmetric
- RSA-OAEP(SHA-256) sealing for small payloads
- Multi-recipient hybrid envelopes using OpenSSH public keys

Keys are represented by `KeyRef` objects. Public keys should be provided in
OpenSSH format via `KeyRef.public`, while private keys are supplied as
PEM-encoded bytes in `KeyRef.material`. RSA sealing is limited to inputs no
larger than the modulus-dependent RSA-OAEP bound (`modulus_bytes - 2 * hash_len
- 2`). For larger payloads use the hybrid envelope mode instead.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_crypto_paramiko

# Poetry
poetry add swarmauri_crypto_paramiko

# uv
uv add swarmauri_crypto_paramiko
```

## Usage

### Symmetric AEAD Encryption

```python
from swarmauri_crypto_paramiko import ParamikoCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = ParamikoCrypto()

sym = KeyRef(
    kid="sym1",
    version=1,
    type=KeyType.SYMMETRIC,
    uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=b"\x00" * 32,
)

ct = await crypto.encrypt(sym, b"hello")
pt = await crypto.decrypt(sym, ct)
```

### RSA Key Wrapping/Unwrapping

```python
import paramiko
from cryptography.hazmat.primitives import serialization
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = ParamikoCrypto()

key = paramiko.RSAKey.generate(2048)
pub_line = f"{key.get_name()} {key.get_base64()}\n".encode()
priv_pem = key.key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

recipient = KeyRef(
    kid="rsa1",
    version=1,
    type=KeyType.RSA,
    uses=(KeyUse.WRAP, KeyUse.UNWRAP),
    export_policy=ExportPolicy.PUBLIC_ONLY,
    public=pub_line,
    material=priv_pem,
)

wrapped = await crypto.wrap(recipient)
unwrapped = await crypto.unwrap(recipient, wrapped)
```

To wrap with a symmetric key-encryption key instead, provide the AES key bytes
in `KeyRef.material` and set `wrap_alg="AES-256-GCM"`:

```python
sym_kek = KeyRef(
    kid="kek1",
    version=1,
    type=KeyType.SYMMETRIC,
    uses=(KeyUse.WRAP, KeyUse.UNWRAP),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=b"\x01" * 32,
)

wrapped = await crypto.wrap(sym_kek, wrap_alg="AES-256-GCM")
plaintext_key = await crypto.unwrap(sym_kek, wrapped)
```

### RSA Sealing for Small Payloads

```python
# Using the `recipient` defined above
sealed = await crypto.seal(recipient, b"tiny secret")
plaintext = await crypto.unseal(recipient, sealed)
```

### Hybrid Envelope for Multiple Recipients

```python
env = await crypto.encrypt_for_many([recipient], b"secret")
```

Calling `encrypt_for_many` without overrides produces an AES-256-GCM ciphertext
shared by every recipient, while `env.recipients` holds RSA-OAEP-wrapped
session keys. Use `enc_alg="RSA-OAEP-SHA256-SEAL"` to emit individual RSA-OAEP
sealed payloads instead of a shared ciphertext when the plaintext fits within
the sealing size limit.

## Entry point

The provider is registered under the `swarmauri.cryptos` entry-point as `ParamikoCrypto`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.