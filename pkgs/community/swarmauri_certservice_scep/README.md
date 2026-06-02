![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certservice_scep/">
        <img src="https://static.pepy.tech/badge/swarmauri_certservice_scep/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_scep/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_scep.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_scep" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_scep?label=swarmauri_certservice_scep&color=green" alt="PyPI - swarmauri_certservice_scep"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri SCEP Certificate Service

`swarmauri_certservice_scep` provides `ScepCertService`, a Swarmauri certificate service for Simple Certificate Enrollment Protocol style workflows. The implemented service creates PKCS#10 CSRs, optionally embeds a challenge password, posts CSR bytes to a SCEP `PKIOperation` endpoint, and parses returned X.509 certificate metadata.

## Why Swarmauri SCEP Certificate Service?

Use this package when Swarmauri applications need a small SCEP-oriented enrollment adapter without embedding enrollment URL construction and CSR creation in application code. It keeps CSR generation, challenge-password handling, SCEP endpoint submission, and certificate metadata extraction behind `CertServiceBase`.

## FAQ

### Q: Does this package build complete CMS or PKCS#7 SCEP envelopes?

A: No. The current implementation posts CSR bytes directly to `pkiclient.exe?operation=PKIOperation` and returns the responder content. If your responder requires full SCEP CMS wrapping or PKCS#7 response extraction, handle that in the surrounding enrollment layer.

### Q: What CSR fields are supported?

A: `create_csr()` currently builds a CSR with the common name from `subject["CN"]`, DNS SAN entries, and a challenge password from the call or service constructor.

### Q: What does `verify_cert()` check?

A: The current verifier loads PEM or DER certificates and returns issuer, subject, serial, validity timestamps, and CA status. It does not perform chain validation or revocation checking.

### Q: Which standards does the package document?

A: The service docstring references SCEP from RFC 8894, PKCS#10 CSR creation from RFC 2986, and X.509 certificate metadata from RFC 5280.

## Features

- `ScepCertService` class registered under the `swarmauri.cert_services` entry point.
- PKCS#10 CSR creation from PEM private keys in `KeyRef.material`.
- DNS subject alternative name support.
- Challenge password support through the constructor or per-call argument.
- SCEP `PKIOperation` HTTP submission through `requests`.
- PEM and DER certificate loading for verification and parsing.
- Basic certificate metadata extraction for issuer, subject, serial, validity, and CA status.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- Reachable SCEP endpoint such as `https://mdm.example.com/scep`.
- PEM private key material for each device, service, or workload enrolling.
- RA challenge password when required by the SCEP service.
- Additional CMS/PKCS#7 handling in the caller when required by the SCEP responder.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certservice_scep
```

Install with `pip`:

```bash
pip install swarmauri_certservice_scep
```

## Usage

Create a CSR with a challenge password:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = ScepCertService(
        "https://scep.example.test",
        challenge_password="enroll-secret",
    )
    key_ref = KeyRef(material=Path("device.key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "device-001.example.com"},
        san={"dns": ["device-001.example.com", "device-001"]},
    )
    Path("device.csr").write_bytes(csr)


asyncio.run(main())
```

Submit a CSR to a SCEP endpoint:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = ScepCertService("https://scep.example.test")
    response_bytes = await service.sign_cert(
        Path("device.csr").read_bytes(),
        ca_key=KeyRef(kid="scep-ca"),
    )
    Path("device-response.bin").write_bytes(response_bytes)


asyncio.run(main())
```

Parse a returned certificate:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService


async def main() -> None:
    service = ScepCertService("https://scep.example.test")
    details = await service.parse_cert(Path("device.pem").read_bytes())

    print("Serial:", details["serial"])
    print("Subject:", details["subject"])


asyncio.run(main())
```

## Related Packages

Certificate service packages:

- [swarmauri_certservice_ms_adcs](https://pypi.org/project/swarmauri_certservice_ms_adcs/)
- [swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)
- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
- [swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Store challenge passwords and enrollment secrets in a secure vault.
- Treat SCEP responses as opaque until decoded by a response parser appropriate for your responder.
- Generate distinct key pairs per device or workload.
- Pair SCEP enrollment with CRL or OCSP verification packages for lifecycle monitoring.

## License

Apache-2.0


