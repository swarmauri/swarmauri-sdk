from typing import (
    Optional,
    List,
    Literal,
    TypeVar,
    Type,
    Union,
    Annotated,
    Generic,
    ClassVar,
    Set,
    get_args,
)

from uuid import uuid4
from enum import Enum
import inspect
import hashlib
from pydantic import BaseModel, Field, field_validator
import logging
from swarmauri_core.typing import SubclassUnion


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

        # [subclass.__swm_reset_class__()  for subclass in cls.__swm_subclasses__
        #  if hasattr(subclass, '__swm_reset_class__')]

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

        # This is not necessary as the model_rebuild address forward_refs
        # https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_post_init
        # cls.update_forward_refs()
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
