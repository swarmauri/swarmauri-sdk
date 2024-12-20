from swarmauri.utils.LazyLoader import LazyLoader

chains_files = [
    ("swarmauri.chains.concrete.CallableChain import", "CallableChain"),
    ("swarmauri.chains.concrete.ChainStep", "ChainStep"),
    ("swarmauri.chains.concrete.PromptContextChain", "PromptContextChain"),
    ("swarmauri.chains.concrete.ContextChain", "ContextChain"),
]

# Lazy loading of chain classes, storing them in variables
for module_name, class_name in chains_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded chain classes to __all__
__all__ = [class_name for _, class_name in chains_files]
