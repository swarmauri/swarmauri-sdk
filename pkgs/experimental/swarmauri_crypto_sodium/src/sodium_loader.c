#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <sodium.h>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#else
#include <dlfcn.h>
#endif

/* Forward declaration */
PyMODINIT_FUNC PyInit__sodium_loader(void);

/* Global variable to hold the loaded library handle (unused but reserved for future use) */
static void *libsodium_handle __attribute__((unused)) = NULL;

/* Function to get the path of the shared library containing this extension */
static PyObject *
get_library_path(PyObject *self, PyObject *args)
{
    (void)self;  /* Suppress unused parameter warning */
    (void)args;  /* Suppress unused parameter warning */
    
#if defined(_WIN32) || defined(_WIN64)
    HMODULE hModule = NULL;
    char path[MAX_PATH];
    
    if (GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | 
                          GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                          (LPCSTR) &PyInit__sodium_loader, &hModule)) {
        if (GetModuleFileName(hModule, path, MAX_PATH) != 0) {
            return PyUnicode_FromString(path);
        }
    }
    PyErr_SetString(PyExc_RuntimeError, "Could not determine library path on Windows");
    return NULL;
#else
    Dl_info info;
    if (dladdr((void*)PyInit__sodium_loader, &info) != 0) {
        return PyUnicode_FromString(info.dli_fname);
    }
    PyErr_SetString(PyExc_RuntimeError, "Could not determine library path");
    return NULL;
#endif
}

/* Function to initialize libsodium */
static PyObject *
init_sodium(PyObject *self, PyObject *args)
{
    (void)self;  /* Suppress unused parameter warning */
    (void)args;  /* Suppress unused parameter warning */
    
    if (sodium_init() < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to initialize libsodium");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

/* Function to get version info */
static PyObject *
get_sodium_version(PyObject *self, PyObject *args)
{
    (void)self;  /* Suppress unused parameter warning */
    (void)args;  /* Suppress unused parameter warning */
    
    return PyUnicode_FromString(sodium_version_string());
}

/* Function to check if sodium is available */
static PyObject *
is_sodium_available(PyObject *self, PyObject *args)
{
    (void)self;  /* Suppress unused parameter warning */
    (void)args;  /* Suppress unused parameter warning */
    
    Py_RETURN_TRUE;
}

/* Function to get function address as integer */
static PyObject *
get_function_address(PyObject *self, PyObject *args)
{
    (void)self;  /* Suppress unused parameter warning */
    
    const char *func_name;
    if (!PyArg_ParseTuple(args, "s", &func_name)) {
        return NULL;
    }
    
#if defined(_WIN32) || defined(_WIN64)
    HMODULE hModule = GetModuleHandle(NULL);
    FARPROC addr = GetProcAddress(hModule, func_name);
    if (!addr) {
        PyErr_SetString(PyExc_RuntimeError, "Could not find function on Windows");
        return NULL;
    }
    return PyLong_FromVoidPtr((void*)addr);
#else
    void *addr = dlsym(RTLD_DEFAULT, func_name);
    if (!addr) {
        PyErr_SetString(PyExc_RuntimeError, dlerror());
        return NULL;
    }
    return PyLong_FromVoidPtr(addr);
#endif
}

/* Method definitions */
static PyMethodDef SodiumLoaderMethods[] = {
    {"get_library_path", get_library_path, METH_NOARGS,
     "Get the path of the shared library."},
    {"init_sodium", init_sodium, METH_NOARGS,
     "Initialize libsodium library."},
    {"get_sodium_version", get_sodium_version, METH_NOARGS,
     "Get libsodium version string."},
    {"is_sodium_available", is_sodium_available, METH_NOARGS,
     "Check if libsodium is available."},
    {"get_function_address", get_function_address, METH_VARARGS,
     "Get the address of a function."},
    {NULL, NULL, 0, NULL}
};

/* Module definition */
static struct PyModuleDef sodiumloadermodule = {
    PyModuleDef_HEAD_INIT,
    "_sodium_loader",
    "Internal module for loading bundled libsodium",
    -1,
    SodiumLoaderMethods,
    NULL,  /* m_slots */
    NULL,  /* m_traverse */
    NULL,  /* m_clear */
    NULL   /* m_free */
};

/* Module initialization */
PyMODINIT_FUNC
PyInit__sodium_loader(void)
{
    return PyModule_Create(&sodiumloadermodule);
}