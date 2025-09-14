# QueryEngine

<p align="center">
    <a href="https://pypi.org/project/QueryEngine/">
        <img src="https://img.shields.io/pypi/dm/QueryEngine" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/RapidSimilarity/QueryEngine/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/RapidSimilarity/QueryEngine.svg"/></a>
    <a href="https://pypi.org/project/QueryEngine/">
        <img src="https://img.shields.io/pypi/pyversions/QueryEngine" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/QueryEngine/">
        <img src="https://img.shields.io/pypi/l/QueryEngine" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/QueryEngine/">
        <img src="https://img.shields.io/pypi/v/QueryEngine?label=QueryEngine&color=green" alt="PyPI - QueryEngine"/></a>
</p>

---


## Description
The `QueryEngine` package provides a Python interface for performing both exact and approximate similarity searches on indexes built by the `IndexBuilder`. The underlying implementation leverages C++ optimizations for enhanced speed and efficiency.

## Purpose
The primary purpose of this package is to execute similarity search queries over pre-built indexes, allowing users to efficiently retrieve similar items based on various criteria.

## Authors
- Michael Nwogha

## Installation
To install the `QueryEngine` package, ensure you have the following dependencies installed:

- Python 3.10 or later
- Meson build system
- Ninja build system
- NumPy
- Pybind11

You can install the necessary packages via pip:

```bash
pip install numpy pybind11 meson
```

After installing the required dependencies, clone the repository and navigate to the project directory. You can then build and install the package using Meson:

```bash
meson setup build
meson compile -C build
meson install -C build
```

## Usage

### Exact Similarity Search
To perform an exact similarity search, utilize the `exact_nearest_neighbors` function. Here is how you can do it:

```python
import numpy as np
from QueryEngine import exact_nearest_neighbors

# Example dataset
data = np.array([1.0, 2.5, 3.3, 4.8], dtype=np.float32)
query_value = 3.0
k = 2

# Perform exact similarity search
neighbors = exact_nearest_neighbors(data, query_value, k)
print("Exact Neighbors:", neighbors)
```

### Approximate Similarity Search
For approximate searches, use the `approx_query` function. Below is an example of how to perform an approximate query:

```python
import numpy as np
from QueryEngine import approx_query

# Example dataset and query
dataset = [[1.0, 2.0], [1.5, 2.5], [3.0, 4.0], [5.0, 6.0]]
query_point = [1.2, 2.1]
num_neighbors = 2
accuracy = 0.9

# Perform approximate similarity search
approx_neighbors = approx_query(dataset, query_point, num_neighbors, accuracy)
print("Approximate Neighbors:", approx_neighbors)
```

## C++ Build Instructions
The C++ components of `QueryEngine` are built using the Meson build system. Ensure you have configured the `meson.build` file correctly to include necessary dependencies. The following code snippets illustrate the core structure of the C++ implementation.

### C++ File Example: `exact_query.cpp`
```cpp
#include <Python.h>
#include <numpy/arrayobject.h>
#include <vector>
#include <algorithm>

// Function to find exact nearest neighbors
std::vector<int> exact_nearest_neighbors(const std::vector<float>& dataset, float query, size_t k) {
    // Implementation here
}

// Python wrapper for exact_nearest_neighbors
static PyObject* py_exact_nearest_neighbors(PyObject* self, PyObject* args) {
    // Implementation here
}

// Module initialization
PyMODINIT_FUNC PyInit_QueryEngine(void) {
    import_array();  // Initialize NumPy API
    return PyModule_Create(&queryenginemodule);
}
```

### C++ File Example: `approx_query.cpp`
```cpp
#include <Python.h>
#include <numpy/arrayobject.h>
#include <vector>
#include <algorithm>

// Class for approximate nearest neighbor search
class ApproximateQueryEngine {
public:
    // Implementation here
};

// Python interface for the ApproximateQueryEngine
static PyObject* approx_query(PyObject* self, PyObject* args) {
    // Implementation here
}

// Module initialization
PyMODINIT_FUNC PyInit_approx_query(void) {
    import_array(); // Initialize NumPy API
    return PyModule_Create(&approxquerymodule);
}
```

## Testing and Validation
The package includes unit tests to ensure functionality and correctness. You can run the tests using pytest:

```bash
pytest tests/
```

Make sure to check for any failing tests and validate the output accordingly.