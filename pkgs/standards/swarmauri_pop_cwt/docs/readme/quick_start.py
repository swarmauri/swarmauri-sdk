import base64
from cose.algorithms import SignatureAlg
from cose.keys import CoseKey
from swarmauri_pop_cwt import CwtPoPSigner

private_key = CoseKey.from_dict(
    {
        1: 1,  # OKP
        -1: 6,  # Ed25519
        -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g=="),
    }
)
public_key = CoseKey.from_dict(
    {
        1: 1,
        -1: 6,
        -2: base64.urlsafe_b64decode("11qYAYafhZMrrZ8Zgo5u1g=="),
    }
)

signer = CwtPoPSigner(
    private_key=private_key,
    public_key=public_key,
    algorithm=SignatureAlg.EdDSA,
)

cwp_header = signer.sign_request("GET", "https://api.example.com/resource")
print("CWP header:", cwp_header)
print("cnf:", signer.cnf_binding())
