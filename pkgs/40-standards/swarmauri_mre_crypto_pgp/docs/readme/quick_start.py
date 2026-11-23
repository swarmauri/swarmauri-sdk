import asyncio
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)
from swarmauri_mre_crypto_pgp import PGPMreCrypto


async def main():
    # Generate an OpenPGP key pair with pgpy
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Test User", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.EncryptCommunications},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )

    # Create references understood by the provider
    pub_ref = {"kind": "pgpy_pub", "pub": key.pubkey}
    priv_ref = {"kind": "pgpy_priv", "priv": key}

    # Encrypt for many and open with the private key
    mre = PGPMreCrypto()
    pt = b"hello"
    env = await mre.encrypt_for_many([pub_ref], pt)
    rt = await mre.open_for(priv_ref, env)
    print(rt)


if __name__ == "__main__":
    asyncio.run(main())
