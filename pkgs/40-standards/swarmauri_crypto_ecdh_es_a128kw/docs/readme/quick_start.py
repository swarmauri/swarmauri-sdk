import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_crypto_ecdh_es_a128kw import ECDHESA128KWCrypto


def make_recipient_key() -> KeyRef:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    return KeyRef(
        kid="recipient-key",
        version=1,
        type=KeyType.EC,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        public=public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )


async def main() -> None:
    crypto = ECDHESA128KWCrypto()
    recipient = make_recipient_key()
    dek = b"0123456789ABCDEF"  # 16 byte content encryption key

    wrapped = await crypto.wrap(recipient, dek=dek)
    recovered = await crypto.unwrap(recipient, wrapped)

    print("Wrapped payload:", wrapped.wrapped.decode("utf-8"))
    assert recovered == dek


if __name__ == "__main__":
    asyncio.run(main())
