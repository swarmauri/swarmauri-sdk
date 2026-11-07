project('IndexBuilder', 'cpp',
  version: '0.1.0',
  default_options: ['cpp_std=c++17', 'warning_level=3']
)

# Find the Python installation
py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

# Find pybind11
pybind11_dep = dependency('pybind11', required: true)

# Create Python extension modules


numpy_include = run_command(py, ['-c', 'import numpy; print(numpy.get_include())'], check: true).stdout().strip()
numpy_dep = declare_dependency(include_directories: include_directories(numpy_include))

# Include directory for the main submodule
subdir('IndexBuilder')