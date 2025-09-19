![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_self_signed/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_self_signed" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_self_signed/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_self_signed.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_self_signed/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_self_signed" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_self_signed/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_self_signed" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_self_signed/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_self_signed?label=swarmauri_certs_self_signed&color=green" alt="PyPI - swarmauri_certs_self_signed"/></a>
</p>

---

# Swarmauri Self-Signed Certificate Builder

Standalone plugin providing utilities to issue self-signed X.509 certificates using the `SelfSignedCertificate` builder.

## Features

- Issue PEM (default) or DER encoded self-signed certificates from existing private keys.
- Populate subjects, subject alternative names, name constraints, and key usage extensions via simple dictionaries.
- Convenience constructors for common TLS server and mTLS client certificates.
- Automatically reuse a passphrase stored in `KeyRef.tags["passphrase"]` when loading encrypted keys.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_certs_self_signed

# Poetry
poetry add swarmauri_certs_self_signed

# uv
uv add swarmauri_certs_self_signed
```

## Quickstart

`SelfSignedCertificate` operates on a `KeyRef` whose `material` holds the PEM encoded private key. The example below generates an Ed25519 key, issues a TLS server certificate with DNS subject alternative names, and prints the PEM header of the resulting certificate.

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_certs_self_signed import SelfSignedCertificate

private_key = ed25519.Ed25519PrivateKey.generate()
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

key_ref = KeyRef(
    kid="example-ed25519",
    version=1,
    type=KeyType.ED25519,
    uses=(KeyUse.SIGN,),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=private_bytes,
)

builder = SelfSignedCertificate.tls_server(
    common_name="example.local",
    dns_names=["example.local", "api.example.local"],
)

certificate_pem = builder.issue(key_ref)
print(certificate_pem.decode().splitlines()[0])
```

The builder automatically mirrors the TLS server defaults: the subject common name is set from `common_name`, all DNS names are added to the SAN extension, and the certificate is valid for 397 days unless overridden. Set `output_der=True` on the builder to receive DER encoded bytes instead of PEM.

## Entry Point

This package registers `SelfSignedCertificate` under both the `swarmauri.cert_services` and `peagen.plugins.cert_services` entry points.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.