#include <Python.h>
#include <numpy/arrayobject.h>
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

// Python interface for the ApproximateQueryEngine
static PyObject* approx_query(PyObject* self, PyObject* args) {
    PyObject* dataset_obj;
    PyObject* query_point_obj;
    size_t num_neighbors;
    double accuracy;

    if (!PyArg_ParseTuple(args, "OOd", &dataset_obj, &query_point_obj, &num_neighbors, &accuracy)) {
        return NULL;
    }

    // Convert dataset from Python list to C++ vector
    std::vector<std::vector<double>> dataset;
    if (!PyList_Check(dataset_obj)) {
        return NULL;
    }
    for (Py_ssize_t i = 0; i < PyList_Size(dataset_obj); ++i) {
        PyObject* item = PyList_GetItem(dataset_obj, i);
        if (!PyList_Check(item)) {
            return NULL;
        }
        std::vector<double> point;
        for (Py_ssize_t j = 0; j < PyList_Size(item); ++j) {
            PyObject* coord = PyList_GetItem(item, j);
            point.push_back(PyFloat_AsDouble(coord));
        }
        dataset.push_back(point);
    }

    // Convert query point from Python list to C++ vector
    std::vector<double> query_point;
    if (!PyList_Check(query_point_obj)) {
        return NULL;
    }
    for (Py_ssize_t i = 0; i < PyList_Size(query_point_obj); ++i) {
        PyObject* coord = PyList_GetItem(query_point_obj, i);
        query_point.push_back(PyFloat_AsDouble(coord));
    }

    // Create query engine and perform search
    ApproximateQueryEngine engine(num_neighbors, accuracy);
    std::vector<size_t> result = engine.query(dataset, query_point);

    // Convert result to Python list
    PyObject* result_list = PyList_New(result.size());
    for (size_t i = 0; i < result.size(); ++i) {
        PyList_SetItem(result_list, i, PyLong_FromSize_t(result[i]));
    }

    return result_list;
}

// Module definition
static PyMethodDef ApproxQueryMethods[] = {
    {"approx_query", approx_query, METH_VARARGS, "Execute an approximate similarity query."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef approxquerymodule = {
    PyModuleDef_HEAD_INIT,
    "approx_query",
    NULL,
    -1,
    ApproxQueryMethods
};

PyMODINIT_FUNC PyInit_approx_query(void) {
    import_array(); // Initialize NumPy API
    return PyModule_Create(&approxquerymodule);
}