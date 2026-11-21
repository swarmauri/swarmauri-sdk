import asyncio
from pathlib import Path

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = ScepCertService(
        "https://scep.example.test",
        challenge_password="enroll-secret",
    )
    key_ref = KeyRef(material=Path("device.key.pem").read_bytes())

    csr = await service.create_csr(
        key=key_ref,
        subject={"CN": "device-001.example.com"},
        san={"dns": ["device-001.example.com", "device-001"]},
    )
    Path("device.csr").write_bytes(csr)


asyncio.run(main())
