import json
from typing import (
    Any,
    Dict,
    Optional,
    List,
    Literal,
    TypeVar,
    Type,
    Union,
    ClassVar,
    Set,
    get_args,
)

from uuid import uuid4
from enum import Enum
import inspect
import hashlib
from pydantic import BaseModel, Field, ValidationError, field_validator
import logging
from swarmauri_core.typing import SubclassUnion


T = TypeVar("T", bound="ComponentBase")


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
    VCM = "VCM"
    DATA_CONNECTOR = "DataConnector"
    TRANSPORT = "Transport"
    FACTORY = "Factory"
    PIPELINE = "Pipeline"
    SERVICE_REGISTRY = "ServiceRegistry"
    CONTROL_PANEL = "ControlPanel"
    TASK_MGT_STRATEGY = "TaskMgtStrategy"

def generate_id() -> str:
    return str(uuid4())

class ComponentBase(BaseModel):
    name: Optional[str] = None
    id: str = Field(default_factory=generate_id)
    members: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    host: Optional[str] = None
    resource: str = Field(default="ComponentBase")
    version: str = "0.1.0"
    __swm_subclasses__: ClassVar[Set[Type["ComponentBase"]]] = set()
    type: Literal["ComponentBase"] = "ComponentBase"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ComponentBase.__swm_register_subclass__(cls)

    @classmethod
    def __swm_register_subclass__(cls, subclass) -> None:
        logging.debug("__swm_register_subclass__ executed\n")

        if "type" in subclass.__annotations__:
            sub_type = subclass.__annotations__["type"]
            if sub_type not in [
                subclass.__annotations__["type"] for subclass in cls.__swm_subclasses__
            ]:
                cls.__swm_subclasses__.add(subclass)
        else:
            logging.warning(
                f"Subclass {subclass.__name__} does not have a type annotation"
            )

    @classmethod
    def __swm_reset_class__(cls):
        logging.debug("__swm_reset_class__ executed\n")
        for each in cls.__fields__:
            logging.debug(each, cls.__fields__[each].discriminator)
            if cls.__fields__[each].discriminator and each in cls.__annotations__:
                if len(get_args(cls.__fields__[each].annotation)) > 0:
                    for x in range(0, len(get_args(cls.__fields__[each].annotation))):
                        if hasattr(
                            get_args(cls.__fields__[each].annotation)[x], "__base__"
                        ):
                            if (
                                hasattr(
                                    get_args(cls.__fields__[each].annotation)[
                                        x
                                    ].__base__,
                                    "__swm_subclasses__",
                                )
                                and not get_args(cls.__fields__[each].annotation)[
                                    x
                                ].__base__.__name__
                                == "ComponentBase"
                            ):
                                baseclass = get_args(cls.__fields__[each].annotation)[
                                    x
                                ].__base__

                                sc = SubclassUnion[baseclass]

                                cls.__annotations__[each] = sc
                                cls.__fields__[each].annotation = sc

        cls.model_rebuild(force=True)

    @field_validator("type")
    def set_type(cls, v, values):
        if v == "ComponentBase" and cls.__name__ != "ComponentBase":
            return cls.__name__
        return v

    def __swm_class_hash__(self):
        sig_hash = hashlib.sha256()
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if callable(attr_value) and not attr_name.startswith("_"):
                sig = inspect.signature(attr_value)
                sig_hash.update(str(sig).encode())
        return sig_hash.hexdigest()

    @classmethod
    def swm_public_interfaces(cls):
        methods = []
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if (callable(attr_value) and not attr_name.startswith("_")) or isinstance(
                attr_value, property
            ):
                methods.append(attr_name)
        return methods

    @classmethod
    def swm_ismethod_registered(cls, method_name: str):
        return method_name in cls.public_interfaces()

    @classmethod
    def swm_method_signature(cls, input_signature):
        for method_name in cls.public_interfaces():
            method = getattr(cls, method_name)
            if callable(method):
                sig = str(inspect.signature(method))
                if sig == input_signature:
                    return True
        return False

    @property
    def swm_path(self):
        if self.host and self.owner:
            return f"{self.host}/{self.owner}/{self.resource}/{self.name}/{self.id}"
        if self.resource and self.name:
            return f"/{self.resource}/{self.name}/{self.id}"
        return f"/{self.resource}/{self.id}"

    @property
    def swm_isremote(self):
        return bool(self.host)

    @classmethod
    def model_validate_json(
        cls: Type[T], json_payload: Union[str, Dict[str, Any]], strict: bool = False
    ) -> T:
        # Ensure we're working with a dictionary
        if isinstance(json_payload, str):
            try:
                payload_dict = json.loads(json_payload)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON payload")
        else:
            payload_dict = json_payload

        # Try to determine the specific component type
        component_type = payload_dict.get("type", "ComponentBase")

        # Attempt to find the correct subclass
        target_cls = cls.get_subclass_by_type(component_type)

        # Fallback logic
        if target_cls is None:
            if strict:
                raise ValueError(f"Cannot resolve component type: {component_type}")
            target_cls = cls
            logging.warning(
                f"Falling back to base ComponentBase for type: {component_type}"
            )

        # Validate using the determined class
        try:
            return target_cls.model_validate(payload_dict)
        except ValidationError as e:
            logging.error(f"Validation failed for {component_type}: {e}")
            raise

    @classmethod
    def get_subclass_by_type(cls, type_name: str) -> Optional[Type["ComponentBase"]]:
        # First, check for exact match in registered subclasses
        for subclass in cls.__swm_subclasses__:
            if (
                subclass.__name__ == type_name
                or getattr(subclass, "type", None) == type_name
            ):
                return subclass

        # If no exact match, try case-insensitive search
        for subclass in cls.__swm_subclasses__:
            if (
                subclass.__name__.lower() == type_name.lower()
                or str(getattr(subclass, "type", "")).lower() == type_name.lower()
            ):
                return subclass

        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentBase":
        return cls.model_validate(data)
