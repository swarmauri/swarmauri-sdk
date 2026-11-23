from swarmauri_cipher_suite_jwa import JwaCipherSuite
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

# Construct a key reference representative of the caller's key inventory
key = KeyRef(
    kid="demo-rsa",
    version=1,
    type=KeyType.RSA,
    uses=(KeyUse.SIGN, KeyUse.VERIFY),
    export_policy=ExportPolicy.PUBLIC_ONLY,
)

suite = JwaCipherSuite(name="default-jwa")

# Resolve the provider-facing descriptor for a signing request
descriptor = suite.normalize(op="sign", alg="PS256", key=key)
print(descriptor["mapped"]["provider"])  # -> "PS256"
print(descriptor["params"]["saltBits"])  # -> 256 (derived default)
