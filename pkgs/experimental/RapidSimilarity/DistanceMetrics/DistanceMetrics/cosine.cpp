#include <Python.h>
#include <numpy/arrayobject.h>
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

// Python wrapper for cosine_similarity function
static PyObject* py_cosine_similarity(PyObject* self, PyObject* args) {
    PyObject *vec1_obj, *vec2_obj;
    
    // Parse input tuples
    if (!PyArg_ParseTuple(args, "OO", &vec1_obj, &vec2_obj)) {
        return NULL;
    }

    // Convert Python lists to std::vector
    std::vector<double> vec1, vec2;
    if (PyList_Check(vec1_obj) && PyList_Check(vec2_obj)) {
        Py_ssize_t size1 = PyList_Size(vec1_obj);
        Py_ssize_t size2 = PyList_Size(vec2_obj);
        
        if (size1 != size2) {
            PyErr_SetString(PyExc_ValueError, "Vectors must be of the same length.");
            return NULL;
        }

        for (Py_ssize_t i = 0; i < size1; ++i) {
            PyObject *item = PyList_GetItem(vec1_obj, i);
            vec1.push_back(PyFloat_AsDouble(item));
            item = PyList_GetItem(vec2_obj, i);
            vec2.push_back(PyFloat_AsDouble(item));
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "Expected lists for vectors.");
        return NULL;
    }

    // Compute cosine similarity
    double result = cosine_similarity(vec1, vec2);
    
    return Py_BuildValue("d", result); // Return result as a Python float
}

// Module method definitions
static PyMethodDef CosineMethods[] = {
    {"cosine_similarity", py_cosine_similarity, METH_VARARGS, "Compute cosine similarity between two vectors."},
    {NULL, NULL, 0, NULL} // Sentinel
};

// Module definition
static struct PyModuleDef cosine_module = {
    PyModuleDef_HEAD_INIT,
    "cosine", // Name of the module
    NULL, // Module documentation
    -1, // Size of per-interpreter state of the module
    CosineMethods // Method definitions
};

// Module initialization function
PyMODINIT_FUNC PyInit_cosine(void) {
    import_array(); // Initialize NumPy API
    return PyModule_Create(&cosine_module);
}