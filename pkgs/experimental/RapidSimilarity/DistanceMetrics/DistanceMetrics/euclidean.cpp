#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <cmath>
#include <vector>

// Function to calculate Euclidean distance between two vectors
static double euclidean_distance(const std::vector<double>& a, const std::vector<double>& b) {
    double sum = 0.0;
    for (size_t i = 0; i < a.size(); ++i) {
        double diff = a[i] - b[i];
        sum += diff * diff; // Accumulate squared differences
    }
    return std::sqrt(sum); // Return the square root of the sum
}


PYBIND11_MODULE(euclidean, module) {
    module.def("euclidean_distance", [](py::array_t<double, py::array::c_style | py::array::forcecast> a, py::array_t<double, py::array::c_style | py::array::forcecast> b) {
        if (a.ndim() != 1 || b.ndim() != 1) throw py::value_error("Expected one-dimensional vectors.");
        if (a.size() != b.size()) throw py::value_error("Input arrays must have the same size.");
        return euclidean_distance({a.data(), a.data() + a.size()}, {b.data(), b.data() + b.size()});
    });
}
