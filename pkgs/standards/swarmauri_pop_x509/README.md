![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

---

# Swarmauri PoP X.509

`swarmauri_pop_x509` validates mutual TLS certificate bindings for Swarmauri PoP
workflows. It matches presented client certificates against access-token
confirmation claims so downstream components can trust mTLS-provided identities.

## Features

- Implements `X509PoPVerifier` that matches SHA-256 thumbprints against `cnf`
  values for RFC 8705-style confirmation
- Reuses the shared Swarmauri PoP contract, allowing X.509 proofs to be
  interchanged with JWT- and COSE-based strategies
- Accepts asynchronous HTTP request parts and extra context so you can forward
  peer certificate material from proxies or API gateways
- Provides clear error messaging for missing certificates, mismatched thumbprints,
  or unsupported binding types

## Installation

```bash
pip install swarmauri_pop_x509
```

```bash
uv add swarmauri_pop_x509
```

## Usage

The verifier consumes the normalised HTTP request alongside the `cnf` binding
from the access token. Provide the peer certificate in DER form via the
`extras` mapping when invoking `verify_http`.

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

`X509PoPVerifier` does not parse any detached proof artefact; the TLS handshake
supplies the evidence. Only the certificate thumbprint comparison is performed,
mirroring the behaviour of OAuth 2.0 mutual TLS confirmation.

## Compatibility

- Python 3.10, 3.11, and 3.12
- Works with TLS termination layers that can forward peer certificates into the
  verification context
- Built on the same asynchronous verification contract exposed by
  `swarmauri_core`

## Related Packages

- [`swarmauri_pop_cwt`](../swarmauri_pop_cwt) for COSE Sign1 confirmation
- [`swarmauri_pop_dpop`](../swarmauri_pop_dpop) for Demonstrating Proof-of-
  Possession JWT headers
- [`swarmauri_core`](../../core) for the PoP abstractions and helpers that power
  all verification implementations

## Contributing

Changes and documentation updates should be proposed through the
[Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk). Run the
formatting, linting, and targeted tests outlined in the repository guides before
submitting pull requests.

## Support

For integration questions or bug reports, open an
[issue on GitHub](https://github.com/swarmauri/swarmauri-sdk/issues). Sensitive
security matters should follow the disclosure guidance referenced in the
repository security policy.

## License

Apache License 2.0. See the [LICENSE](./LICENSE) file for details.
