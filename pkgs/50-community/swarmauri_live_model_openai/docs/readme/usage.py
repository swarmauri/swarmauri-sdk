import importlib

package = importlib.import_module("swarmauri_live_model_openai")
assert package.__name__ == "swarmauri_live_model_openai"
