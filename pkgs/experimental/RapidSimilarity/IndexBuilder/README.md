# IndexBuilder

## Purpose

The `IndexBuilder` package provides efficient algorithms for building indexes (e.g., tree-based or hash-based structures) to accelerate similarity queries over large datasets.

## Installation

To install the `IndexBuilder` package, you need to have Python 3.10 or later, along with Meson and Ninja build systems.

1. Ensure you have `meson` and `ninja` installed:
   ```bash
   pip install meson ninja
   ```

2. Clone the repository and navigate into the directory:
   ```bash
   git clone <repository-url>
   cd IndexBuilder
   ```

3. Build the package:
   ```bash
   meson setup builddir
   meson compile -C builddir
   ```

4. Install the package:
   ```bash
   meson install -C builddir
   ```

## Usage 

### C++ Extensions

The `IndexBuilder` package includes C++ extensions for both tree-based and hash-based indexing.

#### Example: KDTree

Here is an example of how to use the KDTree implementation through the Python interface:

```python
import numpy as np
from kdtree import nearestNeighbor

# Example dataset
points = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
target = np.array([3.5, 4.5])

# Find the nearest neighbor
nearest = nearestNeighbor(points.tolist(), target.tolist())
print("Nearest Neighbor:", nearest)
```

#### Example: LSHIndex

Using the LSHIndex for approximate nearest neighbor search:

```python
import numpy as np
from lsh import insert, query

# Insert points into the LSH index
data_points = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
for point in data_points:
    insert(point.tolist(), num_hashes=5, bucket_size=10)

# Query the LSH index
query_point = np.array([3.5, 4.5])
results = query(query_point.tolist())
print("LSH Query Results:", results)
```

### Dependencies

The `IndexBuilder` package has the following dependencies:

- Python 3.10 or later
- NumPy
- SciPy

For development, you may also install:

- pytest
- uv

This package is intended for users looking to implement high-dimensional indexing for similarity searches in their applications.