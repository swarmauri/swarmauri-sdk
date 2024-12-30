"""
interface_registry.py
Centralized registry for mapping resource kinds to their validation interfaces.
"""

# Example imports for interface definitions
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.chains.ChainBase import ChainBase
from swarmauri_base.chunkers.ChunkerBase import ChunkerBase
from swarmauri_base.control_panels.ControlPanelBase import ControlPanelBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.dataconnectors.DataConnectorBase import DataConnectorBase
from swarmauri_base.distances.DistanceBase import DistanceBase
from swarmauri_base.documents.DocumentBase import DocumentBase
from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase
from swarmauri_base.factories.FactoryBase import FactoryBase
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.measurements.MeasurementBase import MeasurementBase
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_base.pipelines.PipelineBase import PipelineBase
from swarmauri_base.prompts.PromptBase import PromptBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.service_registries.ServiceRegistryBase import ServiceRegistryBase
from swarmauri_base.state.StateBase import StateBase
from swarmauri_base.swarms.SwarmBase import SwarmBase
from swarmauri_base.task_mgmt_strategies.TaskMgmtStrategyBase import TaskMgmtStrategyBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase
from swarmauri_base.vectors.VectorBase import VectorBase

# Define the mapping
INTERFACE_REGISTRY = {
    "swarmauri.agents": AgentBase,
    "swarmauri.chains": ChainBase,
    "swarmauri.chunkers": ChunkerBase,
    "swarmauri.control_panels": ControlPanelBase,
    "swarmauri.conversations": ConversationBase,
    "swarmauri.dataconnectors": DataConnectorBase,
    "swarmauri.distances": DistanceBase,
    "swarmauri.documents": DocumentBase,
    "swarmauri.embeddings": EmbeddingBase,
    "swarmauri.exceptions": None,
    "swarmauri.factories": FactoryBase,
    "swarmauri.image_gens": ImageGenBase,
    "swarmauri.llms": LLMBase,
    "swarmauri.measurements": MeasurementBase,
    "swarmauri.messages": MessageBase,
    "swarmauri.parsers": ParserBase,
    "swarmauri.pipelines": PipelineBase,
    "swarmauri.prompts": PromptBase,
    "swarmauri.plugins": None,
    "swarmauri.schema_converters": SchemaConverterBase,
    "swarmauri.service_registries": ServiceRegistryBase,
    "swarmauri.state": StateBase,
    "swarmauri.swarms": SwarmBase,
    "swarmauri.task_mgmt_strategies": TaskMgmtStrategyBase,
    "swarmauri.toolkits": ToolkitBase,
    "swarmauri.tools": ToolBase,
    "swarmauri.tracing": None,
    "swarmauri.transports": TransportBase,
    "swarmauri.utils": None,
    "swarmauri.vector_stores": VectorStoreBase,
    "swarmauri.vectors": VectorBase,
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
