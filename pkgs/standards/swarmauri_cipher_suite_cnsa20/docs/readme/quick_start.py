from swarmauri_cipher_suite_cnsa20 import Cnsa20CipherSuite

suite = Cnsa20CipherSuite(name="demo-cnsa20")

# Inspect the available operations and defaults
print(suite.features()["ops"].keys())

# Normalize a post-quantum signing request
descriptor = suite.normalize(op="sign", alg="ML-DSA-65")
print(descriptor["alg"], descriptor["constraints"]["nistLevel"])  # -> 3
