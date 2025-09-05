![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

- ECDH-ES key agreement per recipient
- AES-128 Key Wrap of a shared content-encryption key
- AES-128-GCM payload encryption with optional AAD

### Installation

```bash
pip install swarmauri_mre_crypto_ecdh_es_kw
```

### Usage

```python
from cryptography.hazmat.primitives.asymmetric import ec
from swarmauri_mre_crypto_ecdh_es_kw import EcdhEsA128KwMreCrypto

crypto = EcdhEsA128KwMreCrypto()

sk = ec.generate_private_key(ec.SECP256R1())
pk = sk.public_key()
ref = {"kid": "1", "version": 1, "kind": "cryptography_obj", "obj": pk}

env = await crypto.encrypt_for_many([ref], b"secret")
pt = await crypto.open_for({"kind": "cryptography_obj", "obj": sk}, env)
```

## Entry point

The provider is registered under the `swarmauri.mre_cryptos` entry-point as `EcdhEsA128KwMreCrypto`.
