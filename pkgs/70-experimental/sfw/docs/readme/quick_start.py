import importlib

package = importlib.import_module("sfw")
assert package.__name__ == "sfw"
