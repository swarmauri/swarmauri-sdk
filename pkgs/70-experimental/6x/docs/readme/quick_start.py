import importlib

package = importlib.import_module("6x")
assert package.__name__ == "6x"
