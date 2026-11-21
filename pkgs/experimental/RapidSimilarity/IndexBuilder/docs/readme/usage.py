import numpy as np
from kdtree import nearestNeighbor

# Example dataset
points = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
target = np.array([3.5, 4.5])

# Find the nearest neighbor
nearest = nearestNeighbor(points.tolist(), target.tolist())
print("Nearest Neighbor:", nearest)
