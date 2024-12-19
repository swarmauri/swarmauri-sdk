from swarmauri.utils.LazyLoader import LazyLoader

# List of data connector files names (file names without the ".py" extension) and corresponding class names
data_connector_files = [
    (
        "swarmauri.dataconnectors.concrete.GoogleDriveDataConnector",
        "GoogleDriveDataConnector",
    ),
]

# Lazy loading of data connector classes, storing them in variables
for module_name, class_name in data_connector_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded data connector classes to __all__
__all__ = [class_name for _, class_name in data_connector_files]
