#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <vector>
#include <cmath>

// Function to compute dot product of two vectors
double dot_product(const std::vector<double>& vec1, const std::vector<double>& vec2) {
    double result = 0.0;
    for (size_t i = 0; i < vec1.size(); ++i) {
        result += vec1[i] * vec2[i];
    }
    return result;
}

// Function to compute the norm of a vector
double norm(const std::vector<double>& vec) {
    return std::sqrt(dot_product(vec, vec));
}

// Function to compute cosine similarity between two vectors
double cosine_similarity(const std::vector<double>& vec1, const std::vector<double>& vec2) {
    double norm1 = norm(vec1);
    double norm2 = norm(vec2);
    
    // Handle edge case for zero vectors
    if (norm1 == 0.0 || norm2 == 0.0) {
        return 0.0; // Cosine similarity is undefined for zero vectors
    }
    
    return dot_product(vec1, vec2) / (norm1 * norm2);
}


PYBIND11_MODULE(cosine, module) {
    module.def("cosine_similarity", [](py::object first, py::object second) {
        if (!PySequence_Check(first.ptr()) || !PySequence_Check(second.ptr()))
            throw py::type_error("Expected lists for vectors.");
        auto a = first.cast<std::vector<double>>();
        auto b = second.cast<std::vector<double>>();
        if (a.size() != b.size()) throw py::value_error("Vectors must be of the same length.");
        return cosine_similarity(a, b);
    });
}
