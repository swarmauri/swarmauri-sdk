import importlib

package = importlib.import_module("swarmauri_live_model_qwen")
assert package.__name__ == "swarmauri_live_model_qwen"
