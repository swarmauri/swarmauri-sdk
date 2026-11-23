import asyncio
from pathlib import Path

from swarmauri_certs_crlverifyservice import CrlVerifyService


async def main() -> None:
    service = CrlVerifyService()
    verification = await service.verify_cert(
        cert=Path("leaf.pem").read_bytes(),
        crls=[Path("issuer.crl").read_bytes()],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate is valid.")
    elif verification.get("revoked"):
        print("Certificate was revoked:", verification["reason"])
    else:
        print("Certificate failed validation:", verification["reason"])


asyncio.run(main())
