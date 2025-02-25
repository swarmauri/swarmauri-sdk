# swarmauri_base/ComponentBase.py


from enum import Enum
from typing import (
    Annotated,
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, ConfigDict

###########################################
# Logging
###########################################
from swarmauri_base.glogging import glogger


###########################################
# Typing
###########################################

T = TypeVar("T", bound="ComponentBase")


###########################################
# Resource Kinds
###########################################
class ResourceTypes(Enum):
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
    FACTORY = "Factory"
    PIPELINE = "Pipeline"
    SERVICE_REGISTRY = "ServiceRegistry"
    CONTROL_PANEL = "ControlPanel"
    TASK_MGMT_STRATEGY = "TaskMgmtStrategy"
    TOOL_LLM = "ToolLLM"
    TTS = "TTS"
    STT = "STT"
    OCR = "OCR"


###########################################
# ComponentBase
###########################################

def generate_id() -> str:
    return str(uuid4())

from swarmauri_base.YamlMixin import YamlMixin
from swarmauri_base.LoggerMixin import LoggerMixin
from swarmauri_base.DynamicBase import DynamicBase

@DynamicBase.register_type()
class ComponentBase(
        LoggerMixin, 
        YamlMixin, 
        DynamicBase, 
        BaseModel
    ):
    """
    Base class for all components.
    """
    _type: ClassVar[str] = "ComponentBase"

    # Instance-attribute type (to support deserialization)
    type: Literal["ComponentBase"] = "ComponentBase"
    name: Optional[str] = None
    id: str = Field(default_factory=generate_id)
    members: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    host: Optional[str] = None
    resource: str = Field(default="ComponentBase")
    version: str = "0.1.0"

    model_config = ConfigDict(arbitrary_types_allowed=True)

###########################################
# Subclass Union
###########################################
from swarmauri_base.DynamicBase import SubclassUnion as SubclassUnion

