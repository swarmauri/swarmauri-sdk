import asyncio
from swarmauri_keyprovider_remote_jwks import RemoteJwksKeyProvider


async def main() -> None:
    provider = RemoteJwksKeyProvider(
        jwks_url="https://example.com/.well-known/jwks.json"
    )

    # Optional: pre-fetch the JWKS; otherwise the first key lookup triggers it
    provider.refresh(force=True)

    jwk = await provider.get_public_jwk("test", version=1)
    print(jwk)


asyncio.run(main())
