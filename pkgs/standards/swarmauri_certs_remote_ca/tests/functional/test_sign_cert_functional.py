import asyncio
import httpx

from swarmauri_certs_remote_ca import RemoteCaCertService


def test_sign_cert_raw_body():
    csr = b"func-csr"
    cert_bytes = b"func-cert"

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=cert_bytes)

    transport = httpx.MockTransport(handler)
    svc = RemoteCaCertService("https://ca.example/sign")
    svc._client = httpx.AsyncClient(transport=transport)

    result = asyncio.run(svc.sign_cert(csr, {"kind": "dummy"}))
    assert result == cert_bytes
