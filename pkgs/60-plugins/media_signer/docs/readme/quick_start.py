import asyncio

from MediaSigner import MediaSigner
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider

# Optionally pass a key provider so plugins receive a shared source for
# retrieving signing material.
key_provider: IKeyProvider | None = None
signer = MediaSigner(key_provider=key_provider)


async def sign_payload(payload: bytes) -> None:
    signatures = await signer.sign_bytes("jws", key="my-key", payload=payload)
    assert signatures, "At least one signature should be returned"
    print(signer.supports("jws"))


asyncio.run(sign_payload(b"payload"))
