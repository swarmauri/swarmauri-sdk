# from swarmauri_standard.utils._lazy_import import _lazy_import

# # List of pipeline names (file names without the ".py" extension) and corresponding class names
# pipeline_files = [
#     ("swarmauri_standard.pipelines.Pipeline", "Pipeline"),
# ]

# # Lazy loading of pipeline classes, storing them in variables
# for module_name, class_name in pipeline_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded pipeline classes to __all__
# __all__ = [class_name for _, class_name in pipeline_files]