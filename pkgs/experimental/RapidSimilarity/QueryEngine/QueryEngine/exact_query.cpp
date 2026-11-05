#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <cmath>
#include <vector>
#include <algorithm>

// Function to find exact nearest neighbors
std::vector<int> exact_nearest_neighbors(const std::vector<float>& dataset, float query, size_t k) {
    std::vector<std::pair<float, int>> distances;
    for (size_t i = 0; i < dataset.size(); ++i) {
        distances.emplace_back(std::abs(dataset[i] - query), i);
    }
    std::sort(distances.begin(), distances.end());
    
    std::vector<int> neighbors;
    for (size_t i = 0; i < k && i < distances.size(); ++i) {
        neighbors.push_back(distances[i].second);
    }
    return neighbors;
}


PYBIND11_MODULE(exact_query, module) {
    module.def("exact_nearest_neighbors", [](py::array_t<float, py::array::c_style | py::array::forcecast> values, float query, py::ssize_t k) {
        if (values.ndim() != 1) throw py::value_error("Expected a one-dimensional dataset");
        if (values.size() == 0) throw py::index_error("Dataset is empty");
        if (k < 0) throw py::value_error("k must be nonnegative");
        return exact_nearest_neighbors({values.data(), values.data() + values.size()}, query, static_cast<size_t>(k));
    });
}
