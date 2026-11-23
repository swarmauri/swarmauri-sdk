from swarmauri_cipher_suite_fips1403 import FipsCipherSuite

suite = FipsCipherSuite(name="fips-mode")

# Describe a compliant RSA-PSS signing request
descriptor = suite.normalize(op="sign", alg="PS256")
print(descriptor["params"]["saltBits"])  # -> 256 enforced default
print(descriptor["constraints"]["minKeyBits"])  # -> 2048 minimum RSA modulus
