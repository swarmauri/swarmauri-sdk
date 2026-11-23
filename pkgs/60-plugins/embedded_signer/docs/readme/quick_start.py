import importlib

package = importlib.import_module("EmbeddedSigner")
assert package.__name__ == "EmbeddedSigner"
