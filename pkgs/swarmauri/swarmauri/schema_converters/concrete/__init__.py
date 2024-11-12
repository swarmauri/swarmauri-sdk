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

# List of schema converter names (file names without the ".py" extension)
schema_converter_files = [
    "AnthropicSchemaConverter",
    "CohereSchemaConverter",
    "GeminiSchemaConverter",
    "GroqSchemaConverter",
    "MistralSchemaConverter",
    "OpenAISchemaConverter",
    "ShuttleAISchemaConverter",
]

# Lazy loading of schema converters, storing them in variables
for schema_converter in schema_converter_files:
    globals()[schema_converter] = _lazy_import(f"swarmauri.schema_converters.concrete.{schema_converter}", schema_converter)

# Adding the lazy-loaded schema converters to __all__
__all__ = schema_converter_files
