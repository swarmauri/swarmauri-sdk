![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_azure" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_azure/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_azure.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_azure" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_azure" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_azure?label=swarmauri_certs_azure&color=green" alt="PyPI - swarmauri_certs_azure"/></a>

</p>

---

# swarmauri_certs_azure

Community-maintained utilities for working with X.509 certificates via Azure Key Vault.

## Features
- `AzureKeyVaultCertService` adapter that plugs into Swarmauri's certificate service architecture.
- RFC-aligned helpers for serial number generation (RFC 5280), PEM formatting (RFC 7468), and PKCS#10 CSR creation (RFC 2986).
- Native `DefaultAzureCredential` support so you can reuse the same authentication chain across tools.
- Works with RSA 2048-bit key material—perfect for Key Vault-backed certificate issuance flows.

## Prerequisites
- Python 3.10 or newer.
- An Azure Key Vault enabled for the Certificates and Keys resource providers.
- Exportable RSA key material (PEM) or an Azure Key Vault key that can be exported for CSR signing.
- Azure credentials configured for `DefaultAzureCredential` (e.g., `AZURE_CLIENT_ID`, managed identity, or CLI login).

## Installation

```bash
# pip
pip install swarmauri_certs_azure

# poetry
poetry add swarmauri_certs_azure

# uv (pyproject-based projects)
uv add swarmauri_certs_azure
```

## Quickstart

Generate a CSR using `AzureKeyVaultCertService` and store it for downstream issuance:

```python
import asyncio
from pathlib import Path

from azure.identity import DefaultAzureCredential

from swarmauri_certs_azure.certs import AzureKeyVaultCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AzureKeyVaultCertService(
        vault_url="https://example-vault.vault.azure.net/",
        credential=DefaultAzureCredential(),
    )

    key_ref = KeyRef(material=Path("app-private-key.pem").read_bytes())
    csr_bytes = await service.create_csr(
        key=key_ref,
        subject={"CN": "app.example.com"},
        san={"dns": ["app.example.com", "www.app.example.com"]},
    )

    Path("app.csr").write_bytes(csr_bytes)
    print("CSR written to app.csr")


if __name__ == "__main__":
    asyncio.run(main())
```

## Integrate with Azure Certificate Workflows

After generating the CSR, import it into Azure Key Vault or an external CA:

```python
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

vault_url = "https://example-vault.vault.azure.net/"
client = CertificateClient(vault_url=vault_url, credential=DefaultAzureCredential())

csr_bytes = Path("app.csr").read_bytes()

poller = client.begin_create_certificate(
    certificate_name="app-cert",
    policy={
        "contentType": "application/x-pem-file",
        "csr": csr_bytes,
    },
)

certificate = poller.result()
print("Certificate operation state:", certificate.properties.x509_thumbprint)
```

For external issuance, submit `app.csr` to your CA, then store the returned certificate chain back in Key Vault using `set_certificate_contacts` and `import_certificate`.

## Testing
Run tests with:
```bash
uv run --package swarmauri_certs_azure --directory community pytest
```

## Best Practices
- Prefer managed identities or workload identity federation over client secrets in production.
- Scope Key Vault permissions tightly (`get`, `sign`, `unwrapKey`) for the keys used by this service.
- Rotate keys and certificates ahead of expiry; the helper functions simplify CSR generation for renewals.
- Persist generated CSRs and issued certificates securely to aid in auditing and disaster recovery.
