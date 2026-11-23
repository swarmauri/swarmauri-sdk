import importlib

package = importlib.import_module("ymls")
assert package.__name__ == "ymls"
