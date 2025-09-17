![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_dpop/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_dpop" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_dpop/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_dpop.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dpop/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_dpop" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dpop/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_dpop" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dpop/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_dpop?label=swarmauri_signing_dpop&color=green" alt="PyPI - swarmauri_signing_dpop"/></a>
</p>

# Swarmauri Signing DPoP

DPoP proof signer/verifier implementing RFC 9449 for proof-of-possession over HTTP requests.

Features:
- Creates and validates `dpop+jwt` proofs with embedded public JWK thumbprints.
- Supports `ES256`, `RS256`, and `EdDSA` algorithms through the `SigningBase` interface.
- Optional access-token hash binding (`ath`), nonce enforcement, and replay-protection hooks.

## Installation

The package is published on PyPI together with the dependencies required to sign and verify DPoP proofs.

### pip

```bash
pip install swarmauri_signing_dpop
```

### uv

```bash
uv add swarmauri_signing_dpop
```

### Poetry

```bash
poetry add swarmauri_signing_dpop
```

## Usage

`DpopSigner` implements the asynchronous `SigningBase` / `ISigning` interface. Signing requires the HTTP method and URL (`opts['htm']` and `opts['htu']`), and verification requires the same data passed via `require`.

### Signing and verifying a request

```python
import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_dpop import DpopSigner


async def main() -> None:
    signer = DpopSigner()

    private_key = ed25519.Ed25519PrivateKey.generate()
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key = {"kind": "pem", "priv": priv_pem, "alg": "EdDSA"}

    signatures = await signer.sign_bytes(
        key,
        b"",
        opts={"htm": "GET", "htu": "https://api.example/x"},
    )

    is_valid = await signer.verify_bytes(
        b"",
        signatures,
        require={"htm": "GET", "htu": "https://api.example/x"},
    )
    assert is_valid
    print("DPoP proof valid:", is_valid)


asyncio.run(main())
```

### Signature format

`sign_bytes` and `sign_envelope` return a sequence with a single detached signature entry:

```python
{
    "alg": "EdDSA",            # JWS algorithm used
    "format": "dpop+jwt",      # proof media type
    "sig": "<compact JWT>",    # DPoP proof token containing the claims
    "jkt": "<thumbprint>",     # SHA-256 JWK thumbprint for cnf.jkt binding
}
```

Use the `jkt` helper when comparing against `cnf.jkt` values embedded in access tokens.

### Key references

Keys are provided using the `KeyRef` mapping expected by other Swarmauri signing packages:

- `{ "kind": "pem", "priv": <PEM bytes|str> }` — RSA/EC keys and Ed25519 PKCS8 PEM.
- `{ "kind": "jwk", "priv": <private JWK dict> }` — accepts EC, RSA, or OKP keys with private fields.

For Ed25519 material, both formats are supported; the signer derives and embeds the public JWK automatically.

### Options reference

- `opts['htm']` / `opts['htu']`: HTTP method and URL that will be bound in the proof (required for signing).
- `opts['nonce']`: Optional server-issued `DPoP-Nonce` to include in the proof.
- `opts['access_token']`: Optional access token to derive the `ath` confirmation hash.
- `require['htm']` / `require['htu']`: Expected method and URL (required for verification).
- `require['max_skew_s']`: IAT skew tolerance (defaults to 300 seconds).
- `require['algs']`: Allowed signing algorithms. Defaults to all supported values.
- `require['nonce']`: Expected nonce when enforcing a server challenge.
- `require['access_token']`: Expected bearer token when validating `ath`.
- `require['replay']`: Mapping with `seen(jti) -> bool` and `mark(jti, ttl_s)` callables for replay prevention.

`sign_envelope` and `verify_envelope` reuse the same logic after canonicalizing the envelope to bytes (`raw` or `json`). Payload bytes are otherwise unused because the DPoP proof binds request metadata instead of message content.

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `DpopSigner`.
