import importlib

# Define a lazy loader function with a warning message if the module is not found
def _lazy_import(module_name, module_description=None):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        # If module is not available, print a warning message
        print(f"Warning: The module '{module_description or module_name}' is not available. "
              f"Please install the necessary dependencies to enable this functionality.")
        return None

# List of agent names (file names without the ".py" extension)
agent_files = [
    "SimpleConversationAgent",
    "QAAgent",
    "RagAgent",
    "ToolAgent",
]

# Lazy loading of agent modules, storing them in variables
for agent in agent_files:
    globals()[agent] = _lazy_import(f"swarmauri.agents.concrete.{agent}", agent)

# Adding the lazy-loaded agent modules to __all__
__all__ = agent_files
