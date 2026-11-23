import importlib

package = importlib.import_module("zr0")
assert package.__name__ == "zr0"
