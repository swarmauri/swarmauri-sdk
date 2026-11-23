import importlib

package = importlib.import_module("zdx")
assert package.__name__ == "zdx"
