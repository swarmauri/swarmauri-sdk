# interface_registry.py

"""
interface_registry.py

Centralized registry for mapping resource kinds to their validation interfaces.
Provides mechanisms to retrieve and manage interface classes based on resource namespaces.
"""

from typing import Optional, Type, Dict, Any, List
import logging

# Example imports for interface definitions
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.chains.ChainBase import ChainBase
from swarmauri_base.chunkers.ChunkerBase import ChunkerBase
from swarmauri_base.control_panels.ControlPanelBase import ControlPanelBase
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.dataconnectors.DataConnectorBase import DataConnectorBase
from swarmauri_base.crypto.CryptoBase import CryptoBase
from swarmauri_base.mre_crypto.MreCryptoBase import MreCryptoBase
from swarmauri_base.secrets.SecretDriveBase import SecretDriveBase
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_base.distances.DistanceBase import DistanceBase
from swarmauri_base.documents.DocumentBase import DocumentBase
from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase
from swarmauri_base.factories.FactoryBase import FactoryBase
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_base.tts.TTSBase import TTSBase
from swarmauri_base.ocrs.OCRBase import OCRBase
from swarmauri_base.stt.STTBase import STTBase
from swarmauri_base.vlms.VLMBase import VLMBase
from swarmauri_base.measurements.MeasurementBase import MeasurementBase
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_base.pipelines.PipelineBase import PipelineBase
from swarmauri_base.prompts.PromptBase import PromptBase
from swarmauri_base.prompt_templates.PromptTemplateBase import PromptTemplateBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.service_registries.ServiceRegistryBase import ServiceRegistryBase
from swarmauri_base.state.StateBase import StateBase
from swarmauri_base.swarms.SwarmBase import SwarmBase
from swarmauri_base.task_mgmt_strategies.TaskMgmtStrategyBase import (
    TaskMgmtStrategyBase,
)
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.transports.TransportBase import TransportBase
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase
from swarmauri_base.vectors.VectorBase import VectorBase
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.loggers.LoggerBase import LoggerBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.rate_limits.RateLimitBase import RateLimitBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

try:
    from swarmauri_base.signing.SigningBase import SigningBase
except Exception:  # pragma: no cover

    class SigningBase:  # type: ignore[too-many-ancestors]
        pass


# Configure logging
logger = logging.getLogger(__name__)


class InterfaceRegistry:
    """
    InterfaceRegistry

    A centralized registry for mapping resource kinds to their corresponding interface classes.
    Provides methods to retrieve and manage interface classes based on resource namespaces.
    """

    # Define the mapping as a class variable
    INTERFACE_REGISTRY: Dict[str, Optional[Type[Any]]] = {
        "swarmauri.agents": AgentBase,
        "swarmauri.chains": ChainBase,
        "swarmauri.chunkers": ChunkerBase,
        "swarmauri.control_panels": ControlPanelBase,
        "swarmauri.conversations": ConversationBase,
        "swarmauri.dataconnectors": DataConnectorBase,
        "swarmauri.decorators": None,
        "swarmauri.distances": DistanceBase,
        "swarmauri.documents": DocumentBase,
        "swarmauri.embeddings": EmbeddingBase,
        "swarmauri.exceptions": None,
        "swarmauri.factories": FactoryBase,
        "swarmauri.image_gens": ImageGenBase,
        "swarmauri.llms": LLMBase,
        "swarmauri.tool_llms": ToolLLMBase,
        "swarmauri.tts": TTSBase,
        "swarmauri.ocrs": OCRBase,
        "swarmauri.stt": STTBase,
        "swarmauri.vlms": VLMBase,
        "swarmauri.measurements": MeasurementBase,
        "swarmauri.messages": MessageBase,
        "swarmauri.middlewares": MiddlewareBase,
        "swarmauri.parsers": ParserBase,
        "swarmauri.pipelines": PipelineBase,
        "swarmauri.prompts": PromptBase,
        "swarmauri.prompt_templates": PromptTemplateBase,
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
        "swarmauri.crypto": CryptoBase,
        "swarmauri.mre_cryptos": MreCryptoBase,
        "swarmauri.secrets": SecretDriveBase,
        "swarmauri.signings": SigningBase,
        "swarmauri.signings.EcdsaEnvelopeSigner": SigningBase,
        "swarmauri.signings.RSAEnvelopeSigner": SigningBase,
        "swarmauri.logger_formatters": FormatterBase,
        "swarmauri.loggers": LoggerBase,
        "swarmauri.logger_handlers": HandlerBase,
        "swarmauri.rate_limits": RateLimitBase,
        "swarmauri.mre_crypto": MreCryptoBase,
    }

    @classmethod
    def get_interface_for_resource(cls, resource_kind: str) -> Optional[Type[Any]]:
        """
        Retrieve the interface class for a given resource kind.

        :param resource_kind: The namespace or resource kind (e.g., "swarmauri.conversations").
        :return: The corresponding interface class if registered; otherwise, None.
        :raises KeyError: If the resource kind is not registered.
        """
        if resource_kind not in cls.INTERFACE_REGISTRY:
            logger.error(f"No interface registered for resource kind: {resource_kind}")
            raise KeyError(
                f"No interface registered for resource kind: {resource_kind}"
            )

        interface = cls.INTERFACE_REGISTRY[resource_kind]
        if interface is None:
            logger.warning(
                f"Resource kind '{resource_kind}' has no associated interface."
            )
        else:
            logger.debug(
                f"Retrieved interface '{interface.__name__}' for resource kind '{resource_kind}'."
            )

        return interface

    @classmethod
    def register_interface(
        cls, resource_kind: str, interface_class: Optional[Type[Any]]
    ) -> None:
        """
        Register or update the interface class for a given resource kind.

        :param resource_kind: The namespace or resource kind (e.g., "swarmauri.conversations").
        :param interface_class: The interface class to associate with the resource kind.
                                If None, removes the existing association.
        """
        if not isinstance(resource_kind, str):
            logger.error("Resource kind must be a string.")
            raise ValueError("Resource kind must be a string.")

        cls.INTERFACE_REGISTRY[resource_kind] = interface_class
        if interface_class:
            logger.info(
                f"Registered interface '{interface_class.__name__}' for resource kind '{resource_kind}'."
            )
        else:
            logger.info(
                f"Removed interface association for resource kind '{resource_kind}'."
            )

    @classmethod
    def unregister_interface(cls, resource_kind: str) -> None:
        """
        Unregister the interface class for a given resource kind.

        :param resource_kind: The namespace or resource kind to unregister.
        """
        cls.register_interface(resource_kind, None)

    @classmethod
    def list_registered_interfaces(cls) -> Dict[str, Optional[Type[Any]]]:
        """
        List all registered resource kinds and their corresponding interfaces.

        :return: A dictionary mapping resource kinds to their interface classes.
        """
        return cls.INTERFACE_REGISTRY.copy()

    @classmethod
    def list_registered_namespaces(cls) -> List[str]:
        """
        Lists all registered interface namespaces.

        :return: A list of registered namespace strings.
        """
        namespaces = list(cls.INTERFACE_REGISTRY.keys()).copy()
        logger.debug(f"Registered namespaces retrieved: {namespaces}")
        return namespaces
