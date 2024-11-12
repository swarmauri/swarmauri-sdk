import importlib

# Define a lazy loader function with a warning message if the module or class is not found
def _lazy_import(module_name, class_name):
    try:
        # Import the module
        module = importlib.import_module(module_name)
        # Dynamically get the class from the module
        return getattr(module, class_name)
    except ImportError:
        # If module is not available, print a warning message
        print(f"Warning: The module '{module_name}' is not available. "
              f"Please install the necessary dependencies to enable this functionality.")
        return None
    except AttributeError:
        # If class is not found, print a warning message
        print(f"Warning: The class '{class_name}' was not found in module '{module_name}'.")
        return None

# List of agent names (file names without the ".py" extension) and corresponding class names
agent_files = [
    ("swarmauri.agents.concrete.SimpleConversationAgent", "SimpleConversationAgent"),
    ("swarmauri.agents.concrete.QAAgent", "QAAgent"),
    ("swarmauri.agents.concrete.RagAgent", "RagAgent"),
    ("swarmauri.agents.concrete.ToolAgent", "ToolAgent"),
]

# Lazy loading of agent classes, storing them in variables
for module_name, class_name in agent_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded agent classes to __all__
__all__ = [class_name for _, class_name in agent_files]
