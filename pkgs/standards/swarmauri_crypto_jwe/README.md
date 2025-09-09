<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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

- Supports `dir`, `RSA-OAEP`, `RSA-OAEP-256`, and `ECDH-ES`
- Supports `A128GCM`, `A192GCM`, and `A256GCM`
- Optional compression (`zip` = `DEF`) and Additional Authenticated Data (AAD)

### Installation

```bash
pip install swarmauri_crypto_jwe
```

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
        alg="RSA-OAEP-256",
        enc="A256GCM",
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

**Parameters**

- `alg` – key management algorithm such as `RSA-OAEP-256` or `dir`.
- `enc` – content encryption algorithm like `A256GCM`.
- `key` – mapping containing the public key or direct symmetric key
  material.
- Decryption requires the matching private key via `rsa_private_pem`,
  `dir_key`, or `ecdh_private_key`.

## Entry point

The provider is registered under the `swarmauri.cryptos` entry point as `JweCrypto`.
