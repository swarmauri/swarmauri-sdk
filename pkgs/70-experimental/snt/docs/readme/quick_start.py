import importlib

package = importlib.import_module("snt")
assert package.__name__ == "snt"
