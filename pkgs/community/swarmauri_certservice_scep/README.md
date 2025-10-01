![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_scep" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_scep/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_scep.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_scep" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_scep" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_scep?label=swarmauri_certservice_scep&color=green" alt="PyPI - swarmauri_certservice_scep"/></a>
</p>

---

# Swarmauri Certservice SCEP

`ScepCertService` implements certificate enrollment using the [Simple Certificate Enrollment Protocol (SCEP)](https://datatracker.ietf.org/doc/html/rfc8894). It maps the generic `ICertService` flows onto SCEP operations so applications can request, receive, and validate X.509 certificates without dealing with protocol details.

## Features

- Generate RFC 2986-compliant PKCS#10 certificate signing requests with challenge passwords and subject alternative names.
- Submit CSRs to SCEP responders via `PKCSReq` and retrieve issued certificates.
- Download issuer CA certificates and validate issued leaf certificates for time window, issuer, and CA flags.
- Parse returned certificates into structured dictionaries for downstream automation.

## Prerequisites

- Python 3.10 or newer.
- An accessible SCEP server URL (for example, `https://mdm.example.com/scep`).
- Private key material for each device or service enrolling via SCEP. Software keys can be embedded in the `KeyRef.material` field.
- Optional: RA challenge password if your SCEP service requires one for enrollment.

## Installation

```bash
# pip
pip install swarmauri_certservice_scep

# poetry
poetry add swarmauri_certservice_scep

# uv (pyproject-based projects)
uv add swarmauri_certservice_scep
```

## Quickstart: Enroll a Device Certificate

```python
import asyncio
from pathlib import Path

from cryptography.hazmat.primitives import serialization

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.certs.ICertService import SubjectSpec
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def enroll() -> None:
    service = ScepCertService(
        "https://scep.example.test",
        challenge_password="enroll-secret",
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
    )

    fullchain = await service.sign_cert(csr_pem, ca_key=key_ref)
    Path("device.pem").write_bytes(fullchain)
    print("Enrollment complete → device.pem")


if __name__ == "__main__":
    asyncio.run(enroll())
```

`sign_cert` returns the DER content provided by the SCEP server. Depending on your responder, the payload may be a single certificate or a PKCS#7 chain; decode accordingly before storing.

## Verify Certificates from SCEP

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService


async def verify() -> None:
    service = ScepCertService("https://scep.example.test")

    device_cert = Path("device.pem").read_bytes()

    result = await service.verify_cert(device_cert)
    if result["valid"]:
        print("Issuer:", result["issuer"])
        print("Valid until:", result["not_after"])
    else:
        print("Certificate failed validation:", result["reason"])

    details = await service.parse_cert(device_cert)
    print("Serial:", details["serial"])
    print("Subject alternative names:", details.get("san"))


if __name__ == "__main__":
    asyncio.run(verify())
```

`verify_cert` evaluates SCEP-issued certificates for validity windows and CA constraints, while `parse_cert` extracts SAN, EKU, and key usage metadata for logging or policy engines.

## Operational Tips

- Generate distinct key pairs per device or workload, and store them securely—`KeyRef` can reference HSM-backed keys instead of raw PEM material.
- Capture challenge passwords and sensitive enrollment secrets from a secure vault or environment variables rather than hard-coding them in scripts.
- If your SCEP responder returns PKCS#7 payloads, feed the response into `cryptography.hazmat.primitives.serialization.pkcs7` to extract certificate chains before deployment.
- Pair SCEP enrollment with Swarmauri revocation check services (`swarmauri_certs_ocspverify`, `swarmauri_certs_crlverifyservice`) to maintain lifecycle hygiene.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
