from swarmauri.utils._lazy_import import _lazy_import

# List of data connector files names (file names without the ".py" extension) and corresponding class names
data_connector_files = [
    (
        "swarmauri_standard.dataconnectors.GoogleDriveDataConnector",
        "GoogleDriveDataConnector",
    ),
]

# Lazy loading of data connector classes, storing them in variables
for module_name, class_name in data_connector_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded data connector classes to __all__
__all__ = [class_name for _, class_name in data_connector_files]
