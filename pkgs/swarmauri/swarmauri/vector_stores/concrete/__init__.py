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

# List of vector store names (file names without the ".py" extension)
vector_store_files = [
    # "Doc2VecVectorStore",
    # "MlmVectorStore",
    "SqliteVectorStore",
    "TfidfVectorStore",
]

# Lazy loading of vector stores, storing them in variables
for vector_store in vector_store_files:
    globals()[vector_store] = _lazy_import(f"swarmauri.vector_stores.concrete.{vector_store}", vector_store)

# Adding the lazy-loaded vector stores to __all__
__all__ = vector_store_files
