![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_pop_dpop/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_pop_dpop" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_dpop/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_dpop.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_dpop/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_pop_dpop" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_dpop/">
        <img src="https://img.shields.io/pypi/l/swarmauri_pop_dpop" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_dpop/">
        <img src="https://img.shields.io/pypi/v/swarmauri_pop_dpop?label=swarmauri_pop_dpop&color=green" alt="PyPI - swarmauri_pop_dpop"/></a>
</p>

# Swarmauri PoP DPoP

`DPoPVerifier` and `DPoPSigner` provide RFC 9449 proof-of-possession for HTTP requests. The verifier enforces `htm`/`htu` bindings, supports nonce and replay hooks, and validates `ath` claims against server-provided access tokens.

## Installation

### pip

```bash
pip install swarmauri_pop_dpop
```

### uv

```bash
uv add swarmauri_pop_dpop
```

### Poetry

```bash
poetry add swarmauri_pop_dpop
```

## Usage

### Signing a request

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

from swarmauri_pop_dpop import DPoPSigner

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

public_jwk = {
    "kty": "OKP",
    "crv": "Ed25519",
    "x": base64.urlsafe_b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    ).rstrip(b"=").decode("ascii"),
}

signer = DPoPSigner(
    private_key=private_key,
    public_jwk=public_jwk,
    algorithm="EdDSA",
)

dpop_header = signer.sign_request("GET", "https://api.example.com/resource")
print("DPoP header:", dpop_header)
print("cnf:", signer.cnf_binding())
```

### Verifying an incoming HTTP request

```python
import asyncio
from typing import Mapping

from swarmauri_core.pop import CnfBinding, HttpParts, VerifyPolicy
from swarmauri_pop_dpop import DPoPVerifier


class MemoryReplay:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def seen(self, scope: str, key: str) -> bool:
        return f"{scope}:{key}" in self._seen

    def mark(self, scope: str, key: str, ttl_s: int) -> None:
        self._seen.add(f"{scope}:{key}")


async def verify_request(headers: Mapping[str, str], cnf: CnfBinding, access_token: str) -> None:
    verifier = DPoPVerifier()
    req = HttpParts(method="GET", url="https://api.example.com/resource", headers=headers)
    await verifier.verify_http(
        req,
        cnf,
        policy=VerifyPolicy(require_ath=True),
        replay=MemoryReplay(),
        extras={"access_token": access_token},
    )


asyncio.run(verify_request({"DPoP": dpop_header}, signer.cnf_binding(), "opaque-access-token"))
```

The verifier automatically enforces the JWK thumbprint against the `cnf` value from the access token and uses the provided replay hook to reject reused `jti` values within the configured skew window.
