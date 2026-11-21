from swarmauri_crypto_rust import RustCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
import asyncio


async def main():
    crypto = RustCrypto()

    # Create a symmetric key
    sym_key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=crypto.generate_key(32),  # 32-byte key
    )

    # Encrypt and decrypt
    plaintext = b"Hello, Rust crypto world!"
    ciphertext = await crypto.encrypt(sym_key, plaintext)
    decrypted = await crypto.decrypt(sym_key, ciphertext)

    print(f"Original:  {plaintext}")
    print(f"Decrypted: {decrypted}")
    print(f"Match:     {plaintext == decrypted}")

    # Get version information
    version_info = crypto.get_version_info()
    print(f"Backend:   {version_info['backend']}")
    print(f"Version:   {version_info['rust_crypto_version']}")


asyncio.run(main())
