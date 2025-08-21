project('swarmauri_crypto_sodium', 'c',
        version: '0.1.0',
        meson_version: '>=0.64.0',
        default_options: [
            'warning_level=2',
            'buildtype=release',
        ])

# Python installation
py = import('python').find_installation('python3')

# Get build options
use_system_libsodium = get_option('use_system_libsodium')
static_link = get_option('static_link')
debug_build = get_option('debug_build')

# Configure libsodium dependency
if use_system_libsodium
  libsodium_dep = dependency('libsodium', version: '>=1.0.11', required: true)
else
  # Try system libsodium first, then fallback to subproject
  libsodium_dep = dependency('libsodium', 
                            version: '>=1.0.11', 
                            required: false)
  
  if not libsodium_dep.found()
    # Use libsodium as a subproject
    libsodium_subproject_options = ['default_library=static']
    if debug_build
      libsodium_subproject_options += ['buildtype=debug']
    endif
    
    libsodium_proj = subproject('libsodium', 
                               default_options: libsodium_subproject_options)
    libsodium_dep = libsodium_proj.get_variable('libsodium_dep')
  endif
endif

# Create a C extension module that provides libsodium bindings
# This will be used by the Python code to load the bundled library
sodium_c_sources = [
    'src/sodium_loader.c'
]

# Define include directories
inc_dirs = include_directories('src')

# Configure extension module build options
ext_options = {}
if debug_build
  ext_options += {'c_args': ['-g', '-O0']}
else
  ext_options += {'c_args': ['-O2']}
endif

# Build shared library extension
sodium_ext = py.extension_module('_sodium_loader',
    sources: sodium_c_sources,
    dependencies: [libsodium_dep],
    include_directories: inc_dirs,
    install: true,
    install_tag: 'python-runtime',
    kwargs: ext_options
)

# Install Python source files
py.install_sources([
    'swarmauri_crypto_sodium/__init__.py',
    'swarmauri_crypto_sodium/SodiumCrypto.py',
], 
subdir: 'swarmauri_crypto_sodium',
install_tag: 'python-runtime')
