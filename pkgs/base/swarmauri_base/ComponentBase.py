# swarmauri_base/ComponentBase.py
"""Core base component and resource type definitions."""

from enum import Enum
from typing import (
    ClassVar,
    Literal,
    Optional,
    TypeVar,
)

from pydantic import ConfigDict, Field

from swarmauri_base.DynamicBase import DynamicBase

###########################################
# Export Subclass Union for Legacy Support
###########################################
from swarmauri_base.DynamicBase import SubclassUnion as SubclassUnion
from swarmauri_base.LoggerMixin import LoggerMixin
from swarmauri_base.ServiceMixin import ServiceMixin
from swarmauri_base.YamlMixin import YamlMixin
from swarmauri_base.TomlMixin import TomlMixin

###########################################
# ComponentBase
###########################################

T = TypeVar("T", bound="ComponentBase")


@DynamicBase.register_type()
class ComponentBase(LoggerMixin, YamlMixin, TomlMixin, ServiceMixin, DynamicBase):
    """
    Base class for all components.
    """

    _type: ClassVar[str] = "ComponentBase"

    # Instance-attribute type (to support deserialization)
    type: Literal["ComponentBase"] = "ComponentBase"
    name: Optional[str] = None
    resource: str = Field(default="ComponentBase")
    version: str = "0.1.0"

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


###########################################
# Resource Types Enum (This should become ResourceKinds)
###########################################
class ResourceTypes(Enum):
    """Enumeration of built-in resource type names."""

    UNIVERSAL_BASE = "ComponentBase"
    AGENT = "Agent"
    AGENT_FACTORY = "AgentFactory"
    CHAIN = "Chain"
    CHAIN_METHOD = "ChainMethod"
    CHUNKER = "Chunker"
    CONVERSATION = "Conversation"
    DISTANCE = "Distance"
    DOCUMENT_STORE = "DocumentStore"
    DOCUMENT = "Document"
    EMBEDDING = "Embedding"
    EXCEPTION = "Exception"
    IMAGE_GEN = "ImageGen"
    LLM = "LLM"
    MESSAGE = "Message"
    MEASUREMENT = "Measurement"
    PARSER = "Parser"
    PROMPT = "Prompt"
    STATE = "State"
    CHAINSTEP = "ChainStep"
    SCHEMA_CONVERTER = "SchemaConverter"
    SWARM = "Swarm"
    TOOLKIT = "Toolkit"
    TOOL = "Tool"
    PARAMETER = "Parameter"
    TRACE = "Trace"
    UTIL = "Util"
    VECTOR_STORE = "VectorStore"
    VECTOR = "Vector"
    VLM = "VLM"
    DATA_CONNECTOR = "DataConnector"
    TRANSPORT = "Transport"
    PUBLISHER = "Publisher"
    FACTORY = "Factory"
    PIPELINE = "Pipeline"
    SERVICE_REGISTRY = "ServiceRegistry"
    CONTROL_PANEL = "ControlPanel"
    TASK_MGMT_STRATEGY = "TaskMgmtStrategy"
    TOOL_LLM = "ToolLLM"
    TTS = "TTS"
    STT = "STT"
    OCR = "OCR"
    PROGRAM = "Program"
    EVALUATOR = "Evaluator"
    EVALUATOR_RESULT = "EvaluatorResult"
    EVALUATOR_POOL = "EvaluatorPool"
    RATE_LIMIT = "RateLimit"
    INNER_PRODUCT = "InnerProduct"
    METRIC = "Metric"
    NORM = "Norm"
    SIMILARITY = "Similarity"
    PSEUDOMETRIC = "PseudoMetric"
    SEMINORM = "SemiNorm"
    ENSEMBLE = "Ensemble"
    MIDDLEWARE = "Middleware"
    SECRET_DRIVE = "SecretDrive"
    CRYPTO = "Crypto"
    AGENT_API = "AgentAPI"
    SWARM_API = "SwarmAPI"
    CERT_SERVICE = "CertService"
    KEY_PROVIDER = "KeyProvider"
    LOGGER = "Logger"
    LOGGER_HANDLER = "LoggerHandler"
    LOGGER_FORMATTER = "LoggerFormatter"
    MATRIX = "Matrix"
    MRE_CRYPTO = "MreCrypto"
    PROMPT_TEMPLATE = "PromptTemplate"
    SIGNING = "Signing"
    CIPHER_SUITE = "CipherSuite"
    TRACER = "Tracer"
    TENSOR = "Tensor"
    TOKEN_SERVICE = "TokenService"
    STORAGE_ADAPTER = "StorageAdapter"
    SST = "SST"
