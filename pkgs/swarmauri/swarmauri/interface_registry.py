"""
interface_registry.py
Centralized registry for mapping resource kinds to their validation interfaces.
"""

# Example imports for interface definitions
from swarmauri_base.agents.AgentBase import AgentBase
#from swarmauri_base.chains.ChainBase import ChainBase
from swarmauri_base.chunkers.ChunkerBase import ChunkerBase
#from swarmauri_base.conversations.ConversationBase import ConversationBase
#from swarmauri_base.llms.LLMBase import LLMBase

# Define the mapping
INTERFACE_REGISTRY = {
    "swarmauri.agents": AgentBase,
    #"swarmauri.chains": ChainBase,
    "swarmauri.chunkers": ChunkerBase,
    #"swarmauri.conversations": ConversationBase,
    #"swarmauri.llms": LLMBase,
    "swarmauri.utils": None
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
