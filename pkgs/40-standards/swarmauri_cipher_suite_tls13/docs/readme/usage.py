from swarmauri_cipher_suite_tls13 import Tls13CipherSuite

suite = Tls13CipherSuite(name="demo-tls13")

# Inspect the available operations and defaults
print(suite.features()["ops"].keys())

# Normalize an operation
descriptor = suite.normalize(op=list(suite.supports().keys())[0])
print(descriptor["alg"], descriptor["params"])
