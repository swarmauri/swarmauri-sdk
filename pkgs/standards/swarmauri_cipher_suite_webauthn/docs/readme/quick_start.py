from swarmauri_cipher_suite_webauthn import WebAuthnCipherSuite

suite = WebAuthnCipherSuite(name="demo-webauthn")

# Inspect the available operations and defaults
print(suite.features()["ops"].keys())

# Normalize an operation
descriptor = suite.normalize(op=list(suite.supports().keys())[0])
print(descriptor["alg"], descriptor["params"])
