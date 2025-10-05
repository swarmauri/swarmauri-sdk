![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_stepca" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_stepca/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_stepca.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_stepca" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_stepca" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_stepca?label=swarmauri_certservice_stepca&color=green" alt="PyPI - swarmauri_certservice_stepca"/></a>

</p>

---

# Swarmauri Step-ca Certificate Service

Community plugin providing a step-ca backed certificate service for Swarmauri. It turns the generic `ICertService` workflows into calls against the [smallstep step-ca](https://smallstep.com/docs/step-ca) REST API so agents can request certificates without hand-crafting HTTP payloads.

## Features

- Generate RFC 2986-compliant PKCS#10 certificate signing requests with SANs, challenge passwords, and custom extensions.
- Exchange CSRs for signed certificates through the step-ca `/1.0/sign` endpoint, including provisioner selection and template data.
- Asynchronous HTTP client with configurable TLS verification, timeouts, and one-time token (OTT) acquisition via a pluggable `token_provider`.
- Structured capability introspection through `supports()` so orchestrators can negotiate key algorithms and features.

## Prerequisites

- Python 3.10 or newer.
- Reachable step-ca instance (hosted or self-managed) exposing the `/1.0/sign` API.
- Provisioner configured in step-ca with one-time token authentication. Either supply OTTs directly at request time or provide an async `token_provider` function that returns them when asked.
- Local private key material for each CSR you plan to submit; embed it in `KeyRef.material` or wire in your own key management layer.

## Installation

```bash
# pip
pip install swarmauri_certservice_stepca

# poetry
poetry add swarmauri_certservice_stepca

# uv (pyproject-based projects)
uv add swarmauri_certservice_stepca
```

## Quickstart: Issue a Certificate via step-ca

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService
from swarmauri_core.certs.ICertService import SubjectSpec
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def enroll() -> None:
    async def fetch_ott(claims):
        # Look up the device-specific token issued by step-ca (KV store, API call, etc).
        device_id = claims["sub"] or "default"
        return Path(f"otts/{device_id}.txt").read_text().strip()

    service = StepCaCertService(
        ca_url="https://ca.example",
        provisioner="devices",
        token_provider=fetch_ott,
        timeout_s=10.0,
    )

    key_bytes = Path("device.key.pem").read_bytes()
    key_ref = KeyRef(
        kid="device-key",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=key_bytes,
    )

    subject: SubjectSpec = {
        "C": "US",
        "O": "Example Corp",
        "CN": "device-001.example.com",
    }

    csr_pem = await service.create_csr(
        key=key_ref,
        subject=subject,
        san={"dns": ["device-001.example.com", "device-001"]},
        extensions={
            "extended_key_usage": {"oids": ["serverAuth", "clientAuth"]},
        },
    )

    cert_pem = await service.sign_cert(csr_pem, ca_key=key_ref)
    Path("device.pem").write_bytes(cert_pem)

    await service.aclose()
    print("Certificate written to device.pem")


if __name__ == "__main__":
    asyncio.run(enroll())
```

The service extracts the subject name from the CSR and passes it to the `token_provider`, making it easy to map devices to their OTTs. If you already possess the token, skip the provider and pass it in via `opts={"ott": "..."}` when calling `sign_cert`.

## Control Validity Windows and Template Data

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def request_short_lived_cert(ott: str) -> bytes:
    service = StepCaCertService("https://ca.example", verify_tls="/etc/ssl/ca.pem")

    key_ref = KeyRef(
        kid="build-runner",
        version=1,
        type=KeyType.EC,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=Path("runner-key.pem").read_bytes(),
    )

    csr = await service.create_csr(
        key_ref,
        {"CN": "ci-runner", "O": "Example Corp"},
    )

    now = datetime.now(timezone.utc)
    cert = await service.sign_cert(
        csr,
        key_ref,
        not_before=int(now.timestamp()),
        not_after=int((now + timedelta(hours=8)).timestamp()),
        opts={
            "ott": ott,
            "template_data": {"env": "ci", "workload": "runner"},
        },
    )

    await service.aclose()
    return cert


# Usage
# asyncio.run(request_short_lived_cert(os.environ["STEPCA_OTT"]))
```

`sign_cert` automatically normalizes DER and PEM inputs, propagates custom template data, and honors explicit validity windows when your provisioner allows overrides.

## Operational Tips

- Close the underlying HTTP client with `aclose()` once you are done issuing certificates to release sockets.
- Provisioners can restrict key algorithms and SAN contents—call `supports()` to check compatibility before presenting the service to end users.
- Store OTTs in a secure vault or request them just-in-time from step-ca’s ACME/JWT machinery; never hard-code long-lived tokens in scripts.
- Combine this service with Swarmauri verification agents (CRL/OCSP) or your preferred PKI lints to track certificate health after issuance.
