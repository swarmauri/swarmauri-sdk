![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_mre_crypto_age/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_age" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_age/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_age.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_age/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_mre_crypto_age" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_age/">
        <img src="https://img.shields.io/pypi/l/swarmauri_mre_crypto_age" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_age/">
        <img src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_age?label=swarmauri_mre_crypto_age&color=green" alt="PyPI - swarmauri_mre_crypto_age"/></a>
</p>

---

## Swarmauri MRE Crypto Age

Age-based multi-recipient encryption provider implementing the `IMreCrypto` contract.

- Sealed-per-recipient X25519 stanzas
- ChaCha20-Poly1305 payload encryption
- Deterministic recipient identifiers via SHA-256 public key fingerprints

### Installation

```bash
pip install swarmauri_mre_crypto_age
```

### Usage

```python
from swarmauri_mre_crypto_age import AgeMreCrypto
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

crypto = AgeMreCrypto()

sk = X25519PrivateKey.generate()
pk = sk.public_key()
recipient = {"kind": "cryptography_obj", "obj": pk}

env = await crypto.encrypt_for_many([recipient], b"secret")
pt = await crypto.open_for({"kind": "cryptography_obj", "obj": sk}, env)
```

## Entry point

The provider is registered under the `swarmauri.mre_cryptos` entry-point as `AgeMreCrypto`.
