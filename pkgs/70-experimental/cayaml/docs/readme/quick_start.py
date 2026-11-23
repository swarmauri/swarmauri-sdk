import importlib

package = importlib.import_module("cayaml")
assert package.__name__ == "cayaml"
