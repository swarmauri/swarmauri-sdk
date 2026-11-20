import importlib

package = importlib.import_module("swarmauri_live_model_gemini")
assert package.__name__ == "swarmauri_live_model_gemini"
