import importlib

package = importlib.import_module("swarmauri_parser_asn1")
assert package.__name__ == "swarmauri_parser_asn1"
