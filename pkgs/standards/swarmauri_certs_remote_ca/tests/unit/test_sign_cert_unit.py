import asyncio
import base64
import json
import httpx
import pytest

from swarmauri_certs_remote_ca import RemoteCaCertService


@pytest.mark.unit
def test_sign_cert_unit():
    csr = b"unit-csr"
    cert_bytes = b"unit-cert"

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("https://ca.example/sign")
        data = json.loads(request.content)
        assert base64.b64decode(data["csr"]) == csr
        return httpx.Response(200, json={"cert": base64.b64encode(cert_bytes).decode()})

    transport = httpx.MockTransport(handler)
    svc = RemoteCaCertService("https://ca.example/sign")
    svc._client = httpx.AsyncClient(transport=transport)

    result = asyncio.run(svc.sign_cert(csr, {"kind": "dummy"}))
    assert result == cert_bytes
