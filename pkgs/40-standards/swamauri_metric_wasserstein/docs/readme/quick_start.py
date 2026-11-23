from swamauri_metric_wasserstein import WassersteinMetric
from swarmauri_standard.vectors.Vector import Vector

vector_a = Vector(value=[0.0, 1.0, 2.0])
vector_b = Vector(value=[0.0, 1.0, 2.0])

distance_calculator = WassersteinMetric()

distance = distance_calculator.distance(vector_a, vector_b)
similarity = distance_calculator.similarity(vector_a, vector_b)

print(f"Distance: {distance}")
print(f"Similarity: {similarity}")
