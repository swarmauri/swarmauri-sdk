![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certs_azure/">
        <img src="https://static.pepy.tech/badge/swarmauri_certs_azure/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_azure/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_azure.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_azure" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_azure?label=swarmauri_certs_azure&color=green" alt="PyPI - swarmauri_certs_azure"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Azure Key Vault Certificate Service

`swarmauri_certs_azure` provides `AzureKeyVaultCertService`, a Swarmauri certificate-service adapter for Azure-oriented certificate workflows. The current implementation authenticates with Azure credentials, prepares an Azure Key Vault key client, and creates PKCS#10 certificate signing requests from exportable PEM private key material supplied through Swarmauri `KeyRef` objects.

## Why Swarmauri Azure Key Vault Certificate Service?

Use this package when a Swarmauri deployment needs certificate request generation that fits Azure Key Vault operational patterns. It gives certificate code one Swarmauri interface while preserving Azure authentication through `DefaultAzureCredential` and keeping CSR construction, RFC 5280 serial helpers, and RFC 7468 PEM formatting in a package-local certificate service.

## FAQ

### Q: Does this package create certificates directly in Azure Key Vault?

A: Not in the current runtime implementation. It creates CSRs from exportable private key material and prepares an Azure Key Vault key client. Azure certificate creation, import, and lifecycle operations should be handled by the surrounding Azure workflow.

### Q: What standards does it cover?

A: The package includes PKCS#10 CSR creation, RFC 5280-style serial number generation helpers, and RFC 7468 PEM certificate formatting helpers.

### Q: What credential model does it use?

A: `AzureKeyVaultCertService` uses a caller-provided Azure credential or falls back to `DefaultAzureCredential`, which supports local developer login, managed identity, workload identity, and service-principal flows supported by Azure Identity.

### Q: What key material is required?

A: The implemented CSR path requires exportable PEM private key material in `KeyRef.material`. Non-exportable Key Vault signing is not implemented by this simplified service.

## Features

- `AzureKeyVaultCertService` class for Swarmauri certificate-service workflows.
- Azure Identity integration through `DefaultAzureCredential` or a caller-provided credential.
- Azure Key Vault key client construction for the configured vault URL.
- PKCS#10 CSR creation from PEM private keys.
- Common-name subject handling for CSR generation.
- RFC 5280-oriented serial number helper.
- RFC 7468 PEM certificate formatting helper.
- Capability metadata reporting RSA-2048, RSA-SHA256, and CSR support.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certs_azure
```

Install with `pip`:

```bash
pip install swarmauri_certs_azure
```

## Usage

Create a service for an Azure Key Vault URL:

```python
from azure.identity import DefaultAzureCredential

from swarmauri_certs_azure.certs import AzureKeyVaultCertService

service = AzureKeyVaultCertService(
    "https://example-vault.vault.azure.net/",
    credential=DefaultAzureCredential(),
)

print(service.supports()["features"])
```

Generate a CSR from local exportable key material:

```python
import asyncio
from pathlib import Path

from azure.identity import DefaultAzureCredential

from swarmauri_certs_azure.certs import AzureKeyVaultCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AzureKeyVaultCertService(
        "https://example-vault.vault.azure.net/",
        credential=DefaultAzureCredential(),
    )
    key_ref = KeyRef(material=Path("app-private-key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "app.example.com"},
    )
    Path("app.csr").write_bytes(csr)


asyncio.run(main())
```

Check helper behavior for PEM output:

```python
from swarmauri_certs_azure.certs.AzureKeyVaultCertService import _serial_or_random

serial = _serial_or_random(None)
assert 0 < serial < 2**128
```

## Related Packages

Certificate service packages:

- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)
- [swarmauri_certservice_aws_kms](https://pypi.org/project/swarmauri_certservice_aws_kms/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Prefer managed identities or workload identity federation over long-lived client secrets.
- Keep Key Vault permissions scoped to the minimum operations required by the surrounding workflow.
- Store generated CSRs and issued certificate chains in auditable storage.
- Use a dedicated cloud CA or Azure certificate workflow for issuance/import operations outside this package.

## License

Apache-2.0


