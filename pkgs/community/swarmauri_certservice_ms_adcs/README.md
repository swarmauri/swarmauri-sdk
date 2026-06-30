![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certservice_ms_adcs/">
        <img src="https://static.pepy.tech/badge/swarmauri_certservice_ms_adcs/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_ms_adcs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_ms_adcs.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_ms_adcs" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_ms_adcs?label=swarmauri_certservice_ms_adcs&color=green" alt="PyPI - swarmauri_certservice_ms_adcs"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Microsoft AD CS Certificate Service

`swarmauri_certservice_ms_adcs` provides `MsAdcsCertService`, a Swarmauri certificate service prepared for Microsoft Active Directory Certificate Services environments. The implemented runtime builds PKCS#10 CSRs from PEM private keys, creates local self-signed certificates, verifies issued certificates against supplied issuers, parses X.509 metadata, and configures HTTP authentication sessions for AD CS Web Enrollment endpoints.

## Why Swarmauri Microsoft AD CS Certificate Service?

Use this package when Swarmauri workflows need AD CS-compatible certificate request generation and local certificate inspection while preserving room for NTLM, Kerberos, basic, or anonymous Web Enrollment access. It gives enterprise PKI code one `CertServiceBase` component for CSR creation, self-signed test certificates, verification, parsing, and authentication configuration.

## FAQ

### Q: Does this package submit CSRs to AD CS today?

A: Not yet. `sign_cert()` currently raises `NotImplementedError`. Use `create_csr()` to build the request, then submit it through your AD CS Web Enrollment workflow or a custom automation layer.

### Q: Which authentication modes are modeled?

A: `_AuthCfg` supports `basic` and `none` with the built-in `httpx` client. NTLM and Kerberos require an httpx-compatible auth adapter before use.

### Q: What certificate operations are implemented?

A: CSR creation, self-signed certificate creation, validity/signature verification with supplied issuer certificates, and metadata parsing are implemented.

### Q: What certificate metadata can it parse?

A: `parse_cert()` returns serial, signature algorithm, issuer, subject, validity timestamps, SKID, AKID, SAN, EKU, key usage, and CA status when those extensions are present.

## Features

- `MsAdcsCertService` class registered under the `swarmauri.cert_services` entry point.
- HTTP session setup for AD CS-style endpoints with configurable TLS verification.
- NTLM, Kerberos/SPNEGO, HTTP Basic, and anonymous authentication modes.
- PKCS#10 CSR creation from PEM private keys in `KeyRef.material`.
- Subject support for standard X.509 distinguished-name fields and custom RDNs.
- SAN support for DNS, IP, URI, email, and UPN entries.
- Key usage and extended key usage CSR extension support.
- Local self-signed certificate generation for development and tests.
- Certificate verification with validity-window checks and optional issuer signature verification.
- X.509 metadata parsing for audit and observability workflows.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- Network access to an AD CS Web Enrollment endpoint when integrating with a live CA.
- PEM private key material for CSR and self-signed certificate creation.
- Optional httpx-compatible adapters for NTLM or Kerberos/SPNEGO authentication.
- Issuer certificates when using signature verification.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certservice_ms_adcs
```

Install with `pip`:

```bash
pip install swarmauri_certservice_ms_adcs
```

## Usage

Build a CSR for AD CS enrollment:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = MsAdcsCertService(
        base_url="https://ca.example.com/certsrv",
        default_template="WebServer",
        auth=_AuthCfg(mode="none"),
    )
    key_ref = KeyRef(material=Path("webserver.key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"C": "US", "O": "Example Corp", "CN": "app.example.com"},
        san={"dns": ["app.example.com", "www.example.com"]},
    )
    Path("app.csr").write_bytes(csr)


asyncio.run(main())
```

Create and inspect a local self-signed certificate:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = MsAdcsCertService(
        base_url="https://ca.example.com/certsrv",
        auth=_AuthCfg(mode="none"),
    )
    key_ref = KeyRef(material=Path("dev.key.pem").read_bytes())

    cert = await service.create_self_signed(
        key=key_ref,
        subject={"CN": "dev.example.com"},
    )
    parsed = await service.parse_cert(cert)
    verification = await service.verify_cert(cert, trust_roots=[cert])

    print(parsed["subject"])
    print(verification["valid"])


asyncio.run(main())
```

## Authentication Modes

- `ntlm`: provide an httpx-compatible NTLM auth adapter before using `_AuthCfg(mode="ntlm", username="DOMAIN\\user", password="...")`.
- `kerberos`: provide an httpx-compatible Kerberos/SPNEGO auth adapter before using `_AuthCfg(mode="kerberos", spnego_delegate=True)` when delegation is required.
- `basic`: provide `_AuthCfg(mode="basic", username="...", password="...")`.
- `none`: provide `_AuthCfg(mode="none")` for anonymous, mTLS-fronted, or externally authenticated flows.

## Related Packages

Certificate service packages:

- [swarmauri_certservice_scep](https://pypi.org/project/swarmauri_certservice_scep/)
- [swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)
- [swarmauri_certservice_aws_kms](https://pypi.org/project/swarmauri_certservice_aws_kms/)
- [swarmauri_certservice_gcpkms](https://pypi.org/project/swarmauri_certservice_gcpkms/)
- [swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
- [swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components for certificate-adjacent workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Store AD CS credentials in a secure secrets manager and inject them at runtime.
- Treat generated CSRs, issued certificates, verification results, and parsed metadata as auditable enrollment artifacts.
- Regenerate CSRs before certificate expiry to leave time for manual approvals.
- Combine this service with CRL and OCSP verification packages for revocation visibility.

## License

Apache-2.0


