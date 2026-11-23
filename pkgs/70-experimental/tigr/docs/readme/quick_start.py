import importlib

package = importlib.import_module("tigr")
assert package.__name__ == "tigr"
