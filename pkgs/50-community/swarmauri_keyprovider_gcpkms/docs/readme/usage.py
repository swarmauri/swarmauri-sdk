import asyncio

from swarmauri_keyprovider_gcpkms import GcpKmsKeyProvider


async def main() -> None:
    provider = GcpKmsKeyProvider(
        project_id="my-project",
        location_id="us-central1",
        key_ring_id="swarmauri",
    )
    key_ref = await provider.get_key("jwt-signing-key")
    jwk = await provider.get_public_jwk("jwt-signing-key", key_ref.version)

    print(key_ref.uses)
    print(jwk["kty"])


asyncio.run(main())
