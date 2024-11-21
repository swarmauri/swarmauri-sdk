from swarmauri.utils._lazy_import import _lazy_import

# List of schema_converters names (file names without the ".py" extension) and corresponding class names
schema_converters_files = [
    (
        "swarmauri.schema_converters.concrete.AnthropicSchemaConverter",
        "AnthropicSchemaConverter",
    ),
    (
        "swarmauri.schema_converters.concrete.CohereSchemaConverter",
        "CohereSchemaConverter",
    ),
    (
        "swarmauri.schema_converters.concrete.GeminiSchemaConverter",
        "GeminiSchemaConverter",
    ),
    ("swarmauri.schema_converters.concrete.GroqSchemaConverter", "GroqSchemaConverter"),
    (
        "swarmauri.schema_converters.concrete.MistralSchemaConverter",
        "MistralSchemaConverter",
    ),
    (
        "swarmauri.schema_converters.concrete.OpenAISchemaConverter",
        "OpenAISchemaConverter",
    ),
    (
        "swarmauri.schema_converters.concrete.ShuttleAISchemaConverter",
        "ShuttleAISchemaConverter",
    ),
]

# Lazy loading of schema_converters classes, storing them in variables
for module_name, class_name in schema_converters_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded schema_converters classes to __all__
__all__ = [class_name for _, class_name in schema_converters_files]
