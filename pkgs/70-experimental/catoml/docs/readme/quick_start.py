import importlib

package = importlib.import_module("catoml")
assert package.__name__ == "catoml"
