import importlib

package = importlib.import_module("swarmauri_tool_gmail")
assert package.__name__ == "swarmauri_tool_gmail"
