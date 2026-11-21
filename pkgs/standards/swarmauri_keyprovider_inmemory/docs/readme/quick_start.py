import asyncio
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyClass,
    KeyAlg,  # optional, not enforced by the provider
    KeyUse,
    ExportPolicy,
)


async def main() -> None:
    provider = InMemoryKeyProvider()

    # Create a symmetric key kept only in memory
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,  # optional hint ? not strictly enforced
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,  # material may be present
        label="session-key",
    )
    ref = await provider.create_key(spec)
    assert ref.kid and ref.version == 1
    # ref.material may be populated depending on export_policy

    # Rotate to get a new version, still in memory only
    ref2 = await provider.rotate_key(ref.kid)
    assert ref2.version == 2

    # List available versions
    versions = await provider.list_versions(ref.kid)
    print(versions)  # e.g., (1, 2)

    # Import existing key material
    imported = await provider.import_key(
        spec,
        material=b"\x00" * 32,
    )
    assert imported.version == 1

    # Fetch current version
    current = await provider.get_key(ref.kid)
    assert current.version == max(versions)

    # Destroy a specific version or the whole key
    await provider.destroy_key(ref.kid, version=1)  # delete only v1
    await provider.destroy_key(imported.kid)  # delete all versions

    # Utilities
    rand = await provider.random_bytes(16)
    okm = await provider.hkdf(b"ikm", salt=b"salt", info=b"ctx", length=32)
    print(len(rand), len(okm))


asyncio.run(main())
