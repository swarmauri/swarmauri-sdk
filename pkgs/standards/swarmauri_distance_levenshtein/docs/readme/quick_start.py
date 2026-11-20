import importlib

package = importlib.import_module("swarmauri_distance_levenshtein")
assert package.__name__ == "swarmauri_distance_levenshtein"
