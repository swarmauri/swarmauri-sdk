![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_mlkem/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_mlkem" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_mlkem/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_mlkem.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_mlkem/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_mlkem" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_mlkem/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_mlkem" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_mlkem/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_mlkem?label=swarmauri_crypto_mlkem&color=green" alt="PyPI - swarmauri_crypto_mlkem"/></a>
</p>

---

## Swarmauri Crypto ML-KEM

`swarmauri_crypto_mlkem` delivers a post-quantum key establishment provider for the
Swarmauri platform. It implements the `ICrypto` contract via `CryptoBase` using the
standardized [ML-KEM-768](https://csrc.nist.gov/publications/detail/fips/203/final)
(Kyber-768) algorithm for encapsulation and decapsulation operations.

### Features

- ML-KEM-768 key encapsulation (`seal`) producing raw Kyber ciphertexts
- ML-KEM-768 key decapsulation (`unseal`) recovering the 32-byte shared secret
- Key wrapping/unwrapping that serializes the shared secret into a `WrappedKey`
- Algorithm advertisement compatible with `CompositeCrypto` routing
- Strict `KeyRef` validation for `KeyType.MLKEM` materials and usage flags

## Installation

Install with the tool that fits your workflow:

```bash
# pip
pip install swarmauri_crypto_mlkem

# uv
uv add swarmauri_crypto_mlkem

# Poetry
poetry add swarmauri_crypto_mlkem
```

## Usage

```python
import asyncio
from pqcrypto.kem import kyber768

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_crypto_mlkem import MlKemCrypto

async def main() -> None:
    public, private = kyber768.generate_keypair()
    public_ref = KeyRef(
        kid="mlkem",
        version=1,
        type=KeyType.MLKEM,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=public,
    )
    private_ref = KeyRef(
        kid="mlkem",
        version=1,
        type=KeyType.MLKEM,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private,
    )

    crypto = MlKemCrypto()

    sealed = await crypto.seal(public_ref, b"")
    shared_secret = await crypto.unseal(private_ref, sealed)

    wrapped = await crypto.wrap(public_ref)
    recovered = await crypto.unwrap(private_ref, wrapped)
    assert shared_secret != recovered  # each encapsulation is randomized

asyncio.run(main())
```

## License

Licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license.
