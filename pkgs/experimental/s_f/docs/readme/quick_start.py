import importlib

package = importlib.import_module("s_f")
assert package.__name__ == "s_f"
