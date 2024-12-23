from swarmauri.utils.LazyLoader import LazyLoader

# List of mas_agent_apis names (file names without the ".py" extension) and corresponding class names
mas_agent_apis_files = [
    ("swarmauri.mas_agent_apis.concrete.MasAgentAPI", "MasAgentAPI"),
]

# Lazy loading of mas_agent_apis classes, storing them in variables
for module_name, class_name in mas_agent_apis_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded mas_agent_apis classes to __all__
__all__ = [class_name for _, class_name in mas_agent_apis_files]
