![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

Below is a minimal example demonstrating how the composite router delegates
operations to the first provider that advertises a given feature.  Providers can
also be selected explicitly via the `backend` option.

```python
import asyncio
from swarmauri_certs_composite import CompositeCertService
from swarmauri_core.certs.ICertService import ICertService
from swarmauri_core.crypto.types import (
    KeyRef,
    KeyType,
    KeyUse,
    ExportPolicy,
)


class CSRProvider(ICertService):
    """Handles CSR creation and certificate signing."""

    type = "CSR"

    def supports(self):
        return {"features": ("csr", "sign_from_csr")}

    async def create_csr(self, key, subject, **kw):
        return b"csr"

    async def sign_cert(self, csr, ca_key, **kw):
        return b"cert-from-csr"

    async def create_self_signed(self, *args, **kwargs):
        raise NotImplementedError

    async def verify_cert(self, *args, **kwargs):
        raise NotImplementedError

    async def parse_cert(self, *args, **kwargs):
        raise NotImplementedError


class SelfSignedProvider(ICertService):
    """Creates self-signed certificates and can sign CSRs."""

    type = "SELF"

    def supports(self):
        return {"features": ("self_signed", "sign_from_csr")}

    async def create_self_signed(self, key, subject, **kw):
        return b"self-signed"

    async def sign_cert(self, csr, ca_key, **kw):
        return b"cert-signed"

    async def create_csr(self, *args, **kwargs):
        raise NotImplementedError

    async def verify_cert(self, *args, **kwargs):
        raise NotImplementedError

    async def parse_cert(self, *args, **kwargs):
        raise NotImplementedError


async def main():
    svc = CompositeCertService([CSRProvider(), SelfSignedProvider()])
    key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.NONE,
    )
    subject = {"CN": "example.com"}

    csr = await svc.create_csr(key, subject)
    cert = await svc.sign_cert(csr, key, opts={"backend": "SELF"})
    self_signed = await svc.create_self_signed(key, subject)
    return csr, cert, self_signed


asyncio.run(main())
```

## Entry point

The provider is registered under the `swarmauri.certs` entry-point as `CompositeCertService`.
