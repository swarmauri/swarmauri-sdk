![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_secp256k1/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_secp256k1" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_secp256k1/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_secp256k1.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_secp256k1/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_secp256k1" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_secp256k1/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_secp256k1" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_secp256k1/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_secp256k1?label=swarmauri_signing_secp256k1&color=green" alt="PyPI - swarmauri_signing_secp256k1"/></a>
</p>

---

# Swarmauri Signing Secp256k1

An opinionated secp256k1 ECDSA signer that implements the Swarmauri
`ISigning` interface for detached signatures over raw bytes and
canonicalized envelopes.

## Features

- **Asynchronous API** – `sign_bytes`, `verify_bytes`, `sign_envelope`, and
  `verify_envelope` operate with `asyncio` and return canonical Swarmauri
  signature payloads.
- **Multiple canonicalizations** – JSON canonicalization is always
  available, while CBOR canonicalization can be enabled with the optional
  `cbor2` dependency.
- **Flexible key loading** – accepts PEM strings/paths, JWK dictionaries, or
  native `cryptography` key objects via the `KeyRef` protocol.
- **Deterministic verification requirements** – verification expects one or
  more secp256k1 public keys provided through `opts["pubkeys"]`.
- **Signature format control** – DER encoding is returned by default; supply
  `opts={"format": "RAW"}` when signing or verifying to work with
  JOSE-style `r || s` concatenated signatures.

## Installation

The package requires `cryptography` and, optionally, `cbor2` when CBOR
canonicalization is needed.

```bash
pip install swarmauri_signing_secp256k1

# install with CBOR canonicalization support
pip install "swarmauri_signing_secp256k1[cbor]"
```

```bash
poetry add swarmauri_signing_secp256k1
```

```bash
uv add swarmauri_signing_secp256k1

# with the optional CBOR extra
uv add "swarmauri_signing_secp256k1[cbor]"
```

## Usage

### Sign and verify raw bytes

The signer derives a key identifier (`kid`) from the provided private key and
requires the corresponding public key when verifying signatures.

<!-- example-start -->
```python
import asyncio

from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_secp256k1 import Secp256k1EnvelopeSigner


async def main() -> bool:
    signer = Secp256k1EnvelopeSigner()

    private_key = ec.generate_private_key(ec.SECP256K1())
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    payload = b"hello from secp256k1"
    signatures = await signer.sign_bytes(key_ref, payload)

    public_key_ref = {
        "kind": "cryptography_obj",
        "obj": private_key.public_key(),
    }
    is_valid = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [public_key_ref]},
    )

    print(f"Signature valid? {is_valid}")
    assert is_valid
    return is_valid


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- example-end -->

### Canonicalized envelopes

To sign envelopes, pass JSON-serializable dictionaries (and optionally
`canon="cbor"`). Canonicalization reuses the same raw signing logic shown
above:

```python
envelope = {"payload": {"msg": "hello"}}
signatures = await signer.sign_envelope(key_ref, envelope, canon="json")
is_valid = await signer.verify_envelope(
    envelope,
    signatures,
    opts={"pubkeys": [public_key_ref]},
)
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as
`Secp256k1EnvelopeSigner`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.