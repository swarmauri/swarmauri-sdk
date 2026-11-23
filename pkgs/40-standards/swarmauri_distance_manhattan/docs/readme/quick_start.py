import importlib

package = importlib.import_module("swarmauri_distance_manhattan")
assert package.__name__ == "swarmauri_distance_manhattan"
