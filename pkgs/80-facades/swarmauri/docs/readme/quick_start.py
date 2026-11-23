import swarmauri

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

namespaces = InterfaceRegistry.list_registered_namespaces()
registered = PluginCitizenshipRegistry.total_registry()

print("known namespaces", len(namespaces))
print("known component mappings", len(registered))
