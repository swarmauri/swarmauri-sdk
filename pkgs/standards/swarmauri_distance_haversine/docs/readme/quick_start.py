import importlib

package = importlib.import_module("swarmauri_distance_haversine")
assert package.__name__ == "swarmauri_distance_haversine"
