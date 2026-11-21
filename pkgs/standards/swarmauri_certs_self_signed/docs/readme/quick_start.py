from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_certs_self_signed import SelfSignedCertificate

private_key = ed25519.Ed25519PrivateKey.generate()
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

key_ref = KeyRef(
    kid="example-ed25519",
    version=1,
    type=KeyType.ED25519,
    uses=(KeyUse.SIGN,),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=private_bytes,
)

builder = SelfSignedCertificate.tls_server(
    common_name="example.local",
    dns_names=["example.local", "api.example.local"],
)

certificate_pem = builder.issue(key_ref)
print(certificate_pem.decode().splitlines()[0])
