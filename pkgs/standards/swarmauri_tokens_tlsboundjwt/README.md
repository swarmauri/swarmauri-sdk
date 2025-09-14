![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_tlsboundjwt/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_tlsboundjwt" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_tlsboundjwt/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_tlsboundjwt.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_tlsboundjwt/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_tlsboundjwt" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_tlsboundjwt/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_tlsboundjwt" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_tlsboundjwt/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_tlsboundjwt?label=swarmauri_tokens_tlsboundjwt&color=green" alt="PyPI - swarmauri_tokens_tlsboundjwt"/></a>
</p>

---

# Swarmauri Tokens TLS-Bound JWT

A mutual-TLS bound JWT token service per [RFC 8705](https://www.rfc-editor.org/rfc/rfc8705).
It derives the `x5t#S256` confirmation claim from the current client certificate
and verifies that presented certificates match the token binding.

Features:
- Automatic `cnf` claim insertion with the SHA-256 thumbprint of the client certificate
- Verification that rejects tokens when the live certificate is missing or mismatched

## Installation

```bash
pip install swarmauri_tokens_tlsboundjwt
```

## Usage

```python
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_tokens_tlsboundjwt import TlsBoundJWTTokenService

svc = TlsBoundJWTTokenService(key_provider, client_cert_der_getter=my_cert_getter)
await svc.mint({"sub": "alice"}, alg=JWAAlg.HS256)
```

## Entry Point

The service registers under the `swarmauri.tokens` entry point as
`TlsBoundJWTTokenService`.
