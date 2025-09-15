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

Routing certificate service delegating to child providers based on requested features.

## Installation

```bash
pip install swarmauri_certs_composite
```

## Usage

The composite accepts a sequence of certificate service implementations and
routes each call to the first provider that advertises a matching capability.
Below is a minimal example using two toy providers:

```python
from swarmauri_certs_composite import CompositeCertService
from swarmauri_base.certs.CertServiceBase import CertServiceBase


class SelfSignedOnly(CertServiceBase):

    def supports(self):
        return {"features": ("self_signed",)}

    async def create_self_signed(self, key, subject, **kw):
        return b"self-signed-cert"


class CsrOnly(CertServiceBase):

    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"csr-data"


svc = CompositeCertService([SelfSignedOnly(), CsrOnly()])

# create a self-signed certificate - routed to SelfSignedOnly
cert = await svc.create_self_signed("key", {"CN": "example"})

# create a CSR and explicitly route to the second provider by class name
csr = await svc.create_csr("key", {"CN": "example"}, opts={"backend": "CsrOnly"})
```

`supports()` aggregates the advertised features of all child providers,
allowing callers to inspect available capabilities before invoking them.

## Entry point

The provider is registered under the `swarmauri.certs` entry-point as `CompositeCertService`.
