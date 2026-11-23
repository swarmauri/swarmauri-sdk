import importlib

package = importlib.import_module("swarmauri_transport_websocket")
assert package.__name__ == "swarmauri_transport_websocket"
