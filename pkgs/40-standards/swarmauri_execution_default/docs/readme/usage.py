import importlib

package = importlib.import_module("swarmauri_execution_default")
assert package.__name__ == "swarmauri_execution_default"
