import importlib

# Define a lazy loader function with a warning message if the module is not found
def _lazy_import(module_name, module_description=None):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        # If module is not available, print a warning message
        print(f"Warning: The module '{module_description or module_name}' is not available. "
              f"Please install the necessary dependencies to enable this functionality.")
        return None

# Lazy loading of embeddings with descriptive names
# Doc2VecEmbedding = _lazy_import("swarmauri.embeddings.concrete.Doc2VecEmbedding", "Doc2VecEmbedding")
GeminiEmbedding = _lazy_import("swarmauri.embeddings.concrete.GeminiEmbedding", "GeminiEmbedding")
MistralEmbedding = _lazy_import("swarmauri.embeddings.concrete.MistralEmbedding", "MistralEmbedding")
# MlmEmbedding = _lazy_import("swarmauri.embeddings.concrete.MlmEmbedding", "MlmEmbedding")
NmfEmbedding = _lazy_import("swarmauri.embeddings.concrete.NmfEmbedding", "NmfEmbedding")
OpenAIEmbedding = _lazy_import("swarmauri.embeddings.concrete.OpenAIEmbedding", "OpenAIEmbedding")
TfidfEmbedding = _lazy_import("swarmauri.embeddings.concrete.TfidfEmbedding", "TfidfEmbedding")

# Adding lazy-loaded modules to __all__
__all__ = [
    # "Doc2VecEmbedding",
    "GeminiEmbedding",
    "MistralEmbedding",
    # "MlmEmbedding",
    "NmfEmbedding",
    "OpenAIEmbedding",
    "TfidfEmbedding",
]
