import asyncio

from swarmauri_keyproviders_mirrored import MirroredKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    ExportPolicy,
)
from swarmauri_core.crypto.types import KeyUse


async def main() -> None:
    primary = LocalKeyProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(
        primary,
        secondary,
        mirror_mode="public_only",
        fail_open_reads=True,
    )

    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    created = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(created.kid, created.version)

    await primary.destroy_key(created.kid, created.version)
    mirrored = await provider.get_public_jwk(created.kid, created.version)

    assert mirrored["x"] == jwk["x"]
    print(
        f"Failover retrieved Ed25519 key from secondary provider: {mirrored['kid']}"
    )


if __name__ == "__main__":
    asyncio.run(main())
