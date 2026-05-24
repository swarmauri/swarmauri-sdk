![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certs_csronly/">
        <img src="https://static.pepy.tech/badge/swarmauri_certs_csronly/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_csronly/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_csronly.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_csronly" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_csronly?label=swarmauri_certs_csronly&color=green" alt="PyPI - swarmauri_certs_csronly"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri CSR Only Certificate Service

`swarmauri_certs_csronly` provides `CsrOnlyService`, a focused Swarmauri certificate service for creating PKCS#10 certificate signing requests. It builds CSRs from PEM private key material in `KeyRef`, applies X.509 subject fields, optional subject alternative names, optional challenge passwords, and basic constraints, then returns PEM or DER CSR bytes.

## Why Swarmauri CSR Only Certificate Service?

Use this package when certificate issuance is handled by another CA, but Swarmauri code still needs a standards-aligned CSR generator. It is useful for ACME, CFSSL, Azure, local CA, and enterprise PKI workflows where key generation and request construction are separated from certificate signing.

## FAQ

### Q: Does this package issue certificates?

A: No. `CsrOnlyService` does not create self-signed certificates, sign certificates, verify certificates, or parse certificates. Those methods intentionally raise `NotImplementedError`.

### Q: What key types does it support?

A: `supports()` advertises RSA-2048, RSA-3072, RSA-4096, EC-P256, and Ed25519. Runtime signing uses `cryptography` private keys loaded from PEM bytes.

### Q: Which CSR features are implemented?

A: CSR creation supports common subject fields, DNS/IP/URI/email SAN entries, PKCS#9 challenge password attributes, basic constraints, and DER or PEM output.

### Q: Which standards does it align with?

A: The implementation targets PKCS#10 CSR generation from RFC 2986 and X.509 naming and extension semantics from RFC 5280.

## Features

- `CsrOnlyService` class registered under the `swarmauri.certs` entry point.
- PKCS#10 CSR creation from PEM private keys stored in `KeyRef.material`.
- Subject support for CN, C, ST, L, O, OU, and emailAddress.
- Subject alternative name support for DNS names, IP addresses, URIs, and email addresses.
- Optional challenge password attribute support.
- Optional basic constraints extension support.
- PEM output by default with DER output available through `output_der=True`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- PEM-encoded private key material available locally or through a `KeyRef` provider.
- Subject metadata for the certificate request.
- Optional SAN entries, basic constraints, and challenge passwords when required by the target CA.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certs_csronly
```

Install with `pip`:

```bash
pip install swarmauri_certs_csronly
```

## Usage

Generate a CSR for `example.com` with DNS SAN entries:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = CsrOnlyService()
    key_ref = KeyRef(material=Path("example-key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "example.com", "O": "Example Inc"},
        san={"dns": ["example.com", "www.example.com"]},
    )
    Path("example.csr").write_bytes(csr)


asyncio.run(main())
```

Create a DER-encoded CSR with a challenge password and basic constraints:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = CsrOnlyService()
    key_ref = KeyRef(material=Path("root-ca-key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "Example Root CA"},
        extensions={"basic_constraints": {"ca": True, "path_len": 0}},
        challenge_password="change-me",
        output_der=True,
    )
    Path("root-ca.csr.der").write_bytes(csr)


asyncio.run(main())
```

## Related Packages

Certificate service packages:

- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_azure](https://pypi.org/project/swarmauri_certs_azure/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Generate new key pairs and CSRs ahead of certificate expiry to allow review and approval time.
- Store private keys securely; `KeyRef` can reference hardware or cloud KMS backed material rather than local files.
- Keep SAN lists minimal and auditable to avoid overly broad certificate requests.
- Pair this service with a signing backend such as CFSSL, ACME, Azure, or a local CA package to form a complete issuance pipeline.

## License

Apache-2.0


