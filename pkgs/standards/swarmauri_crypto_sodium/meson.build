project('swarmauri_crypto_sodium', 'c',
        version: '0.1.0',
        meson_version: '>=0.64.0',
        default_options: [
            'warning_level=2',
            'buildtype=release',
        ])

# Python installation
py = import('python').find_installation('python3')

# Always build and bundle libsodium as a subproject so the Python package
# ships with the latest available version.
libsodium_proj = subproject('libsodium', default_options: ['default_library=static'])
libsodium_dep = libsodium_proj.get_variable('libsodium_dep')

# Create a C extension module that provides libsodium bindings
# This will be used by the Python code to load the bundled library
sodium_c_sources = [
    'src/sodium_loader.c'
]

# Define include directories
inc_dirs = include_directories('src')

# Build shared library extension with optimization
sodium_ext = py.extension_module('_sodium_loader',
    sources: sodium_c_sources,
    dependencies: [libsodium_dep],
    include_directories: inc_dirs,
    install: true,
    install_tag: 'python-runtime',
    c_args: ['-O2'],
)

# Install Python source files
py.install_sources([
    'swarmauri_crypto_sodium/__init__.py',
    'swarmauri_crypto_sodium/SodiumCrypto.py',
],
subdir: 'swarmauri_crypto_sodium',
install_tag: 'python-runtime')
