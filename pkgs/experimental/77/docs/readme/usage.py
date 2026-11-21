import importlib

package = importlib.import_module("77")
assert package.__name__ == "77"
