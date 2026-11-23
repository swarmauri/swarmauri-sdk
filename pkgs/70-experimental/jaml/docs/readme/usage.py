import importlib

package = importlib.import_module("jaml")
assert package.__name__ == "jaml"
