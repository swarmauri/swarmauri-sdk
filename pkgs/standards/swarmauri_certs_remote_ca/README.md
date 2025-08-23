![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Remote CA Cert Service

A certificate enrollment bridge implementing the `ICertService` interface and
forwarding CSRs to a remote Certificate Authority.

Features:
- Posts CSRs to a remote endpoint and returns issued certificates.
- Minimal parsing helpers for certificate snippets.
- Designed around X.509 as defined in RFC 5280 and Enrollment over Secure
  Transport (EST) in RFC 7030.

## Installation

```bash
pip install swarmauri_certs_remote_ca
```

## Entry Point

The service registers under the `swarmauri.certs` entry point as
`RemoteCaCertService`.

## Usage

The service is asynchronous and expects an existing CSR (certificate signing
request) in PEM or DER form.  Configure the remote CA endpoint and submit the
CSR to receive the issued certificate:

```python
import asyncio
import base64
import json
import httpx
from swarmauri_certs_remote_ca import RemoteCaCertService

csr = b"example-csr"
cert_bytes = b"example-cert"


async def main() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.content)
        assert base64.b64decode(data["csr"]) == csr
        return httpx.Response(200, json={"cert": base64.b64encode(cert_bytes).decode()})

    transport = httpx.MockTransport(handler)
    svc = RemoteCaCertService("https://ca.example/sign")
    svc._client = httpx.AsyncClient(transport=transport)

    cert = await svc.sign_cert(csr, {"kind": "dummy"})
    print(cert)


asyncio.run(main())
```

The example above mocks a CA using `httpx.MockTransport`.  In real scenarios
`RemoteCaCertService` posts the CSR to the configured endpoint and returns the
certificate bytes supplied by the remote CA.
