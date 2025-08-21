import asyncio
import base64
import httpx
import pytest

from swarmauri_certs_remote_ca import RemoteCaCertService


@pytest.mark.perf
def test_sign_cert_perf(benchmark):
    csr = b"perf-csr"
    cert_bytes = b"perf-cert"

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"cert": base64.b64encode(cert_bytes).decode()})

    transport = httpx.MockTransport(handler)
    svc = RemoteCaCertService("https://ca.example/sign")
    svc._client = httpx.AsyncClient(transport=transport)

    async def _run() -> None:
        await svc.sign_cert(csr, {"kind": "dummy"})

    benchmark(lambda: asyncio.run(_run()))
