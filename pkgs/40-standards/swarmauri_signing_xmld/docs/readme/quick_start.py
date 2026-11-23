import importlib

package = importlib.import_module("swarmauri_signing_xmld")
assert package.__name__ == "swarmauri_signing_xmld"
