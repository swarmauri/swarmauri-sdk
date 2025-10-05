![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_ms_adcs" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_ms_adcs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_ms_adcs.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_ms_adcs" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_ms_adcs" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_ms_adcs?label=swarmauri_certservice_ms_adcs&color=green" alt="PyPI - swarmauri_certservice_ms_adcs"/></a>

</p>

---

# swarmauri_certservice_ms_adcs

Community plugin providing a certificate service client for Microsoft Active Directory Certificate Services (AD CS).

## Features

- Generate RFC 2986-compliant PKCS#10 CSRs with rich subject, subject alternative name, and extension options.
- Parse and validate X.509 certificates per RFC 5280, including issuer matching and signature verification.
- Ready-to-use authentication helpers for NTLM, Kerberos, and HTTP basic auth while preserving TLS configuration.
- Typed `supports()` metadata describing templates, key algorithms, and capabilities advertised to Swarmauri agents.

## Prerequisites

- Python 3.10 or newer.
- Network access to an AD CS Web Enrollment endpoint (typically `https://<ca>/certsrv`).
- A private key for each CSR you plan to submit; software keys can be read from PEM while HSM-backed keys can be referenced via `KeyRef` metadata.
- Optional authentication libraries: install `requests-ntlm` for NTLM flows and `requests-kerberos` for Kerberos/SPNEGO delegation.

## Installation

Install the core package or include extras for the auth helpers your environment requires:

```bash
# pip
pip install "swarmauri_certservice_ms_adcs[ntlm,kerberos]"

# poetry
poetry add swarmauri_certservice_ms_adcs -E ntlm -E kerberos

# uv (pyproject-based projects)
uv add "swarmauri_certservice_ms_adcs[ntlm,kerberos]"
```

You can drop the extras if your AD CS deployment only needs anonymous access or HTTP basic authentication.

## Quickstart: Build a CSR for AD CS

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.certs.ICertService import SubjectSpec
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def main() -> None:
    service = MsAdcsCertService(
        base_url="https://ca.example.com/certsrv",
        default_template="WebServer",
        auth=_AuthCfg(
            mode="ntlm",
            username="EXAMPLE\\svc-adcs",
            password="s3cr3t!",
            verify_tls=True,
        ),
    )

    key_bytes = Path("webserver.key.pem").read_bytes()
    key_ref = KeyRef(
        kid="webserver-key",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        material=key_bytes,
    )

    subject: SubjectSpec = {
        "C": "US",
        "ST": "Texas",
        "L": "Austin",
        "O": "Example Corp",
        "CN": "app.example.com",
    }

    csr_pem = await service.create_csr(
        key=key_ref,
        subject=subject,
        san={"dns": ["app.example.com", "www.example.com"]},
    )

    Path("app.csr").write_bytes(csr_pem)
    print("CSR saved to app.csr")


if __name__ == "__main__":
    asyncio.run(main())
```

Submit `app.csr` through your AD CS Web Enrollment UI, automation, or a downstream Swarmauri agent responsible for certificate issuance.

## Validate Issued Certificates

After AD CS returns a certificate, use the same service instance to confirm the chain and inspect metadata:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg


async def verify_certificate() -> None:
    service = MsAdcsCertService(
        base_url="https://ca.example.com/certsrv",
        auth=_AuthCfg(mode="none"),
    )

    issued_cert = Path("app.pem").read_bytes()
    issuing_ca = Path("issuing-ca.pem").read_bytes()

    verification = await service.verify_cert(
        cert=issued_cert,
        trust_roots=[issuing_ca],
    )
    if verification["valid"]:
        print("Certificate is valid until", verification["not_after"])
    else:
        print("Validation failed:", verification["reason"])

    parsed = await service.parse_cert(issued_cert)
    print("Subject:", parsed["subject"])
    print("Subject Alternative Names:", parsed.get("san"))


if __name__ == "__main__":
    asyncio.run(verify_certificate())
```

`verify_cert` performs structural checks and signature validation when an issuer certificate is supplied, while `parse_cert` surfaces extension data for auditing or observability pipelines.

## Authentication Modes

- **NTLM** – enable by installing `requests-ntlm` and providing domain credentials via `_AuthCfg(mode="ntlm", username="DOMAIN\\user", password="..." )`.
- **Kerberos/SPNEGO** – install `requests-kerberos` and set `_AuthCfg(mode="kerberos", spnego_delegate=True)` when delegation is required.
- **HTTP Basic** – provide `_AuthCfg(mode="basic", username=..., password=...)` for AD CS deployments fronted by basic auth proxies.
- **Anonymous** – set `_AuthCfg(mode="none")` for environments that rely on IP allow lists or mutual TLS.

## Best Practices

- Store AD CS credentials in a secure secrets manager and inject them via environment variables rather than hard-coding passwords.
- Capture issued certificates, verification results, and parsed metadata in your logging system so you can trace enrollment activity.
- Rotate key pairs and certificates regularly; regenerate CSRs ahead of expiry to leave time for manual approvals.
- Combine this plugin with Swarmauri certificate verification agents (CRL/OCSP) to maintain revocation visibility across the lifecycle.
