# Create Python extension modules

tree_index_module = py.extension_module(
  'tree_index',
  'tree_index.cpp',
  dependencies: [py_dep, pybind11_dep, numpy_dep],
  install: true,
  install_dir: py.get_install_dir() / 'IndexBuilder'
)

hash_index_module = py.extension_module(
  'hash_index',
  'hash_index.cpp',
  dependencies: [py_dep, pybind11_dep, numpy_dep],
  install: true,
  install_dir: py.get_install_dir() / 'IndexBuilder'
)


# Install Python sources
py.install_sources(
  '__init__.py',
  subdir: 'IndexBuilder'
)