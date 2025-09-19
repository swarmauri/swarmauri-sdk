![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_mre_crypto_shamir" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_shamir/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_shamir.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_mre_crypto_shamir" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/">
        <img src="https://img.shields.io/pypi/l/swarmauri_mre_crypto_shamir" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_shamir/">
        <img src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_shamir?label=swarmauri_mre_crypto_shamir&color=green" alt="PyPI - swarmauri_mre_crypto_shamir"/></a>

</p>

---

# swarmauri_mre_crypto_shamir

Shamir Secret Sharing based multi-recipient encryption (MRE) provider for the Swarmauri framework. The provider splits an AES-256-GCM content encryption key using Shamir's threshold scheme and distributes shares to recipients.

## Features

- AES-256-GCM payload encryption
- Threshold k-of-n key sharing via Shamir secret sharing
- Envelope rewrapping with optional payload rotation
- Optional authenticated data (AAD) handling

## Extras

The plugin supports optional canonicalization extras:

- `cbor` – enables CBOR canonicalization via `cbor2`

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_mre_crypto_shamir

# Poetry
poetry add swarmauri_mre_crypto_shamir

# uv (project dependency)
uv add swarmauri_mre_crypto_shamir

# uv (one-off virtual environment)
uv pip install swarmauri_mre_crypto_shamir
```

Install extras, such as CBOR canonicalization support, with `swarmauri_mre_crypto_shamir[cbor]`.

## Quickstart

`ShamirMreCrypto` encrypts a payload with a fresh AES-256-GCM content encryption key, splits the key into Shamir shares, and stores the encrypted payload and shares in a multi-recipient envelope. Provide a threshold with `opts["threshold_k"]` (defaults to a simple majority) to control how many shares are required to decrypt.

```python
import asyncio

from swarmauri_mre_crypto_shamir import ShamirMreCrypto


async def main() -> None:
    provider = ShamirMreCrypto()

    recipients = [
        {"kid": "alice"},
        {"kid": "bob"},
        {"kid": "carol"},
    ]

    plaintext = b"Secret launch codes"

    envelope = await provider.encrypt_for_many(
        recipients,
        plaintext,
        opts={"threshold_k": 2},
    )

    print("Mode:", envelope["mode"])
    print("Recipients:", [entry["id"] for entry in envelope["recipients"]])
    print(
        "Threshold:",
        int.from_bytes(envelope["shared"]["threshold_k"], "big"),
    )

    recovered = await provider.open_for_many(
        [{"kid": "alice"}, {"kid": "carol"}],
        envelope,
    )

    assert recovered == plaintext
    print("Recovered plaintext:", recovered.decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
