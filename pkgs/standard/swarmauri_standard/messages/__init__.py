from swarmauri.utils._lazy_import import _lazy_import

# List of messages names (file names without the ".py" extension) and corresponding class names
messages_files = [
    ("swarmauri.messages.concrete.HumanMessage", "HumanMessage"),
    ("swarmauri.messages.concrete.AgentMessage", "AgentMessage"),
    ("from swarmauri.messages.concrete.FunctionMessage", "FunctionMessage"),
    ("swarmauri.messages.concrete.SystemMessage", "SystemMessage"),
]

# Lazy loading of messages classes, storing them in variables
for module_name, class_name in messages_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded messages classes to __all__
__all__ = [class_name for _, class_name in messages_files]
