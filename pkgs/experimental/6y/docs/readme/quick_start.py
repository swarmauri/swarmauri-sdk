import importlib

package = importlib.import_module("6y")
assert package.__name__ == "6y"
