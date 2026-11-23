import importlib

package = importlib.import_module("swarmauri_provider_amazon_nova")
assert package.__name__ == "swarmauri_provider_amazon_nova"
