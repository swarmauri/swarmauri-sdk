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

OpenPGP-backed multi-recipient encryption provider implementing the `IMreCrypto` contract.

- Shared payload via AES-256-GCM or per-recipient sealed payloads
- Recipient protection via OpenPGP public-key encryption
- Supports rewrap operations

### Installation

```bash
pip install swarmauri_mre_crypto_pgp
```

## Entry point

The provider is registered under the `swarmauri.mre_crypto` entry-point as `PGPMreCrypto`.
