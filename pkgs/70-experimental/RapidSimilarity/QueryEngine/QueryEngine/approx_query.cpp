#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <vector>
#include <algorithm>
#include <random>
#include <cmath>

// Function to compute the Euclidean distance between two points
double euclidean_distance(const std::vector<double>& a, const std::vector<double>& b) {
    double sum = 0.0;
    for (size_t i = 0; i < a.size(); ++i) {
        double diff = a[i] - b[i];
        sum += diff * diff;
    }
    return std::sqrt(sum);
}

// Class for approximate nearest neighbor search
class ApproximateQueryEngine {
public:
    ApproximateQueryEngine(size_t num_neighbors, double accuracy)
        : num_neighbors_(num_neighbors), accuracy_(accuracy) {}

    // Method to perform the approximate nearest neighbor search
    std::vector<size_t> query(const std::vector<std::vector<double>>& dataset, const std::vector<double>& query_point) {
        std::vector<std::pair<double, size_t>> distances;
        
        // Calculate distances
        for (size_t i = 0; i < dataset.size(); ++i) {
            double dist = euclidean_distance(dataset[i], query_point);
            distances.emplace_back(dist, i);
        }

        // Sort distances and retrieve nearest neighbors
        std::sort(distances.begin(), distances.end());
        std::vector<size_t> neighbors;
        for (size_t i = 0; i < num_neighbors_ && i < distances.size(); ++i) {
            neighbors.push_back(distances[i].second);
        }
        
        return neighbors;
    }

private:
    size_t num_neighbors_;
    double accuracy_;
};


PYBIND11_MODULE(approx_query, module) {
    module.def("approx_query", [](const std::vector<std::vector<double>>& dataset, const std::vector<double>& point, py::ssize_t k, double accuracy) {
        if (k < 0) throw py::value_error("k must be nonnegative");
        if (!(accuracy >= 0.0 && accuracy <= 1.0)) throw py::value_error("accuracy must be between zero and one");
        for (const auto& item : dataset)
            if (item.size() != point.size()) throw py::value_error("Vector dimensions must match");
        ApproximateQueryEngine engine(static_cast<size_t>(k), accuracy);
        return engine.query(dataset, point);
    });
}
