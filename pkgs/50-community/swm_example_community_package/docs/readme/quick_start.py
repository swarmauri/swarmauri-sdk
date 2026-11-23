import importlib

package = importlib.import_module("swm_example_community_package")
assert package.__name__ == "swm_example_community_package"
