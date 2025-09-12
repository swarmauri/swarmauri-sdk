![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_x509/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_x509" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_x509/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_x509.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_x509" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_x509" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_x509?label=swarmauri_certs_x509&color=green" alt="PyPI - swarmauri_certs_x509"/></a>

</p>

---

# swarmauri_certs_x509

X.509 certificate service plugin for Swarmauri using the `cryptography` library.

## Features
- Create CSRs
- Issue self-signed certificates
- Sign certificates with a CA
- Verify certificate chains

## RFC References
- [RFC 2986](https://datatracker.ietf.org/doc/html/rfc2986) – PKCS #10 Certification Request Syntax
- [RFC 5280](https://datatracker.ietf.org/doc/html/rfc5280) – Internet X.509 Public Key Infrastructure Certificate and CRL Profile

## Usage

The snippet below demonstrates creating a certificate authority (CA), issuing a
leaf certificate, and verifying the resulting chain.

```python
import asyncio
from swarmauri_certs_x509 import X509CertService
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

svc = X509CertService()

def make_key() -> KeyRef:
    sk = ed25519.Ed25519PrivateKey.generate()
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="k1",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
        public=None,
        tags={},
    )

ca_key = make_key()
ca_cert = asyncio.run(svc.create_self_signed(ca_key, {"CN": "Example CA"}))

leaf_key = make_key()
csr = asyncio.run(svc.create_csr(leaf_key, {"CN": "example.org"}))
leaf_cert = asyncio.run(svc.sign_cert(csr, ca_key, ca_cert=ca_cert))
result = asyncio.run(svc.verify_cert(leaf_cert, trust_roots=[ca_cert]))
assert result["valid"]
```

## Testing
Run unit, performance, and functional tests with:

```bash
uv run --package swarmauri_certs_x509 --directory standards/swarmauri_certs_x509 pytest
```
