# Create Python extension modules

exact_query_module = py.extension_module(
  'exact_query',
  'exact_query.cpp',
  dependencies: [py_dep, pybind11_dep, numpy_dep],
  install: true,
  install_dir: py.get_install_dir() / 'QueryEngine'
)

approx_query_module = py.extension_module(
  'approx_query',
  'approx_query.cpp',
  dependencies: [py_dep, pybind11_dep, numpy_dep],
  install: true,
  install_dir: py.get_install_dir() / 'QueryEngine'
)


# Install Python sources
py.install_sources(
  '__init__.py',
  subdir: 'QueryEngine'
)