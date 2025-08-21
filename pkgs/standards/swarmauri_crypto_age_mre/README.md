![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_age_mre/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_age_mre" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_age_mre/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_age_mre.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_age_mre/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_age_mre" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_age_mre/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_age_mre" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_age_mre/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_age_mre?label=swarmauri_crypto_age_mre&color=green" alt="PyPI - swarmauri_crypto_age_mre"/></a>
</p>

---

## Swarmauri Crypto Age MRE

Age-based multi-recipient encryption provider implementing the `IMreCrypto` contract.

- Sealed-per-recipient X25519 stanzas
- ChaCha20-Poly1305 payload encryption
- Deterministic recipient identifiers via SHA-256 public key fingerprints

### Installation

```bash
pip install swarmauri_crypto_age_mre
```

### Usage

```python
from swarmauri_crypto_age_mre import AgeMreCrypto
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
