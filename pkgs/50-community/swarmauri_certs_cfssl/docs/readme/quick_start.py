import importlib

package = importlib.import_module("swarmauri_certs_cfssl")
assert package.__name__ == "swarmauri_certs_cfssl"
