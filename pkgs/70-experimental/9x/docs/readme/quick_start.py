import importlib

package = importlib.import_module("9x")
assert package.__name__ == "9x"
