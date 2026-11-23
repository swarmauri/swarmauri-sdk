import importlib

package = importlib.import_module("swarmauri_agent_realtime")
assert package.__name__ == "swarmauri_agent_realtime"
