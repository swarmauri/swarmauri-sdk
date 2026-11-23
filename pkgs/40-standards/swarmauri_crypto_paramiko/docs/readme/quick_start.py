import importlib

package = importlib.import_module("swarmauri_crypto_paramiko")
assert package.__name__ == "swarmauri_crypto_paramiko"
