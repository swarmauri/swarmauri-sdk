import importlib

package = importlib.import_module("6z")
assert package.__name__ == "6z"
