from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

from swarmauri_pop_dpop import DPoPSigner

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

public_jwk = {
    "kty": "OKP",
    "crv": "Ed25519",
    "x": base64.urlsafe_b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )
    .rstrip(b"=")
    .decode("ascii"),
}

signer = DPoPSigner(
    private_key=private_key,
    public_jwk=public_jwk,
    algorithm="EdDSA",
)

dpop_header = signer.sign_request("GET", "https://api.example.com/resource")
print("DPoP header:", dpop_header)
print("cnf:", signer.cnf_binding())
