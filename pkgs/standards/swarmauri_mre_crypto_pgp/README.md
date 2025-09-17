![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

OpenPGP-based multi-recipient encryption providers that implement the
`IMreCrypto` contract. The package includes three concrete providers, all of
which rely on [PGPy](https://pgpy.readthedocs.io/) for public-key encryption.
Providers that wrap a shared content-encryption key (CEK) additionally require
[`cryptography`](https://cryptography.io/en/latest/).

### Highlights

- **PGPSealMreCrypto** – Implements the `sealed_per_recipient` mode. Each
  recipient receives a sealed copy of the plaintext. Associated data (AAD) is
  not supported and re-wrapping new recipients requires the original plaintext
  via `opts["plaintext"]`.
- **PGPSealedCekMreCrypto** – Implements the `sealed_cek+aead` mode with an
  AES-256-GCM payload. The CEK is sealed per recipient and can be re-used to
  add or rotate recipients without decrypting the payload when
  `opts["cek"]` or `opts["opener_identities"]` are supplied.
- **PGPMreCrypto** – Composite provider supporting both
  `enc_once+per_recipient_header` (AES-256-GCM payload with OpenPGP headers)
  and `sealed_per_recipient`. Re-wrapping shared-payload envelopes requires the
  CEK via `opts["cek"]` or a managing private key supplied through
  `opts["manage_key"]`.

All providers fingerprint OpenPGP keys to derive recipient identifiers. Public
keys can be supplied as live `PGPKey` objects or ASCII-armored blobs using the
following recipient `KeyRef` forms:

- `{"kind": "pgpy_pub", "pub": pgpy.PGPKey}`
- `{"kind": "pgpy_pub_armored", "pub": "-----BEGIN PGP PUBLIC KEY-----"}`
- `{"kind": "pgpy_key", "key": pgpy.PGPKey}` (sealed CEK helper that lifts
  the public subkey from a combined key object)

Use these identity `KeyRef` forms when opening envelopes:

- `{"kind": "pgpy_priv", "priv": pgpy.PGPKey}`
- `{"kind": "pgpy_priv_armored", "priv": "-----BEGIN PGP PRIVATE KEY-----"}`
- `{"kind": "pgpy_key", "key": pgpy.PGPKey}` (sealed CEK provider)
- `{"kind": "pgpy_key_armored", "key": "-----BEGIN PGP PRIVATE KEY-----"}`

Private keys may be locked; pass the unlocking secret in `opts["passphrase"]`.

### Installation

Install the provider with your preferred packaging tool:

```bash
# pip
pip install swarmauri_mre_crypto_pgp

# Poetry
poetry add swarmauri_mre_crypto_pgp

# uv (project dependency)
uv add swarmauri_mre_crypto_pgp

# uv (virtualenv-only install)
uv pip install swarmauri_mre_crypto_pgp
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

### Selecting modes

`PGPMreCrypto` defaults to `MreMode.ENC_ONCE_HEADERS`. Pass
`mode=MreMode.SEALED_PER_RECIPIENT` (or the string value) to switch to the
sealed-per-recipient variant. `PGPSealedCekMreCrypto` always operates in the
`sealed_cek+aead` mode and will raise when the envelope mode or algorithms do
not match the expected values.

### Re-wrapping envelopes

- **Sealed per recipient** – Re-wrapping with additional recipients requires
  `opts["plaintext"]` so the providers can seal the original payload again.
- **Shared CEK (enc_once / sealed_cek)** – Supply either the decrypted CEK via
  `opts["cek"]` or provide identities capable of opening the envelope through
  `opts["manage_key"]` (composite provider) or
  `opts["opener_identities"]` (sealed CEK provider).
  Enable payload rotation with `opts["rotate_payload_on_revoke"]` to generate a
  fresh CEK when removing recipients.

## Entry point

Providers are registered under the `swarmauri.mre_cryptos` entry point as
`PGPSealMreCrypto`, `PGPSealedCekMreCrypto`, and `PGPMreCrypto`.

