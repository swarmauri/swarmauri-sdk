# from swarmauri.utils._lazy_import import _lazy_import

# # List of schema_converters names (file names without the ".py" extension) and corresponding class names
# schema_converters_files = [
#     (
#         "swarmauri_standard.schema_converters.AnthropicSchemaConverter",
#         "AnthropicSchemaConverter",
#     ),
#     (
#         "swarmauri_standard.schema_converters.CohereSchemaConverter",
#         "CohereSchemaConverter",
#     ),
#     (
#         "swarmauri_standard.schema_converters.GeminiSchemaConverter",
#         "GeminiSchemaConverter",
#     ),
#     ("swarmauri_standard.schema_converters.GroqSchemaConverter", "GroqSchemaConverter"),
#     (
#         "swarmauri_standard.schema_converters.MistralSchemaConverter",
#         "MistralSchemaConverter",
#     ),
#     (
#         "swarmauri_standard.schema_converters.OpenAISchemaConverter",
#         "OpenAISchemaConverter",
#     ),
#     (
#         "swarmauri_standard.schema_converters.ShuttleAISchemaConverter",
#         "ShuttleAISchemaConverter",
#     ),
# ]

# # Lazy loading of schema_converters classes, storing them in variables
# for module_name, class_name in schema_converters_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded schema_converters classes to __all__
# __all__ = [class_name for _, class_name in schema_converters_files]
