import numpy as np
from QueryEngine import exact_nearest_neighbors

# Example dataset
data = np.array([1.0, 2.5, 3.3, 4.8], dtype=np.float32)
query_value = 3.0
k = 2

# Perform exact similarity search
neighbors = exact_nearest_neighbors(data, query_value, k)
print("Exact Neighbors:", neighbors)
