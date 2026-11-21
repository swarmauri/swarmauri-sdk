import importlib

package = importlib.import_module("swarmauri_tokens_sshsig")
assert package.__name__ == "swarmauri_tokens_sshsig"
