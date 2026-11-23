import asyncio

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider
from swarmauri_core.key_providers.types import ExportPolicy, KeyAlg, KeySpec


async def main() -> None:
    provider = VaultTransitKeyProvider(
        url="https://vault.example.com:8200",
        token="vault-token",
        mount="transit",
        verify="/etc/ssl/vault-ca.pem",
    )
    spec = KeySpec(
        alg=KeyAlg.ED25519,
        export_policy=ExportPolicy.never_export_secret,
        label="agents-signing",
    )

    key_ref = await provider.create_key(spec)
    rotated = await provider.rotate_key(key_ref.kid)

    print(key_ref.kid, key_ref.version)
    print(rotated.kid, rotated.version)


asyncio.run(main())
