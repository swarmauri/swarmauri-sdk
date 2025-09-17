![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
- Create standards-compliant CSRs
- Issue self-signed leaf or CA certificates
- Sign CSRs with an external CA key
- Verify certificate chains with optional intermediates
- Parse certificates to extract subject, issuer, validity, and extension metadata

## RFC References
- [RFC 2986](https://datatracker.ietf.org/doc/html/rfc2986) – PKCS #10 Certification Request Syntax
- [RFC 5280](https://datatracker.ietf.org/doc/html/rfc5280) – Internet X.509 Public Key Infrastructure Certificate and CRL Profile

## Installation

The package bundles both the local and in-memory key providers, so no
additional extras are required for the example below. Optional PKCS#11
support can be enabled when you need to integrate with hardware modules.

### pip

```bash
pip install swarmauri_certs_x509
# with PKCS#11 support
pip install 'swarmauri_certs_x509[pkcs11]'
```

### uv

```bash
uv pip install swarmauri_certs_x509
# or add to pyproject.toml and install dependencies
uv add swarmauri_certs_x509
uv sync
# enable PKCS#11
uv pip install 'swarmauri_certs_x509[pkcs11]'
```

### Poetry

```bash
poetry add swarmauri_certs_x509
# enable PKCS#11
poetry add swarmauri_certs_x509 --extras pkcs11
```

## Usage

The example below uses ``LocalKeyProvider`` to create a certificate
authority (CA), issue a leaf certificate, and verify the chain.

```python
import asyncio
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass
from swarmauri_core.crypto.types import KeyUse, ExportPolicy

svc = X509CertService()
kp = LocalKeyProvider()

spec = KeySpec(
    klass=KeyClass.asymmetric,
    alg=KeyAlg.ED25519,
    uses=(KeyUse.SIGN,),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
)

ca_key = asyncio.run(kp.create_key(spec))
ca_cert = asyncio.run(svc.create_self_signed(ca_key, {"CN": "Example CA"}))

leaf_key = asyncio.run(kp.create_key(spec))
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
