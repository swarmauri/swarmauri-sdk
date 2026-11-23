import importlib

package = importlib.import_module("jz")
assert package.__name__ == "jz"
