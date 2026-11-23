"""Create keys across multiple providers with policy-driven routing."""

import asyncio

from swarmauri_keyprovider_hierarchical import (
    HierarchicalKeyProvider,
    CreateRule,
)
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
)


async def main() -> None:
    children = {
        "kms": LocalKeyProvider(),
        "local": LocalKeyProvider(),
    }
    provider = HierarchicalKeyProvider(
        children,
        create_policy=[
            CreateRule(provider="kms", klass=KeyClass.asymmetric),
            CreateRule(provider="local", klass=KeyClass.symmetric),
        ],
        randomness_provider="local",  # designate a child for random_bytes
    )

    symmetric_spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    asymmetric_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )

    symmetric_ref = await provider.create_key(symmetric_spec)
    asymmetric_ref = await provider.create_key(asymmetric_spec)
    random_token = await provider.random_bytes(16)
    jwks = await provider.jwks()

    print(f"Symmetric key kid: {symmetric_ref.kid}")
    print(f"Asymmetric key kid: {asymmetric_ref.kid}")
    print(f"Random token length: {len(random_token)} bytes")
    print(f"JWKS entries: {len(jwks['keys'])}")


if __name__ == "__main__":
    asyncio.run(main())
