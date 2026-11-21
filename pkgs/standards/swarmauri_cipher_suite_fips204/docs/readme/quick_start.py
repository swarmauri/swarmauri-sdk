from swarmauri_cipher_suite_fips204 import Fips204CipherSuite

suite = Fips204CipherSuite(name="mldsa")

# Prepare a ML-DSA-65 signing descriptor
descriptor = suite.normalize(op="sign", alg="ML-DSA-65")
print(descriptor["constraints"]["nistLevel"])  # -> 3
print(descriptor["mapped"]["provider"])  # -> ml-dsa:ML-DSA-65
