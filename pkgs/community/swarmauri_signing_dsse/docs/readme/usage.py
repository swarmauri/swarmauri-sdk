import importlib

package = importlib.import_module("swarmauri_signing_dsse")
assert package.__name__ == "swarmauri_signing_dsse"
