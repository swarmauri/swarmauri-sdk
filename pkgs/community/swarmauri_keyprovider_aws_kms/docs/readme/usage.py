import asyncio

from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)


async def main() -> None:
    provider = AwsKmsKeyProvider(
        region="us-east-1",
        alias_prefix="swarmauri-prod",
    )
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        size_bits=3072,
        export_policy=ExportPolicy.never_export_secret,
        label="jwt-signing",
    )

    key_ref = await provider.create_key(spec)
    rotated = await provider.rotate_key(key_ref.kid)

    print(key_ref.kid, key_ref.version)
    print(rotated.kid, rotated.version)


asyncio.run(main())
