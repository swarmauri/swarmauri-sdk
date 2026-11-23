import importlib

package = importlib.import_module("swarmauri_certs_pkcs11")
assert package.__name__ == "swarmauri_certs_pkcs11"
