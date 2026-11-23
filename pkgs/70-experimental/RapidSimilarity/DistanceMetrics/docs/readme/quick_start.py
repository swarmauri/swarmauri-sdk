import numpy as np
from DistanceMetrics import euclidean_distance, cosine_similarity

# Example usage of Euclidean distance
vec1 = np.array([1.0, 2.0, 3.0])
vec2 = np.array([4.0, 5.0, 6.0])
distance = euclidean_distance(vec1, vec2)
print(f"Euclidean Distance: {distance}")

# Example usage of Cosine similarity
similarity = cosine_similarity(vec1, vec2)
print(f"Cosine Similarity: {similarity}")
