# interface_registry.py

"""
interface_registry.py

Centralized registry for mapping resource kinds to their validation interfaces.
Provides mechanisms to retrieve and manage interface classes based on resource namespaces.
"""

from typing import Optional, Type, Dict, Any, List
import importlib
import logging


# Configure logging
logger = logging.getLogger(__name__)


class InterfaceRegistry:
    """
    InterfaceRegistry

    A centralized registry for mapping resource kinds to their corresponding interface classes.
    Provides methods to retrieve and manage interface classes based on resource namespaces.
    """

    INTERFACE_IMPORT_PATHS: Dict[str, Optional[str]] = {
        "swarmauri.agents": "swarmauri_base.agents.AgentBase",
        "swarmauri.chains": "swarmauri_base.chains.ChainBase",
        "swarmauri.chunkers": "swarmauri_base.chunkers.ChunkerBase",
        "swarmauri.conversations": "swarmauri_base.conversations.ConversationBase",
        "swarmauri.dataconnectors": "swarmauri_base.dataconnectors.DataConnectorBase",
        "swarmauri.decorators": None,
        "swarmauri.distances": "swarmauri_base.distances.DistanceBase",
        "swarmauri.documents": "swarmauri_base.documents.DocumentBase",
        "swarmauri.embeddings": "swarmauri_base.embeddings.EmbeddingBase",
        "swarmauri.exceptions": None,
        "swarmauri.factories": "swarmauri_base.factories.FactoryBase",
        "swarmauri.image_gens": "swarmauri_base.image_gens.ImageGenBase",
        "swarmauri.llms": "swarmauri_base.llms.LLMBase",
        "swarmauri.tool_llms": "swarmauri_base.tool_llms.ToolLLMBase",
        "swarmauri.tts": "swarmauri_base.tts.TTSBase",
        "swarmauri.ocrs": "swarmauri_base.ocrs.OCRBase",
        "swarmauri.stt": "swarmauri_base.stt.STTBase",
        "swarmauri.vlms": "swarmauri_base.vlms.VLMBase",
        "swarmauri.measurements": "swarmauri_base.measurements.MeasurementBase",
        "swarmauri.messages": "swarmauri_base.messages.MessageBase",
        "swarmauri.middlewares": "swarmauri_base.middlewares.MiddlewareBase",
        "swarmauri.parsers": "swarmauri_base.parsers.ParserBase",
        "swarmauri.pipelines": "swarmauri_base.pipelines.PipelineBase",
        "swarmauri.prompts": "swarmauri_base.prompts.PromptBase",
        "swarmauri.prompt_templates": "swarmauri_base.prompt_templates.PromptTemplateBase",
        "swarmauri.plugins": None,
        "swarmauri.schema_converters": "swarmauri_base.schema_converters.SchemaConverterBase",
        "swarmauri.service_registries": "swarmauri_base.service_registries.ServiceRegistryBase",
        "swarmauri.state": "swarmauri_base.state.StateBase",
        "swarmauri.swarms": "swarmauri_base.swarms.SwarmBase",
        "swarmauri.task_mgmt_strategies": "swarmauri_base.task_mgmt_strategies.TaskMgmtStrategyBase",
        "swarmauri.toolkits": "swarmauri_base.toolkits.ToolkitBase",
        "swarmauri.tools": "swarmauri_base.tools.ToolBase",
        "swarmauri.tracing": None,
        "swarmauri.transports": "swarmauri_base.transports.TransportBase",
        "swarmauri.utils": None,
        "swarmauri.vector_stores": "swarmauri_base.vector_stores.VectorStoreBase",
        "swarmauri.vectors": "swarmauri_base.vectors.VectorBase",
        "swarmauri.mre_cryptos": "swarmauri_base.mre_crypto.MreCryptoBase",
        "swarmauri.crypto": "swarmauri_base.crypto.CryptoBase",
        "swarmauri.signings": "swarmauri_base.signing.SigningBase",
        "swarmauri.key_providers": "swarmauri_base.keys.KeyProviderBase",
        "swarmauri.logger_formatters": "swarmauri_base.logger_formatters.FormatterBase",
        "swarmauri.loggers": "swarmauri_base.loggers.LoggerBase",
        "swarmauri.logger_handlers": "swarmauri_base.logger_handlers.HandlerBase",
        "swarmauri.rate_limits": "swarmauri_base.rate_limits.RateLimitBase",
        "swarmauri.mre_crypto": "swarmauri_base.mre_crypto.MreCryptoBase",
        "swarmauri.tokens": "swarmauri_base.tokens.TokenServiceBase",
    }

    INTERFACE_REGISTRY: Dict[str, Optional[Type[Any]]] = {
        key: None for key in INTERFACE_IMPORT_PATHS
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
        if interface is None and cls.INTERFACE_IMPORT_PATHS.get(resource_kind):
            module_path = cls.INTERFACE_IMPORT_PATHS[resource_kind]
            if module_path is not None:
                class_name = module_path.rsplit(".", 1)[1]
                module = importlib.import_module(module_path)
                interface = getattr(module, class_name)
                cls.INTERFACE_REGISTRY[resource_kind] = interface
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
            cls.INTERFACE_IMPORT_PATHS[resource_kind] = (
                f"{interface_class.__module__}.{interface_class.__name__}"
            )
            logger.info(
                f"Registered interface '{interface_class.__name__}' for resource kind '{resource_kind}'."
            )
        else:
            cls.INTERFACE_IMPORT_PATHS[resource_kind] = None
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
