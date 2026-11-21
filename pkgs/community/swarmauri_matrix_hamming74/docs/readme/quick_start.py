from swarmauri_matrix_hamming74 import Hamming74Matrix

matrix = Hamming74Matrix()
message = [1, 0, 1, 1]
codeword = matrix.encode(message)

# Introduce a single-bit error
received = codeword.copy()
received[3] ^= 1

# Decode using syndrome lookup and Hamming distance search
nearest = matrix.nearest_codeword(received)
print(nearest)  # Recovers the original codeword
