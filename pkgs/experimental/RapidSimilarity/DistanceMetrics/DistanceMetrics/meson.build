# Create Python extension modules

euclidean_module = py.extension_module(
  'euclidean',
  'euclidean.cpp',
  dependencies: [py_dep, pybind11_dep, numpy_dep],
  install: true,
  install_dir: py.get_install_dir() / 'DistanceMetrics'
)

cosine_module = py.extension_module(
  'cosine',
  'cosine.cpp',
  dependencies: [py_dep, pybind11_dep, numpy_dep],
  install: true,
  install_dir: py.get_install_dir() / 'DistanceMetrics'
)


# Install Python sources
py.install_sources(
  '__init__.py',
  subdir: 'DistanceMetrics'
)