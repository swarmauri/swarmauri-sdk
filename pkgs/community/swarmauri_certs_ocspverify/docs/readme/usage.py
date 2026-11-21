import asyncio
from pathlib import Path

from swarmauri_certs_ocspverify import OcspVerifyService


async def main() -> None:
    service = OcspVerifyService()
    verification = await service.verify_cert(
        cert=Path("leaf.pem").read_bytes(),
        intermediates=[Path("issuer.pem").read_bytes()],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate status: GOOD")
    else:
        print("Certificate status:", verification["reason"])
    print("Next update:", verification.get("next_update"))


asyncio.run(main())
