import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_certs_local_ca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _key(name: str) -> KeyRef:
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid=name,
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


async def main() -> None:
    svc = LocalCaCertService()
    ca_key = _key("ca")
    leaf_key = _key("leaf")

    # Create a certificate signing request for the leaf key.
    csr = await svc.create_csr(leaf_key, {"CN": "leaf"})

    # Sign the CSR with the CA key to produce a leaf certificate.
    cert = await svc.sign_cert(csr, ca_key, issuer={"CN": "ca"})

    # Verify the newly issued certificate.
    result = await svc.verify_cert(cert)
    print(result["valid"], result["subject"], result["issuer"])


asyncio.run(main())
