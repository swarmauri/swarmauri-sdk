![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

- Sealed-per-recipient X25519 stanzas (`mode="sealed_per_recipient"` and `recipient_alg="X25519-SEAL"`)
- ChaCha20-Poly1305 payload encryption for each recipient header
- Deterministic recipient identifiers via SHA-256 public key fingerprints
- Rewrapping support for adding or removing recipients when provided the original plaintext or an opening identity

### Installation

Choose the installer that matches your project workflow:

```bash
# pip
pip install swarmauri_mre_crypto_age

# Poetry
poetry add swarmauri_mre_crypto_age

# uv
uv add swarmauri_mre_crypto_age
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

The helper accepts multiple `KeyRef` formats, including dictionaries with
`kind="cryptography_obj"` (for `X25519PublicKey` / `X25519PrivateKey` objects)
and raw byte references such as `kind="raw_x25519_pk"` or `kind="age_x25519_pk"`.
When rewrapping an existing envelope to add recipients, pass the plaintext via
`opts["pt"]` or provide an identity through `opts["open_with"]` so the payload
can be resealed for the new recipients.

## Entry point

The provider is registered under the `swarmauri.mre_cryptos` entry-point as `AgeMreCrypto`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.