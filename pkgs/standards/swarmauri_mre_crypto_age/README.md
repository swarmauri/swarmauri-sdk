<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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

The provider exposes asynchronous helpers for encrypting data to many
recipients and decrypting it for a specific private key.  The example below
walks through a complete round trip.

1. Create the crypto provider.
2. Generate key pairs for two recipients.
3. Encrypt a payload for both recipients.
4. Decrypt the payload for one recipient.

```python
from swarmauri_mre_crypto_age import AgeMreCrypto
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

crypto = AgeMreCrypto()

# generate key pairs for each participant
sk1 = X25519PrivateKey.generate()
pk1 = sk1.public_key()
sk2 = X25519PrivateKey.generate()
pk2 = sk2.public_key()

recipients = [
    {"kind": "cryptography_obj", "obj": pk1},
    {"kind": "cryptography_obj", "obj": pk2},
]

env = await crypto.encrypt_for_many(recipients, b"secret")
pt = await crypto.open_for({"kind": "cryptography_obj", "obj": sk1}, env)
assert pt == b"secret"
```

## Entry point

The provider is registered under the `swarmauri.mre_cryptos` entry-point as `AgeMreCrypto`.
