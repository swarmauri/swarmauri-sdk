![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_csronly" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_csronly/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_csronly.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_csronly" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_csronly" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_csronly?label=swarmauri_certs_csronly&color=green" alt="PyPI - swarmauri_certs_csronly"/></a>

</p>

---

# swarmauri_certs_csronly

A community-provided certificate service that builds PKCS#10 Certificate Signing Requests (CSRs).

## Features
- `CsrOnlyService` focused exclusively on generating standards-compliant PKCS#10 CSRs (RFC 2986).
- Supports RSA (2048/3072/4096), ECDSA (P-256), and Ed25519 private keys.
- Adds subject alternative names, challenge passwords, and basic constraints when needed.
- Designed to interoperate with other Swarmauri certificate services that handle issuance/verification.

## Prerequisites
- Python 3.10 or newer.
- PEM-encoded private key material available locally or via a `KeyRef` provider.
- Subject metadata (CN, O, OU, etc.) for the entity requesting a certificate.
- Optional: SAN entries, basic constraints, and challenge passwords when integrating with stricter PKI workflows.

## Installation

```bash
# pip
pip install swarmauri_certs_csronly

# poetry
poetry add swarmauri_certs_csronly

# uv (pyproject-based projects)
uv add swarmauri_certs_csronly
```

## Usage

Generate a CSR for `example.com` with SAN entries using an existing private key:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    key_ref = KeyRef(material=Path("example-key.pem").read_bytes())

    service = CsrOnlyService()
    csr_pem = await service.create_csr(
        key=key_ref,
        subject={"CN": "example.com", "O": "Example Inc"},
        san={"dns": ["example.com", "www.example.com"]},
    )

    Path("example.csr").write_bytes(csr_pem)
    print("CSR written to example.csr")


if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced CSR Options

Fine-tune extensions and output encoding for specialized PKI workflows:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.crypto.types import KeyRef


async def build_der_csr() -> None:
    key_ref = KeyRef(material=Path("root-ca-key.pem").read_bytes())

    service = CsrOnlyService()
    csr_der = await service.create_csr(
        key=key_ref,
        subject={"CN": "Example Root CA"},
        extensions={"basic_constraints": {"ca": True, "path_len": 0}},
        challenge_password="p@ssw0rd",
        output_der=True,
    )

    Path("root-ca.csr.der").write_bytes(csr_der)
    print("DER CSR saved to root-ca.csr.der")


if __name__ == "__main__":
    asyncio.run(build_der_csr())
```

## Best Practices
- Generate new key pairs and CSRs ahead of certificate expiry to allow review and approval time.
- Store private keys securely—`KeyRef` can reference hardware or cloud KMS-backed material rather than local files.
- Keep SAN lists minimal and auditable to avoid issuing overly permissive certificates.
- Pair this service with a signing backend (e.g., CFSSL, ACME, Azure Key Vault) to form a complete issuance pipeline.
