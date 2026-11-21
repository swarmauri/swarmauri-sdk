import importlib

package = importlib.import_module("6w")
assert package.__name__ == "6w"
