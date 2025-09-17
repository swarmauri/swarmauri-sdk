![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_composite" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_composite/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_composite.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_composite" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_composite" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_composite?label=swarmauri_tokens_composite&color=green" alt="PyPI - swarmauri_tokens_composite"/></a>
</p>

---

## Swarmauri Token Composite

Algorithm-routing token service delegating to child providers based on JWT headers, claims, or algorithms.

## Features

- Compose multiple asynchronous `ITokenService` implementations behind a single `CompositeTokenService` facade.
- Dispatch mint requests by explicit service hints (`headers["svc"]`), token type headers (`headers["typ"]`), confirmation claims (`claims["cnf"]`), or requested algorithms.
- Detect verification routes from SSH certificate prefixes, JWT-style tokens (including DPoP and mTLS-bound variants), or fall back through each service until one succeeds.
- Merge child capability metadata and JWKS responses, de-duplicating keys by `kid` so downstream clients can rely on a single aggregated feed.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_tokens_composite
```

```bash
poetry add swarmauri_tokens_composite
```

If you use [uv](https://docs.astral.sh/uv/), install it (skip the first line if uv is already available) and then add the package:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install swarmauri_tokens_composite
```

## Usage

`CompositeTokenService` accepts a list of services implementing `ITokenService`.  It inspects headers, claims, and requested algorithms to choose the most appropriate delegate for `mint`, `verify`, and `jwks` calls.  The child services remain responsible for the actual cryptographic work, while the composite aggregates their capabilities and keys.

```python
# README Example: CompositeTokenService basic routing
import asyncio
from typing import Any, Dict, Iterable

from swarmauri_tokens_composite import CompositeTokenService


class MemoryTokenService:
    """In-memory stand-in for an async ITokenService implementation."""

    def __init__(self, type_name: str, formats: Iterable[str], algs: Iterable[str]):
        self.type = type_name
        self._formats = tuple(formats)
        self._algs = tuple(algs)

    def supports(self) -> Dict[str, Iterable[str]]:
        return {"formats": self._formats, "algs": self._algs}

    async def mint(
        self, claims: Dict[str, Any], *, alg: str, headers=None, **_: Any
    ) -> str:
        return f"{self.type}:{alg}:{claims['sub']}"

    async def verify(self, token: str, **kwargs) -> Dict[str, Any]:
        svc, alg, sub = token.split(":", 2)
        if svc != self.type:
            raise ValueError("routed to wrong service")
        return {"sub": sub, "alg": alg, "service": svc}

    async def jwks(self) -> Dict[str, Any]:
        return {"keys": [{"kid": f"{self.type}-kid"}]}


def build_composite() -> CompositeTokenService:
    jwt_service = MemoryTokenService("JWTTokenService", ["JWT"], ["HS256"])
    ssh_service = MemoryTokenService("SshCertTokenService", ["SSH-CERT"], ["ssh-ed25519"])
    return CompositeTokenService([jwt_service, ssh_service])


def describe_example(result: Dict[str, Any]) -> None:
    print("JWT token:", result["jwt_token"])
    print("SSH token:", result["ssh_token"])
    print("JWT service handled mint/verify:", result["jwt_claims"]["service"])
    print("SSH service handled mint/verify:", result["ssh_claims"]["service"])
    print("JWKS keys:", {entry["kid"] for entry in result["jwks"]["keys"]})


async def main() -> Dict[str, Any]:
    composite = build_composite()

    jwt_token = await composite.mint({"sub": "alice"}, alg="HS256")
    ssh_token = await composite.mint({"sub": "bob"}, alg="ssh-ed25519")

    jwt_claims = await composite.verify(jwt_token)
    ssh_claims = await composite.verify(ssh_token)
    jwks = await composite.jwks()

    return {
        "jwt_token": jwt_token,
        "ssh_token": ssh_token,
        "jwt_claims": jwt_claims,
        "ssh_claims": ssh_claims,
        "jwks": jwks,
    }


example_result = asyncio.run(main())
describe_example(example_result)
```

The example above shows how the composite selects different child services by algorithm while producing a merged JWKS response.  In production you would supply concrete implementations that speak to HSMs, remote signing services, or other secure key stores.

## Entry point

The provider is registered under the `swarmauri.tokens` entry-point as `CompositeTokenService`.
