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
from swarmauri_core.key_providers.types import KeySpec, KeyAlg, KeyClass
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

### CMS/S/MIME certificate profile

When preparing identities for CMS or S/MIME signing, include Email Protection
extended key usage and an email subject alternative name so that relying
parties can validate the certificate purpose.

```python
import asyncio
from swarmauri_core.crypto.types import KeyUse, ExportPolicy
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider


async def issue_smime_identity():
    provider = LocalKeyProvider()
    svc = X509CertService()

    ca_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ca_key = await provider.create_key(ca_spec)
    ca_cert = await svc.create_self_signed(
        ca_key,
        {"CN": "Demo CMS Root"},
        extensions={
            "basic_constraints": {"ca": True, "path_len": 0},
            "key_usage": {
                "digital_signature": True,
                "content_commitment": True,
                "key_cert_sign": True,
                "crl_sign": True,
            },
        },
    )

    leaf_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    leaf_key = await provider.create_key(leaf_spec)
    csr = await svc.create_csr(
        leaf_key,
        {"CN": "cms-signer.example", "emailAddress": "signer@example.org"},
        san={"email": ["signer@example.org"]},
    )
    leaf_cert = await svc.sign_cert(
        csr,
        ca_key,
        ca_cert=ca_cert,
        extensions={
            "basic_constraints": {"ca": False},
            "key_usage": {
                "digital_signature": True,
                "content_commitment": True,
            },
            "extended_key_usage": {"oids": ["emailProtection"]},
        },
    )

    return {
        "ca_cert": ca_cert,
        "leaf_cert": leaf_cert,
        "leaf_key_pem": leaf_key.material,
    }


bundle = asyncio.run(issue_smime_identity())
```

The `bundle` dictionary pairs neatly with ``swarmauri_signing_cms.CMSSigner`` by
supplying the `leaf_key_pem` together with the `leaf_cert` and `ca_cert`
entries as the PKCS#7 signing material.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.