import importlib

package = importlib.import_module("swarmauri_invoker_default")
assert package.__name__ == "swarmauri_invoker_default"
