import importlib

package = importlib.import_module("swarmauri_keyprovider_pkcs11")
assert package.__name__ == "swarmauri_keyprovider_pkcs11"
