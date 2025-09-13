# DistanceMetrics

<p align="center">
    <a href="https://pypi.org/project/DistanceMetrics/">
        <img src="https://img.shields.io/pypi/dm/DistanceMetrics" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/RapidSimilarity/DistanceMetrics/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/RapidSimilarity/DistanceMetrics.svg"/></a>
    <a href="https://pypi.org/project/DistanceMetrics/">
        <img src="https://img.shields.io/pypi/pyversions/DistanceMetrics" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/DistanceMetrics/">
        <img src="https://img.shields.io/pypi/l/DistanceMetrics" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/DistanceMetrics/">
        <img src="https://img.shields.io/pypi/v/DistanceMetrics?label=DistanceMetrics&color=green" alt="PyPI - DistanceMetrics"/></a>
</p>

---


## Purpose
The `DistanceMetrics` package provides core distance and similarity measures, including implementations of various distance functions such as Euclidean distance and cosine similarity to evaluate similarity between high-dimensional vectors.

## Authors
- Michael Nwogha

## Installation

To install the `DistanceMetrics` package, you will need to have Python 3.10 or later and the Meson build system installed. You can install the required dependencies using pip:

```bash
pip install numpy scipy meson ninja pybind11
```

Then, navigate to the root directory of the package and run the following commands:

```bash
meson setup builddir
meson compile -C builddir
meson install -C builddir
```

## Usage 

### Python Interface

Once installed, you can use the `DistanceMetrics` package in your Python code as follows:

```python
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
```

### C++ Implementation Example

The package includes C++ extensions for the distance calculations. Below is an example of how to use the C++ functionalities directly:

#### C++ Code Example
```cpp
#include <iostream>
#include "DistanceMetrics/euclidean.h"
#include "DistanceMetrics/cosine.h"

int main() {
    std::vector<double> a = {1.0, 2.0, 3.0};
    std::vector<double> b = {4.0, 5.0, 6.0};
    
    double euclidean_dist = euclidean_distance(a, b);
    double cosine_sim = cosine_similarity(a, b);
    
    std::cout << "Euclidean Distance: " << euclidean_dist << std::endl;
    std::cout << "Cosine Similarity: " << cosine_sim << std::endl;
    
    return 0;
}
```

## Testing and Validation

The package includes tests that can be run using pytest. To execute the tests, navigate to the root directory of the package and run:

```bash
pytest
```

This will ensure that all functionalities are working as expected.

## Dependencies
The `DistanceMetrics` package relies on the following Python packages:
- `numpy`
- `scipy`
- `meson-python`
- `ninja`
- `pybind11`

Make sure to install these dependencies before building the package.