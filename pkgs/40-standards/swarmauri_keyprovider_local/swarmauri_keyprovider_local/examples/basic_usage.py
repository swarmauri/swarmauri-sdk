import asyncio
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)
from swarmauri_core.crypto.types import KeyUse


async def run_example() -> str:
    """Create and retrieve a symmetric key using LocalKeyProvider."""
    provider = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    created = await provider.create_key(spec)
    fetched = await provider.get_key(created.kid, include_secret=True)
    assert fetched.material is not None
    return fetched.kid


if __name__ == "__main__":
    print(asyncio.run(run_example()))
