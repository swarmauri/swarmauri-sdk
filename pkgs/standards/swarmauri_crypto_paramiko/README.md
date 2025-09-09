<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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

Paramiko-backed crypto provider implementing the `ICrypto` contract via `CryptoBase`.

- AES-256-GCM symmetric encrypt/decrypt
- RSA-OAEP(SHA-256) wrap/unwrap
- Multi-recipient hybrid envelopes using OpenSSH public keys

## Installation

```bash
pip install swarmauri_crypto_paramiko
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

### Hybrid Envelope for Multiple Recipients

```python
env = await crypto.encrypt_for_many([recipient], b"secret")
```

## Entry point

The provider is registered under the `swarmauri.cryptos` entry-point as `ParamikoCrypto`.
