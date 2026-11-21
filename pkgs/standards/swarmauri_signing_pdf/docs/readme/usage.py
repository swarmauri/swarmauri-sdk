import asyncio
from swarmauri_signing_pdf import PDFSigner


async def main() -> None:
    signer = PDFSigner()
    print("Features:", signer.supports()["features"])


if __name__ == "__main__":
    asyncio.run(main())
