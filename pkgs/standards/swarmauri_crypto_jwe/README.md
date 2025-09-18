![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_jwe/"><img src="https://img.shields.io/pypi/dm/swarmauri_crypto_jwe" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_jwe/"><img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_jwe.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_jwe/"><img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_jwe" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_jwe/"><img src="https://img.shields.io/pypi/l/swarmauri_crypto_jwe" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_jwe/"><img src="https://img.shields.io/pypi/v/swarmauri_crypto_jwe?label=swarmauri_crypto_jwe&color=green" alt="PyPI - swarmauri_crypto_jwe"/></a>
</p>

---

## Swarmauri Crypto JWE

JSON Web Encryption (JWE) provider implementing RFC 7516 and RFC 7518 compliant encryption and decryption helpers.

### Features

- Asynchronous API for compact JWE serialization returning strings.
- Accepts `JWAAlg` enums from [`swarmauri_core.crypto.types`](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/core/swarmauri_core/crypto/types.py) for algorithms.
- Supports `dir`, `RSA-OAEP`, `RSA-OAEP-256`, and `ECDH-ES` key management algorithms.
- Supports `A128GCM`, `A192GCM`, and `A256GCM` content encryption.
- Optional compression (`zip` = `DEF`) and Additional Authenticated Data (AAD).
- Returns structured decrypt results that include both the protected header and plaintext.
- Registers with the Swarmauri PluginManager via the `swarmauri.cryptos` entry point.

### Installation

```bash
pip install swarmauri_crypto_jwe
# or
poetry add swarmauri_crypto_jwe
# or, with uv
uv add swarmauri_crypto_jwe
```

> [!TIP]
> `uv` can be installed with `pip install uv` or by following the instructions at [astral.sh/uv](https://docs.astral.sh/uv/). Once installed, run `uv add swarmauri_crypto_jwe` from your project directory to add the dependency.

### Usage

The helpers are asynchronous and return compact JWE strings that can be
decrypted back into their original plaintext. A typical flow is:

1. Generate or load the key material for the chosen algorithm.
2. Instantiate `JweCrypto`.
3. Call `encrypt_compact` with the payload, algorithm, and key details.
4. Call `decrypt_compact` with the resulting JWE and the corresponding
   private key.

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_crypto_jwe import JweCrypto


async def main() -> None:
    crypto = JweCrypto()

    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk_pem = sk.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    jwe = await crypto.encrypt_compact(
        payload=b"secret",
        alg=JWAAlg.RSA_OAEP_256,
        enc=JWAAlg.A256GCM,
        key={"pub": pk_pem},
    )

    result = await crypto.decrypt_compact(
        jwe,
        rsa_private_pem=sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )
    assert result.plaintext == b"secret"


asyncio.run(main())
```

### Loading via PluginManager

```python
from swarmauri.plugin import PluginManager

pm = PluginManager()
crypto = pm.load("swarmauri.cryptos", "JweCrypto")
```

**Parameters**

- `alg` – `JWAAlg` member describing the key management algorithm (`JWAAlg.RSA_OAEP_256`, `JWAAlg.DIR`, etc.).
- `enc` – `JWAAlg` member describing the content encryption algorithm (`JWAAlg.A256GCM`, `JWAAlg.A128GCM`, etc.).
- `key` – mapping containing the key material used for encryption:
  - `{"k": bytes}` for direct symmetric keys (`dir`).
  - `{"pub": rsa_public_key}` for RSA OAEP, where the public key may be PEM bytes or an `RSAPublicKey` instance.
  - `{"pub": ec_public_key}` for ECDH-ES with PEM, JWK, or key objects.
- Optional `header_extra` values are merged into the protected header (use `zip="DEF"` to enable compression).
- Decryption requires the matching private key via `dir_key`, `rsa_private_pem`/`rsa_private_password`, or `ecdh_private_key`.
- `expected_algs` and `expected_encs` constrain acceptable algorithms during decryption, and `aad` must match the authenticated data provided at encryption time.

## Entry point

The provider is registered under the `swarmauri.cryptos` entry point as `JweCrypto`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.