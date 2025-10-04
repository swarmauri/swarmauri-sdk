![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

---

# Swarmauri PoP DPoP

`swarmauri_pop_dpop` enables RFC 9449 Demonstrating Proof-of-Possession flows for
Swarmauri services. The signer and verifier reuse the shared Swarmauri PoP
contract so applications can mix DPoP, CWT, and X.509 strategies interchangeably.

## Features

- Implements `DPoPSigner` and `DPoPVerifier` with consistent Swarmauri PoP
  semantics, including `cnf` generation and verification hooks
- Normalises HTTP method and URI handling to align with the DPoP
  specification, including support for query strings and ports
- Provides nonce and replay integration points so you can plug in
  application-specific storage to enforce single-use proofs
- Validates `ath` hashes for OAuth access tokens to ensure request binding when
  PoP is layered on bearer credentials

## Installation

```bash
pip install swarmauri_pop_dpop
```

```bash
uv add swarmauri_pop_dpop
```

## Usage

### Signing an outgoing HTTP request

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

The verifier enforces thumbprints for the provided JWK, checks nonce and replay
constraints, and validates `ath` hashes when bearer tokens are provided.

## Compatibility

- Python 3.10, 3.11, and 3.12
- Asynchronous contexts that can dispatch `HttpParts` instances from
  `swarmauri_core`
- Intended for OAuth 2.0 servers, API gateways, and microservices that need to
  accept Demonstration of Proof-of-Possession headers

## Related Packages

- [`swarmauri_pop_cwt`](../swarmauri_pop_cwt) for COSE-based confirmation
- [`swarmauri_pop_x509`](../swarmauri_pop_x509) to validate mutual TLS
  thumbprints using the same `cnf` contract
- [`swarmauri_core`](../../core) which defines the PoP primitives consumed by all
  Swarmauri proof strategies

## Contributing

Please contribute improvements through the
[Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk). Ensure
tests, formatting, and linting match the root instructions and describe your
changes clearly in pull requests so reviewers understand the intended impact.

## Support

Need help integrating DPoP in Swarmauri? File an
[issue on GitHub](https://github.com/swarmauri/swarmauri-sdk/issues) with
implementation details and reproduction steps. For security disclosures, use the
contact information listed in the repository security policy.

## License

Apache License 2.0. See the [LICENSE](./LICENSE) file for details.
