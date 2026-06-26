import asyncio
import base64
import httpx
import json
import pytest

from swarmauri_certs_remote_ca import RemoteCaCertService


@pytest.mark.example
def test_readme_usage_example() -> None:
    csr = b"example-csr"
    cert_bytes = b"example-cert"

    async def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.content)
        assert base64.b64decode(data["csr"]) == csr
        return httpx.Response(
            200,
            json={"cert": base64.b64encode(cert_bytes).decode("ascii")},
        )

    async def main() -> bytes:
        svc = RemoteCaCertService("https://ca.example/sign")
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler)
        ) as client:
            svc._client = client
            return await svc.sign_cert(csr, {"kind": "dummy"})

    result = asyncio.run(main())
    assert result == cert_bytes
