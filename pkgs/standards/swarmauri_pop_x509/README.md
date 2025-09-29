![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_pop_x509/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_pop_x509" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_x509/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_pop_x509.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_x509/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_pop_x509" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_x509/">
        <img src="https://img.shields.io/pypi/l/swarmauri_pop_x509" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_pop_x509/">
        <img src="https://img.shields.io/pypi/v/swarmauri_pop_x509?label=swarmauri_pop_x509&color=green" alt="PyPI - swarmauri_pop_x509"/></a>
</p>

# Swarmauri PoP X.509

`X509PoPVerifier` validates mTLS client-certificate bindings for PoP-secured access tokens. It checks that the SHA-256 thumbprint of the presented certificate matches the `cnf.x5t#S256` value stored within the token confirmation claim.

## Installation

### pip

```bash
pip install swarmauri_pop_x509
```

### uv

```bash
uv add swarmauri_pop_x509
```

### Poetry

```bash
poetry add swarmauri_pop_x509
```

## Usage

The verifier consumes the normalised HTTP request alongside the `cnf` binding from the access token. Provide the peer certificate in DER form via the `extras` mapping when invoking `verify_http`.

```python
import asyncio
import ssl
from swarmauri_core.pop import CnfBinding, HttpParts, VerifyPolicy, BindType
from swarmauri_pop_x509 import X509PoPVerifier


async def main() -> None:
    verifier = X509PoPVerifier()
    cnf = CnfBinding(BindType.X5T_S256, "<thumbprint-from-token>")
    request = HttpParts(method="GET", url="https://api.example.com/resource", headers={})

    peer_cert_der = ssl.PEM_cert_to_DER_cert(open("client.pem", "r", encoding="utf-8").read())

    await verifier.verify_http(
        request,
        cnf,
        policy=VerifyPolicy(),
        extras={"peer_cert_der": peer_cert_der},
    )


asyncio.run(main())
```

`X509PoPVerifier` does not parse any detached proof artefact; the TLS handshake supplies the evidence. Only the certificate thumbprint comparison is performed, aligning with RFC 8705-style confirmation semantics.
