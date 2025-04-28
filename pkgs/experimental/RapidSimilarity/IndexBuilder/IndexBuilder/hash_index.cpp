#include <Python.h>
#include <numpy/arrayobject.h>
#include <vector>
#include <unordered_map>
#include <random>
#include <cmath>
#include <stdexcept>

class LSHIndex {
public:
    LSHIndex(int num_hashes, int bucket_size) : num_hashes(num_hashes), bucket_size(bucket_size) {
        if (bucket_size <= 0) {
            throw std::invalid_argument("Bucket size must be greater than 0.");
        }
        // Initialize hash functions
        for (int i = 0; i < num_hashes; ++i) {
            hash_functions.emplace_back(generate_random_hash_function());
        }
    }

    void insert(const std::vector<float>& data_point) {
        std::vector<int> hashes(num_hashes);
        for (int i = 0; i < num_hashes; ++i) {
            hashes[i] = hash_functions[i](data_point);
        }
        for (int i = 0; i < num_hashes; ++i) {
            buckets[hashes[i]].push_back(data_point);
            if (buckets[hashes[i]].size() > bucket_size) {
                buckets[hashes[i]].pop_back(); // Maintain bucket size
            }
        }
    }

    std::vector<std::vector<float>> query(const std::vector<float>& data_point) {
        std::unordered_map<int, std::vector<float>> result;
        for (int i = 0; i < num_hashes; ++i) {
            int hash_value = hash_functions[i](data_point);
            result[hash_value] = buckets[hash_value];
        }
        std::vector<std::vector<float>> output;
        for (const auto& entry : result) {
            output.insert(output.end(), entry.second.begin(), entry.second.end());
        }
        return output;
    }

private:
    int num_hashes;
    int bucket_size;
    std::unordered_map<int, std::vector<std::vector<float>>> buckets;
    std::vector<std::function<int(const std::vector<float>&)>> hash_functions;

    std::function<int(const std::vector<float>&)> generate_random_hash_function() {
        std::default_random_engine generator;
        std::uniform_real_distribution<float> distribution(-1.0, 1.0);
        std::vector<float> random_vector(2);
        for (int i = 0; i < 2; ++i) {
            random_vector[i] = distribution(generator);
        }
        return [random_vector](const std::vector<float>& point) {
            float dot_product = random_vector[0] * point[0] + random_vector[1] * point[1];
            return static_cast<int>(std::floor(dot_product));
        };
    }
};

static PyObject* LSHIndex_insert(PyObject* self, PyObject* args) {
    PyObject* data;
    int num_hashes, bucket_size;

    if (!PyArg_ParseTuple(args, "Oii", &data, &num_hashes, &bucket_size)) {
        return NULL;
    }

    if (!PyArray_Check(data)) {
        PyErr_SetString(PyExc_TypeError, "Input must be a numpy array.");
        return NULL;
    }

    int n = (int)PyArray_Size(data);
    std::vector<float> data_point(n);
    for (int i = 0; i < n; ++i) {
        data_point[i] = static_cast<float>(*static_cast<float*>(PyArray_GETPTR1((PyArrayObject*)data, i)));
    }

    LSHIndex index(num_hashes, bucket_size);
    index.insert(data_point);
    
    Py_RETURN_NONE;
}

static PyObject* LSHIndex_query(PyObject* self, PyObject* args) {
    PyObject* data;

    if (!PyArg_ParseTuple(args, "O", &data)) {
        return NULL;
    }

    if (!PyArray_Check(data)) {
        PyErr_SetString(PyExc_TypeError, "Input must be a numpy array.");
        return NULL;
    }

    int n = (int)PyArray_Size(data);
    std::vector<float> data_point(n);
    for (int i = 0; i < n; ++i) {
        data_point[i] = static_cast<float>(*static_cast<float*>(PyArray_GETPTR1((PyArrayObject*)data, i)));
    }

    // Assuming we have an instance of LSHIndex called `index`
    std::vector<std::vector<float>> results = index.query(data_point);
    
    // Convert results to a Python list
    PyObject* result_list = PyList_New(results.size());
    for (size_t i = 0; i < results.size(); ++i) {
        PyObject* result_array = PyArray_FromAny(
            PyList_New(results[i].size()),
            PyArray_DescrFromType(NPY_FLOAT),
            1, 1,
            NPY_ARRAY_DEFAULT,
            NULL
        );
        for (size_t j = 0; j < results[i].size(); ++j) {
            *static_cast<float*>(PyArray_GETPTR1((PyArrayObject*)result_array, j)) = results[i][j];
        }
        PyList_SetItem(result_list, i, result_array);
    }
    
    return result_list;
}

static PyMethodDef LSHMethods[] = {
    {"insert", LSHIndex_insert, METH_VARARGS, "Insert a data point into the LSH index."},
    {"query", LSHIndex_query, METH_VARARGS, "Query the LSH index."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef lshmodule = {
    PyModuleDef_HEAD_INIT,
    "lsh",   // name of module
    NULL, // module documentation, may be NULL
    -1,       // size of per-interpreter state of the module,
    LSHMethods
};

PyMODINIT_FUNC PyInit_lsh(void) {
    import_array();  // Necessary for initializing NumPy API
    return PyModule_Create(&lshmodule);
}