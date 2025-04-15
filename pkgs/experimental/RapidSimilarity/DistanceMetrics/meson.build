project('DistanceMetrics', 'cpp',
  version: '0.1.0',
  default_options: ['cpp_std=c++17', 'warning_level=3']
)

# Find the Python installation
py_mod = import('python')
py = py_mod.find_installation()
py_dep = py.dependency()

# Find pybind11
pybind11_dep = dependency('pybind11', required: true)

# Create Python extension modules
numpy_dep = dependency('numpy', required: true)
numpy_dep = dependency('numpy', required: true)


# Include directory for the main submodule
subdir('DistanceMetrics')