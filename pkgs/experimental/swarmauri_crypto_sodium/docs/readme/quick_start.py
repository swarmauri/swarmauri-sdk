import importlib

package = importlib.import_module("swarmauri_crypto_sodium")
assert package.__name__ == "swarmauri_crypto_sodium"
