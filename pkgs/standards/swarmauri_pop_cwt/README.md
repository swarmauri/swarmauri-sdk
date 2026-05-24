![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_pop_cwt/">
        <img src="https://static.pepy.tech/badge/swarmauri_pop_cwt/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_cwt/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_cwt.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_cwt/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_cwt/">
        <img src="https://img.shields.io/pypi/l/swarmauri_pop_cwt" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_cwt/">
        <img src="https://img.shields.io/pypi/v/swarmauri_pop_cwt?label=swarmauri_pop_cwt&color=green" alt="PyPI - swarmauri_pop_cwt"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri PoP CWT

`swarmauri_pop_cwt` delivers COSE Sign1 proof-of-possession helpers that align with
RFC 8392 and RFC 9449. The signer and verifier share the same Swarmauri PoP
contract so services can mix CWT- and JWT-backed access tokens without changing
validation logic.

## Features

- Provides `CwtPoPSigner` and `CwtPoPVerifier` implementations that honour the
  shared Swarmauri PoP contract
- Accepts asynchronous key resolution hooks for COSE thumbprint matching and
  supports nonce/replay protections consistent with the DPoP workflow
- Generates `cnf` bindings that can be embedded into OAuth access tokens or
  session metadata to enable downstream verification
- Normalises HTTP request parts before signing or verifying to ensure
  interoperable coverage across services and languages

## Installation

Install the package with your preferred tooling:

```bash
pip install swarmauri_pop_cwt
```

```bash
uv add swarmauri_pop_cwt
```

## Usage

### Signing an outgoing HTTP request

```python
import base64
from cose.algorithms import SignatureAlg
from cose.keys import CoseKey
from swarmauri_pop_cwt import CwtPoPSigner

private_key = CoseKey.from_dict({
    1: 1,  # OKP
    -1: 6,  # Ed25519
    -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g=="),
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

The verifier enforces COSE key thumbprints against the `cnf` binding and applies
the same replay and nonce strategies shared across Swarmauri PoP strategies.

## Compatibility

- Python 3.10, 3.11, and 3.12
- Works alongside the shared `swarmauri_core.pop` abstractions and any
  asynchronous framework that can supply an `HttpParts` payload
- Designed to operate with HTTP gateways that forward method, URL, and header
  information for downstream validation

## Related Packages

- [`swarmauri_pop_dpop`](../swarmauri_pop_dpop) for JWT-based Demonstration of
  Proof-of-Possession headers
- [`swarmauri_pop_x509`](../swarmauri_pop_x509) when mutual TLS confirmation is
  required
- [`swarmauri_core`](../../core) for the shared PoP contract, HTTP primitives,
  and error hierarchy leveraged by all PoP implementations

## Contributing

Contributions are welcome through the
[Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk). Follow
the project style guide, run the formatting and linting commands noted in the
root `AGENTS.md`, and open pull requests with focused commits that describe the
improvement.

## Support

If you encounter issues integrating Swarmauri PoP CWT flows, please open a
[GitHub issue](https://github.com/swarmauri/swarmauri-sdk/issues) with details
about your environment and the expected versus observed behaviour. Security
concerns should be responsibly disclosed via the contact details in the
repository security policy.

## License

Apache License 2.0. See the [LICENSE](./LICENSE) file for details.


