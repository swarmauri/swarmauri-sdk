import importlib

package = importlib.import_module("swarmauri_transport_aws_eventstream")
assert package.__name__ == "swarmauri_transport_aws_eventstream"
