#include <Python.h>
#include <numpy/arrayobject.h>
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

// Python wrapper for the Euclidean distance function
static PyObject* py_euclidean_distance(PyObject* self, PyObject* args) {
    PyObject *list_a, *list_b;
    
    // Parse Python arguments
    if (!PyArg_ParseTuple(args, "OO", &list_a, &list_b)) {
        return NULL; // Return NULL on failure
    }

    // Ensure the input is numpy arrays
    if (!PyArray_Check(list_a) || !PyArray_Check(list_b)) {
        PyErr_SetString(PyExc_TypeError, "Both arguments must be numpy arrays.");
        return NULL;
    }

    // Convert numpy arrays to vectors
    double* data_a = static_cast<double*>(PyArray_DATA((PyArrayObject*)list_a));
    double* data_b = static_cast<double*>(PyArray_DATA((PyArrayObject*)list_b));
    npy_intp size_a = PyArray_SIZE((PyArrayObject*)list_a);
    npy_intp size_b = PyArray_SIZE((PyArrayObject*)list_b);

    if (size_a != size_b) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must have the same size.");
        return NULL;
    }

    std::vector<double> vec_a(data_a, data_a + size_a);
    std::vector<double> vec_b(data_b, data_b + size_b);
    
    // Calculate the Euclidean distance
    double distance = euclidean_distance(vec_a, vec_b);

    // Return the result as a Python float
    return PyFloat_FromDouble(distance);
}

// Method definitions for the module
static PyMethodDef DistanceMetricsMethods[] = {
    {"euclidean_distance", py_euclidean_distance, METH_VARARGS, "Calculate Euclidean distance between two vectors."},
    {NULL, NULL, 0, NULL} // Sentinel
};

// Module definition
static struct PyModuleDef distancemetricsmodule = {
    PyModuleDef_HEAD_INIT,
    "DistanceMetrics", // Module name
    NULL, // Module documentation
    -1, // Size of per-interpreter state of the module
    DistanceMetricsMethods // Methods of the module
};

// Module initialization function
PyMODINIT_FUNC PyInit_DistanceMetrics(void) {
    import_array(); // Initialize the NumPy API
    return PyModule_Create(&distancemetricsmodule); // Create the module
}