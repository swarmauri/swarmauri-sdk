from swarmauri_cipher_suite_cose import CoseCipherSuite

suite = CoseCipherSuite(name="default-cose")

# Normalize a COSE signing request using the integer identifier for EdDSA
descriptor = suite.normalize(op="sign", alg=-8)
print(descriptor["alg"])  # -> "-8"
print(descriptor["mapped"]["provider"])  # -> "-8"
print(descriptor["params"]["tagBits"])  # -> 128 for COSE AEAD defaults
