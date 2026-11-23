from swarmauri_cipher_suite_fips203 import Fips203CipherSuite

suite = Fips203CipherSuite(name="mlkem")

# Describe a ML-KEM-768 key encapsulation request
descriptor = suite.normalize(op="wrap", alg="ML-KEM-768")
print(descriptor["constraints"]["nistLevel"])  # -> 3
print(descriptor["mapped"]["provider"])  # -> ml-kem:ML-KEM-768
