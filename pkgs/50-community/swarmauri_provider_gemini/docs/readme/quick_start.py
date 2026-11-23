import importlib

package = importlib.import_module("swarmauri_provider_gemini")
assert package.__name__ == "swarmauri_provider_gemini"
