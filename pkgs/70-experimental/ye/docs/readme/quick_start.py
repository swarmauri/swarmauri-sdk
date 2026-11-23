import importlib

package = importlib.import_module("ye")
assert package.__name__ == "ye"
