![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certservice_stepca/">
        <img src="https://static.pepy.tech/badge/swarmauri_certservice_stepca/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_stepca/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_stepca.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_stepca" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_stepca/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_stepca?label=swarmauri_certservice_stepca&color=green" alt="PyPI - swarmauri_certservice_stepca"/></a>
</p>

# Swarmauri Step CA Certificate Service

`swarmauri_certservice_stepca` provides `StepCaCertService`, an asynchronous Swarmauri certificate service for [smallstep step-ca](https://smallstep.com/docs/step-ca). It creates PKCS#10 certificate signing requests, submits them to the step-ca `/1.0/sign` API with a one-time token, and returns PEM or DER certificate bytes for workload, device, service, and internal PKI enrollment.

## Why Swarmauri Step CA Certificate Service?

Use this package when a Swarmauri application needs step-ca certificate issuance without spreading CSR construction, token lookup, HTTP client handling, and certificate metadata parsing across application code. `StepCaCertService` keeps those operations behind the shared `CertServiceBase` interface so certificate automation can be composed with Swarmauri keys, verifiers, agents, and workflow components.

## FAQ

### Q: What step-ca API does this package call?

A: `sign_cert()` posts JSON to `/1.0/sign`, the step-ca certificate signing endpoint used for CSR-based X.509 issuance. The request includes the CSR and an authorization token supplied through `opts={"ott": "..."}` or a `token_provider`.

### Q: Does this package create one-time tokens?

A: No. It consumes one-time tokens. Provide the token directly or pass an async `token_provider` that maps CSR claims to an issued token from your own step-ca, vault, identity, or provisioning layer.

### Q: Which certificate fields can `create_csr()` build?

A: The CSR builder supports common X.509 subject attributes, DNS/IP/URI/email subject alternative names, challenge passwords, basic constraints, key usage, and extended key usage.

### Q: Does `verify_cert()` perform full PKI path validation?

A: No. It loads PEM or DER certificates, checks the certificate validity window, and returns metadata. Use a dedicated verifier such as CRL or OCSP packages when you need revocation checks or chain policy enforcement.

## Features

- `StepCaCertService` registered under the `swarmauri.cert_services` entry point.
- Async `httpx` client for step-ca `/1.0/sign` calls.
- CSR generation for RSA, EC, and Ed25519 private keys.
- Subject alternative names for DNS names, IP addresses, URIs, and email addresses.
- Challenge password, basic constraints, key usage, and extended key usage support.
- One-time-token handling through direct options or an async token provider.
- Optional provisioner, custom template data, extra request payload fields, and validity-window overrides.
- PEM response handling with optional DER conversion.
- Basic PEM and DER certificate verification and parsing helpers.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- A reachable step-ca instance exposing `/1.0/sign`.
- A provisioner configured for X.509 certificate signing.
- A one-time token for each signing request, or a token provider that can create or retrieve one.
- PEM private key material available through `KeyRef.material`.
- Trust configuration for the step-ca TLS endpoint when it uses a private root.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certservice_stepca
```

Install with `pip`:

```bash
pip install swarmauri_certservice_stepca
```

## Usage

Issue a certificate with an already issued one-time token:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = StepCaCertService(
        ca_url="https://ca.example",
        provisioner="devices",
        verify_tls="/etc/ssl/step-ca-root.pem",
    )
    key_ref = KeyRef(material=Path("device.key.pem").read_bytes())

    csr = await service.create_csr(
        key_ref,
        {"O": "Example Corp", "CN": "device-001.example.com"},
        san={"dns": ["device-001.example.com"], "uri": ["spiffe://example/device-001"]},
    )
    cert = await service.sign_cert(
        csr,
        key_ref,
        opts={"ott": "step-ca-one-time-token"},
    )

    Path("device.crt").write_bytes(cert)
    await service.aclose()


asyncio.run(main())
```

Map CSR claims to a token provider:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService
from swarmauri_core.crypto.types import KeyRef


async def token_provider(claims: dict) -> str:
    common_name = claims["sub"]
    return Path(f"otts/{common_name}.txt").read_text().strip()


async def main() -> None:
    service = StepCaCertService(
        "https://ca.example",
        provisioner="workloads",
        token_provider=token_provider,
        timeout_s=10.0,
    )
    key_ref = KeyRef(material=Path("workload.key.pem").read_bytes())
    csr = await service.create_csr(key_ref, {"CN": "worker-17"})
    cert = await service.sign_cert(
        csr,
        key_ref,
        opts={"template_data": {"env": "prod", "role": "worker"}},
    )

    Path("worker-17.crt").write_bytes(cert)
    await service.aclose()


asyncio.run(main())
```

Parse certificate metadata:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService


async def main() -> None:
    service = StepCaCertService("https://ca.example")
    result = await service.verify_cert(Path("worker-17.crt").read_bytes())
    details = await service.parse_cert(Path("worker-17.crt").read_bytes())

    print(result["valid"])
    print(details["subject"])
    await service.aclose()


asyncio.run(main())
```

## Related Packages

Certificate service packages:

- [swarmauri_certservice_scep](https://pypi.org/project/swarmauri_certservice_scep/)
- [swarmauri_certservice_ms_adcs](https://pypi.org/project/swarmauri_certservice_ms_adcs/)
- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)
- [swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri runtime components.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Retrieve one-time tokens just in time and avoid persisting them in source code or build logs.
- Use `verify_tls` with the step-ca root bundle when the CA is internal.
- Close the async client with `aclose()` after issuance bursts.
- Keep certificate issuance separate from revocation checking; pair this package with OCSP or CRL verification packages for lifecycle monitoring.

## License

Apache-2.0
