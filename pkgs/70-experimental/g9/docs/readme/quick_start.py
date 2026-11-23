import importlib

package = importlib.import_module("g9")
assert package.__name__ == "g9"
