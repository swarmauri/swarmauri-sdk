# from swarmauri.utils._lazy_import import _lazy_import

# # List of message classes (file names without the ".py" extension) and corresponding class names
# message_files = [
#     ("swarmauri_standard.messages.AgentMessage", "AgentMessage"),
#     ("swarmauri_standard.messages.FunctionMessage", "FunctionMessage"),
#     ("swarmauri_standard.messages.HumanMessage", "HumanMessage"),
#     ("swarmauri_standard.messages.SystemMessage", "SystemMessage"),
# ]

# # Lazy loading of message classes, storing them in variables
# for module_name, class_name in message_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded message classes to __all__
# __all__ = [class_name for _, class_name in message_files]
