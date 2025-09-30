![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_pop_cwt/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_pop_cwt" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_cwt/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_cwt.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_cwt/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_pop_cwt" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_cwt/">
        <img src="https://img.shields.io/pypi/l/swarmauri_pop_cwt" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_cwt/">
        <img src="https://img.shields.io/pypi/v/swarmauri_pop_cwt?label=swarmauri_pop_cwt&color=green" alt="PyPI - swarmauri_pop_cwt"/></a>
</p>

# Swarmauri PoP CWT

`CwtPoPVerifier` and `CwtPoPSigner` provide COSE Sign1 proof-of-possession aligned with RFC 8392/9449 semantics. They reuse the shared Swarmauri PoP contract so that server code can validate JWT- and COSE-based schemes identically.

## Installation

### pip

```bash
pip install swarmauri_pop_cwt
```

### uv

```bash
uv add swarmauri_pop_cwt
```

### Poetry

```bash
poetry add swarmauri_pop_cwt
```

## Usage

### Signing a request

```python
import base64
from cose.algorithms import SignatureAlg
from cose.keys import CoseKey
from swarmauri_pop_cwt import CwtPoPSigner

private_key = CoseKey.from_dict({
    1: 1,               # OKP
    -1: 6,              # Ed25519
    -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g==")
})
public_key = CoseKey.from_dict({
    1: 1,
    -1: 6,
    -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g=="),
})

signer = CwtPoPSigner(
    private_key=private_key,
    public_key=public_key,
    algorithm=SignatureAlg.EdDSA,
)

cwp_header = signer.sign_request("GET", "https://api.example.com/resource")
print("CWP header:", cwp_header)
print("cnf:", signer.cnf_binding())
```

### Verifying an incoming HTTP request

```python
import asyncio
from cose.keys import CoseKey
from swarmauri_core.pop import CnfBinding, HttpParts, VerifyPolicy
from swarmauri_pop_cwt import CwtPoPVerifier


def memory_key_resolver(thumb: CnfBinding) -> CoseKey:
    return public_key


class ThumbResolver:
    def by_kid(self, kid: bytes):
        return None

    def by_thumb(self, bind: CnfBinding):
        return memory_key_resolver(bind)


async def verify_request(header: str, cnf: CnfBinding, access_token: str) -> None:
    verifier = CwtPoPVerifier()
    req = HttpParts(method="GET", url="https://api.example.com/resource", headers={"CWP": header})
    await verifier.verify_http(
        req,
        cnf,
        policy=VerifyPolicy(require_ath=True),
        keys=ThumbResolver(),
        extras={"access_token": access_token},
    )


asyncio.run(verify_request(cwp_header, signer.cnf_binding(), "opaque-access-token"))
```

The verifier enforces the COSE key thumbprint against the `cnf` claim and reuses the same replay/nonced handling controls defined for the JWT-based DPoP verifier.
