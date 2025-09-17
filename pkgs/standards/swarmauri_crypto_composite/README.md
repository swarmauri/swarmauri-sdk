![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_composite/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_composite" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_composite/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_composite.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_composite/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_composite" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_composite/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_composite" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_composite/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_composite?label=swarmauri_crypto_composite&color=green" alt="PyPI - swarmauri_crypto_composite"/></a>
</p>

---

## Swarmauri Crypto Composite

`CompositeCrypto` is an algorithm-routing crypto provider that delegates encryption
operations to the first child provider that advertises support for the requested
algorithm. Its behaviour is defined entirely by the wrapped providers:

- Aggregates each provider's `supports()` capabilities and removes duplicates.
- Normalises requested algorithms before routing so stylistic variants still match.
- Requires at least one child provider to be supplied at construction time.
- Exposes the full asynchronous `ICrypto` surface area (encrypt, wrap, seal, etc.).

## Installation

Choose the tool that best fits your workflow:

```bash
pip install swarmauri_crypto_composite
```

```bash
poetry add swarmauri_crypto_composite
```

```bash
uv add swarmauri_crypto_composite
```

## Usage

```python
"""Route crypto operations to the provider that supports the requested algorithm."""
import asyncio

from swarmauri_crypto_composite import CompositeCrypto
from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_core.crypto.types import (
    AEADCiphertext,
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)


class DummyCrypto(ICrypto):
    def __init__(self, name: str, alg: str) -> None:
        self._name = name
        self._alg = alg

    def supports(self):
        return {"encrypt": (self._alg,)}

    async def encrypt(self, key, pt, *, alg=None, aad=None, nonce=None):
        return AEADCiphertext(
            kid="dummy",
            version=1,
            alg=alg or self._alg,
            nonce=b"",
            ct=self._name.encode(),
            tag=b"",
        )

    async def decrypt(self, key, ct, *, aad=None):  # pragma: no cover - demo only
        raise NotImplementedError

    async def wrap(self, kek, *, dek=None, wrap_alg=None, nonce=None):  # pragma: no cover - demo only
        raise NotImplementedError

    async def unwrap(self, kek, wrapped):  # pragma: no cover - demo only
        raise NotImplementedError

    async def seal(self, recipient, pt, *, alg=None):  # pragma: no cover - demo only
        raise NotImplementedError

    async def unseal(self, recipient_priv, sealed, *, alg=None):  # pragma: no cover - demo only
        raise NotImplementedError


async def main() -> None:
    # Compose two providers that advertise different algorithms.
    chacha = DummyCrypto("chacha", "CHACHA20-POLY1305")
    aes = DummyCrypto("aes", "A256GCM")
    composite = CompositeCrypto([chacha, aes])

    key = KeyRef(
        kid="k",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ciphertext = await composite.encrypt(key, b"payload", alg="A256GCM")
    print(f"Selected provider: {ciphertext.ct.decode()}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Entry point

The provider is registered under the `swarmauri.cryptos` entry-point as `CompositeCrypto`.
