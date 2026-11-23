import asyncio
from pathlib import Path

from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = MsAdcsCertService(
        base_url="https://ca.example.com/certsrv",
        default_template="WebServer",
        auth=_AuthCfg(mode="none"),
    )
    key_ref = KeyRef(material=Path("webserver.key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"C": "US", "O": "Example Corp", "CN": "app.example.com"},
        san={"dns": ["app.example.com", "www.example.com"]},
    )
    Path("app.csr").write_bytes(csr)


asyncio.run(main())
