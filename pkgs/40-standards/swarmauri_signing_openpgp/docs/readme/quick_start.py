import asyncio
from swarmauri_signing_openpgp import OpenPGPSigner


async def main() -> None:
    signer = OpenPGPSigner()
    print(signer.supports()["features"])


if __name__ == "__main__":
    asyncio.run(main())
