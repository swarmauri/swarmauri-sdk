# from swarmauri.utils._lazy_import import _lazy_import

# # List of agent names (file names without the ".py" extension) and corresponding class names
# agent_files = [
#     ("swarmauri_standard.agents.QAAgent", "QAAgent"),
#     ("swarmauri_standard.agents.RagAgent", "RagAgent"),
#     ("swarmauri_standard.agents.SimpleConversationAgent", "SimpleConversationAgent"),
#     ("swarmauri_standard.agents.ToolAgent", "ToolAgent"),
# ]

# # Lazy loading of agent classes, storing them in variables
# for module_name, class_name in agent_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded agent classes to __all__
# __all__ = [class_name for _, class_name in agent_files]
