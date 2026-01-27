import asyncio

import pytest

from swarmauri_keyprovider_inmemory import InMemoryKeyProvider
from swarmauri_core.crypto.types import ExportPolicy
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec, KeyUse


@pytest.mark.example
def test_readme_usage_example() -> None:
    async def main() -> None:
        provider = InMemoryKeyProvider()

        spec = KeySpec(
            klass=KeyClass.symmetric,
            alg=KeyAlg.AES256_GCM,
            uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            label="session-key",
        )
        ref = await provider.create_key(spec)
        assert ref.kid and ref.version == 1
        assert ref.material is not None and len(ref.material) == 32

        ref2 = await provider.rotate_key(ref.kid)
        assert ref2.version == 2

        versions = await provider.list_versions(ref.kid)
        assert versions == (1, 2)

        imported = await provider.import_key(
            spec,
            material=b"\x00" * 32,
        )
        assert imported.version == 1
        if imported.material is not None:
            assert imported.material == b"\x00" * 32

        current = await provider.get_key(ref.kid)
        assert current.version == max(versions)

        assert await provider.destroy_key(ref.kid, version=1)
        remaining = await provider.list_versions(ref.kid)
        assert remaining == (2,)

        assert await provider.destroy_key(imported.kid)

        rand = await provider.random_bytes(16)
        okm = await provider.hkdf(b"ikm", salt=b"salt", info=b"ctx", length=32)
        assert len(rand) == 16
        assert len(okm) == 32

    asyncio.run(main())
