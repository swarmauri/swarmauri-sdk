from swarmauri_standard.utils._lazy_import import _lazy_import

# List of transport names (file names without the ".py" extension) and corresponding class names
transport_files = [
    ("swarmauri_standard.transports.PubSubTransport", "PubSubTransport"),
]

# Lazy loading of transport classes, storing them in variables
for module_name, class_name in transport_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded transport classes to __all__
__all__ = [class_name for _, class_name in transport_files]
