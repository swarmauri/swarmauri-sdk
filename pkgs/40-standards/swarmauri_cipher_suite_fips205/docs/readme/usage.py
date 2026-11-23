from swarmauri_cipher_suite_fips205 import Fips205CipherSuite

suite = Fips205CipherSuite(name="slhdsa")

# Normalise a SLH-DSA-SHAKE-192s signing request
descriptor = suite.normalize(op="sign", alg="SLH-DSA-SHAKE-192s")
print(descriptor["constraints"]["nistLevel"])  # -> 3
print(descriptor["mapped"]["provider"])  # -> slh-dsa:SLH-DSA-SHAKE-192s
