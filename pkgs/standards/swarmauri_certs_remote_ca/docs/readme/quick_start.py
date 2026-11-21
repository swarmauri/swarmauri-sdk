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
        return httpx.Response(
            200,
            json={"cert": base64.b64encode(cert_bytes).decode("ascii")},
        )

    svc = RemoteCaCertService("https://ca.example/sign")

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        svc._client = client  # Inject mock transport for the example.
        certificate = await svc.sign_cert(csr, {"kind": "dummy"})
        print(certificate)


asyncio.run(main())
