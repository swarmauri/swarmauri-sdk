project('swarmauri_crypto_sodium', version: '0.1.0', meson_version: '>=0.64.0')

py = import('python').find_installation()
library = run_command(
    py, files('build_libsodium.py'), meson.current_build_dir(), check: true,
).stdout().strip()

py.install_sources([
    'swarmauri_crypto_sodium/__init__.py',
    'swarmauri_crypto_sodium/SodiumCrypto.py',
], subdir: 'swarmauri_crypto_sodium', pure: false)
install_data(library, install_dir: py.get_install_dir(pure: false) / 'swarmauri_crypto_sodium')
