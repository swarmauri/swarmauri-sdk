import importlib

package = importlib.import_module("swarmauri_package_maintenance_demo")
assert package.__name__ == "swarmauri_package_maintenance_demo"
