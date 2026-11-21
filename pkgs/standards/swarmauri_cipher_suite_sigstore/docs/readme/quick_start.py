from swarmauri_cipher_suite_sigstore import SigstoreCipherSuite

suite = SigstoreCipherSuite(name="demo-sigstore")

# Inspect the available operations and defaults
print(suite.features()["ops"].keys())

# Normalize an operation
descriptor = suite.normalize(op=list(suite.supports().keys())[0])
print(descriptor["alg"], descriptor["params"])
