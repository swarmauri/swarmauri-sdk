import importlib

package = importlib.import_module("swm_example_package")
assert package.__name__ == "swm_example_package"
