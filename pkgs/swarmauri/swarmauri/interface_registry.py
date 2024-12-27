"""
interface_registry.py
Centralized registry for mapping resource kinds to their validation interfaces.
"""

# Example imports for interface definitions
from swarmauri_core.interfaces import IConversation, ILLM  # Update paths as per actual project structure

# Define the mapping
INTERFACE_REGISTRY = {
    "swarmauri.conversations": IConversation,
    "swarmauri.llms": ILLM,
    # Add additional mappings as needed
}

def get_interface_for_resource(resource_kind):
    """
    Retrieve the interface class for a given resource kind.
    
    :param resource_kind: The namespace or resource kind (e.g., "swarmauri.conversations").
    :return: The corresponding interface class.
    :raises KeyError: If the resource kind is not registered.
    """
    if resource_kind not in INTERFACE_REGISTRY:
        raise KeyError(f"No interface registered for resource kind: {resource_kind}")
    return INTERFACE_REGISTRY[resource_kind]
