import asyncio
from pathlib import Path

from swarmauri_certservice_stepca import StepCaCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = StepCaCertService(
        ca_url="https://ca.example",
        provisioner="devices",
        verify_tls="/etc/ssl/step-ca-root.pem",
    )
    key_ref = KeyRef(material=Path("device.key.pem").read_bytes())

    csr = await service.create_csr(
        key_ref,
        {"O": "Example Corp", "CN": "device-001.example.com"},
        san={
            "dns": ["device-001.example.com"],
            "uri": ["spiffe://example/device-001"],
        },
    )
    cert = await service.sign_cert(
        csr,
        key_ref,
        opts={"ott": "step-ca-one-time-token"},
    )

    Path("device.crt").write_bytes(cert)
    await service.aclose()


asyncio.run(main())
