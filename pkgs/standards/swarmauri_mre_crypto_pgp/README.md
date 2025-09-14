![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
import asyncio
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)
from swarmauri_mre_crypto_pgp import PGPMreCrypto


async def main():
    # Generate an OpenPGP key pair with pgpy
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Test User", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.EncryptCommunications},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )

    # Create references understood by the provider
    pub_ref = {"kind": "pgpy_pub", "pub": key.pubkey}
    priv_ref = {"kind": "pgpy_priv", "priv": key}

    # Encrypt for many and open with the private key
    mre = PGPMreCrypto()
    pt = b"hello"
    env = await mre.encrypt_for_many([pub_ref], pt)
    rt = await mre.open_for(priv_ref, env)
    print(rt)


if __name__ == "__main__":
    asyncio.run(main())
```

## Entry point

Providers are registered under the `swarmauri.mre_cryptos` entry-point as
`PGPSealMreCrypto`, `PGPSealedCekMreCrypto` and `PGPMreCrypto`.

