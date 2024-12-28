# from swarmauri.utils._lazy_import import _lazy_import

# # List of service_registry name (file names without the ".py" extension) and corresponding class names
# service_registry_files = [
#     (
#         "swarmauri_standard.service_registries.ServiceRegistry",
#         "ServiceRegistry",
#     ),
# ]

# # Lazy loading of service_registry classes, storing them in variables
# for module_name, class_name in service_registry_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded service_registry classes to __all__
# __all__ = [class_name for _, class_name in service_registry_files]
