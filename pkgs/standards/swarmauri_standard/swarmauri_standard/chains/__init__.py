from swarmauri_standard.utils._lazy_import import _lazy_import

chains_files = [
    ("swarmauri_standard.chains.CallableChain", "CallableChain"),
    ("swarmauri_standard.chains.ChainStep", "ChainStep"),
    ("swarmauri_standard.chains.PromptContextChain", "PromptContextChain"),
    ("swarmauri_standard.chains.ContextChain", "ContextChain"),
]

# Lazy loading of chain classes, storing them in variables
for module_name, class_name in chains_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded chain classes to __all__
__all__ = [class_name for _, class_name in chains_files]
