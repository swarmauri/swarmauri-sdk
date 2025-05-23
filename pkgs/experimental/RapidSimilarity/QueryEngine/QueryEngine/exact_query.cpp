#include <Python.h>
#include <numpy/arrayobject.h>
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

// Python wrapper for exact_nearest_neighbors
static PyObject* py_exact_nearest_neighbors(PyObject* self, PyObject* args) {
    PyObject* py_dataset;
    float query;
    size_t k;

    // Parse the input tuple
    if (!PyArg_ParseTuple(args, "Ofn", &py_dataset, &query, &k)) {
        return NULL;
    }

    // Convert input NumPy array to std::vector<float>
    PyArrayObject* dataset_array = reinterpret_cast<PyArrayObject*>(py_dataset);
    if (!PyArray_Check(dataset_array)) {
        PyErr_SetString(PyExc_TypeError, "Input must be a NumPy array");
        return NULL;
    }

    npy_intp* shape = PyArray_DIMS(dataset_array);
    size_t size = shape[0];
    std::vector<float> dataset(size);
    for (size_t i = 0; i < size; ++i) {
        dataset[i] = static_cast<float>(*reinterpret_cast<float*>(PyArray_GETPTR1(dataset_array, i)));
    }

    // Call the exact nearest neighbors function
    std::vector<int> neighbors = exact_nearest_neighbors(dataset, query, k);

    // Create a new Python list to return the results
    PyObject* py_neighbors = PyList_New(neighbors.size());
    for (size_t i = 0; i < neighbors.size(); ++i) {
        PyList_SetItem(py_neighbors, i, PyLong_FromSize_t(neighbors[i]));
    }

    return py_neighbors;
}

// Module method definitions
static PyMethodDef QueryEngineMethods[] = {
    {"exact_nearest_neighbors", py_exact_nearest_neighbors, METH_VARARGS, "Find exact nearest neighbors"},
    {NULL, NULL, 0, NULL}  // Sentinel
};

// Module definition
static struct PyModuleDef queryenginemodule = {
    PyModuleDef_HEAD_INIT,
    "QueryEngine",   // name of module
    NULL,            // module documentation, may be NULL
    -1,              // size of per-interpreter state of the module,
                     // or -1 if the module keeps state in global variables.
    QueryEngineMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_QueryEngine(void) {
    import_array();  // Necessary for NumPy API initialization
    return PyModule_Create(&queryenginemodule);
}