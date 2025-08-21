![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_mre_crypto_pgp/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_pgp" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_pgp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_pgp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_pgp/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_mre_crypto_pgp" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_pgp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_mre_crypto_pgp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_pgp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_pgp?label=swarmauri_mre_crypto_pgp&color=green" alt="PyPI - swarmauri_mre_crypto_pgp"/></a>
</p>

---

## Swarmauri MRE Crypto PGP

OpenPGP-based multi-recipient encryption providers implementing the
`IMreCrypto` contract. This package exposes three providers:

* **PGPSealMreCrypto** – per-recipient sealed payloads
  (`sealed_per_recipient` mode).
* **PGPSealedCekMreCrypto** – shared AEAD payload with per-recipient sealed
  CEK (`sealed_cek+aead` mode).
* **PGPMreCrypto** – composite provider supporting both the
  `enc_once+per_recipient_header` and `sealed_per_recipient` modes.

All providers use OpenPGP public key encryption via PGPy.

### Installation

```bash
pip install swarmauri_mre_crypto_pgp
```

### Usage

```python
from swarmauri_mre_crypto_pgp import PGPMreCrypto

mre = PGPMreCrypto()
```

## Entry point

Providers are registered under the `swarmauri.mre_cryptos` entry-point as
`PGPSealMreCrypto`, `PGPSealedCekMreCrypto` and `PGPMreCrypto`.

