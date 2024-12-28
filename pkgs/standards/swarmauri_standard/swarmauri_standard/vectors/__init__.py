# from swarmauri.utils._lazy_import import _lazy_import

# # List of vectors names (file names without the ".py" extension) and corresponding class names
# vectors_files = [
#     ("swarmauri_standard.vectors.Vector", "Vector"),
# ]

# # Lazy loading of vectorss, storing them in variables
# for module_name, class_name in vectors_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded vectorss to __all__
# __all__ = [class_name for _, class_name in vectors_files]
