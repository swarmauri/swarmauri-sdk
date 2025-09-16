![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_composite/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_composite" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_composite/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_composite.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_composite/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_composite" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_composite/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_composite" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_composite/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_composite?label=swarmauri_certs_composite&color=green" alt="PyPI - swarmauri_certs_composite"/></a>
</p>

---

## Swarmauri Certs Composite

`CompositeCertService` is a lightweight router that coordinates multiple
certificate providers behind a single facade. Configure it with the services
you already have (self-signed, ACME, Vault, PKCS#11, etc.) and the composite
chooses the right backend based on the feature you request.

### Highlights

- Compose any `ICertService` implementations into one entry point.
- Route automatically by declared capability or override explicitly per call.
- Inspect supported features at runtime to drive UI/UX decisions.
- Ship as the default `swarmauri.certs` plugin named `CompositeCertService`.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_certs_composite

# Poetry
poetry add swarmauri_certs_composite

# uv
uv add swarmauri_certs_composite
```

## Quickstart

The composite accepts a sequence of certificate service implementations and
routes each call to the first provider that advertises a matching capability.
Below is a self-contained example that you can run with `python quickstart.py`.

```python
import asyncio

from swarmauri_certs_composite import CompositeCertService
from swarmauri_base.certs.CertServiceBase import CertServiceBase


class SelfSignedOnly(CertServiceBase):
    def supports(self):
        return {"features": ("self_signed",)}

    async def create_self_signed(self, key, subject, **kw):
        return b"self-signed-cert"


class PrimaryCSR(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"primary-csr"


class SecondaryCSR(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"secondary-csr"


async def main():
    svc = CompositeCertService([SelfSignedOnly(), PrimaryCSR(), SecondaryCSR()])

    features = svc.supports()["features"]
    print("Advertised features:", sorted(features))

    cert = await svc.create_self_signed("key", {"CN": "example"})
    print("Self-signed cert:", cert)

    csr = await svc.create_csr("key", {"CN": "example"})
    print("CSR from primary provider:", csr)

    csr_override = await svc.create_csr(
        "key", {"CN": "example"}, opts={"backend": "SecondaryCSR"}
    )
    print("CSR via explicit backend override:", csr_override)


if __name__ == "__main__":
    asyncio.run(main())
```

`supports()` aggregates the advertised features of all child providers so callers
can inspect available capabilities before invoking them. Passing
`opts={"backend": "ProviderType"}` overrides the automatic routing when you
need to target a specific provider.

## For Contributors

If you want to contribute to `swarmauri_certs_composite`, please read our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
and
[style guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/STYLE_GUIDE.md)
to get started.

## License

`swarmauri_certs_composite` is licensed under the Apache License 2.0. See the
[LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/LICENSE) file
for details.

## Entry point

The provider is registered under the `swarmauri.certs` entry-point as `CompositeCertService`.
