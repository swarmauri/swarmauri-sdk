![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_remote_ca/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_remote_ca" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_remote_ca/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_remote_ca.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_remote_ca/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_remote_ca" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_remote_ca/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_remote_ca" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_remote_ca/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_remote_ca?label=swarmauri_certs_remote_ca&color=green" alt="PyPI - swarmauri_certs_remote_ca"/></a>
</p>

---

# Swarmauri Remote CA Cert Service

A certificate enrollment bridge implementing the `ICertService` interface and
forwarding CSRs to a remote Certificate Authority.

Features:
- Posts CSRs to a remote endpoint and returns issued certificates.
- Minimal parsing helpers for certificate snippets.
- Designed around X.509 as defined in RFC 5280 and Enrollment over Secure
  Transport (EST) in RFC 7030.

## Configuration

`RemoteCaCertService` accepts the following arguments:

- `endpoint` – Base URL of the remote CA sign endpoint.
- `auth` – Optional mapping of HTTP headers or an `httpx.Auth` instance for
  authentication.
- `timeout_s` – HTTP timeout in seconds (default `10`).
- `ca_chain` – Optional sequence of cached trust anchors exposed during
  verification and parsing.

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

When used against a real service, provide any required authentication headers
through the `auth` argument and override request or response formats via the
`opts` parameter of `sign_cert`.
