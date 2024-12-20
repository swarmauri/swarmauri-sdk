from swarmauri.utils.LazyLoader import LazyLoader

# List of agent names (file names without the ".py" extension) and corresponding class names
agent_files = [
    ("swarmauri.agents.concrete.QAAgent", "QAAgent"),
    ("swarmauri.agents.concrete.RagAgent", "RagAgent"),
    ("swarmauri.agents.concrete.SimpleConversationAgent", "SimpleConversationAgent"),
    ("swarmauri.agents.concrete.ToolAgent", "ToolAgent"),
]

# Lazy loading of agent classes, storing them in variables
for module_name, class_name in agent_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded agent classes to __all__
__all__ = [class_name for _, class_name in agent_files]
