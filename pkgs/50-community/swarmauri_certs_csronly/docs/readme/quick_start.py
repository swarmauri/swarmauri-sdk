import asyncio
from pathlib import Path

from swarmauri_certs_csronly import CsrOnlyService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = CsrOnlyService()
    key_ref = KeyRef(material=Path("example-key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "example.com", "O": "Example Inc"},
        san={"dns": ["example.com", "www.example.com"]},
    )
    Path("example.csr").write_bytes(csr)


asyncio.run(main())
