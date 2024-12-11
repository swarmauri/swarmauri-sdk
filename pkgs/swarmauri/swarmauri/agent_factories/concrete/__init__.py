from swarmauri.utils._lazy_import import _lazy_import

# List of agent factory names (file names without the ".py" extension) and corresponding class names
agent_factory_files = [
    ("swarmauri.agent_factories.concrete.agent_factory", "AgentFactory"),
    (
        "swarmauri.agent_factories.concrete.conf_driven_agent_factory",
        "ConfDrivenAgentFactory",
    ),
    ("swarmauri.agent_factories.concrete.JsonAgentFactory", "JsonAgentFactory"),
    (
        "swarmauri.agent_factories.concrete.ReflectionAgentFactory",
        "ReflectionAgentFactory",
    ),
]

# Lazy loading of agent factories storing them in variables
for module_name, class_name in agent_factory_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded agent factories to __all__
__all__ = [class_name for _, class_name in agent_factory_files]
