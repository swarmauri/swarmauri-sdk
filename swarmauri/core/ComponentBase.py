from typing import Optional, List, Literal, TypeVar, Type, Union, Annotated, Generic, ClassVar
from uuid import uuid4
from enum import Enum
import inspect
import hashlib
from pydantic import BaseModel, Field, field_validator

class ResourceTypes(Enum):
    UNIVERSAL_BASE = 'ComponentBase'
    AGENT = 'Agent'
    AGENT_FACTORY = 'AgentFactory'
    CHAIN = 'Chain'
    CHAIN_METHOD = 'ChainMethod'
    CHUNKER = 'Chunker'
    CONVERSATION = 'Conversation'
    DISTANCE = 'Distance'
    DOCUMENT_STORE = 'DocumentStore'
    DOCUMENT = 'Document'
    EMBEDDING = 'Embedding'
    EXCEPTION = 'Exception'
    LLM = 'LLM'
    MESSAGE = 'Message'
    METRIC = 'Metric'
    PARSER = 'Parser'
    PROMPT = 'Prompt'
    STATE = 'State'
    CHAINSTEP = 'ChainStep'
    SWARM = 'Swarm'
    TOOLKIT = 'Toolkit'
    TOOL = 'Tool'
    PARAMETER = 'Parameter'
    TRACE = 'Trace'
    UTIL = 'Util'
    VECTOR_STORE = 'VectorStore'
    VECTOR = 'Vector'

def generate_id() -> str:
    return str(uuid4())

ComponentType = TypeVar('ComponentType', bound='ComponentBase')

class ComponentBase(BaseModel):
    name: Optional[str] = None
    id: str = Field(default_factory=generate_id)
    members: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    host: Optional[str] = None
    resource: str = Field(default="ComponentBase")
    version: str = "0.1.0"
    type: Literal['ComponentBase'] = 'ComponentBase'
    
    @field_validator('type')
    def set_type(cls, v, values):
        if v == 'ComponentBase' and cls.__name__ != 'ComponentBase':
            return cls.__name__
        return v

    @classmethod
    def get_subclasses(cls) -> set:
        def is_excluded_module(module_name: str) -> bool:
            return (module_name == 'builtins' or 
                    module_name == 'types')

        subclasses_dict = {cls.__name__: cls}
        for subclass in cls.__subclasses__():
            if not is_excluded_module(subclass.__module__):
                subclasses_dict.update({_s.__name__: _s for _s in subclass.get_subclasses() 
                    if not is_excluded_module(_s.__module__)})

        return set(subclasses_dict.values())

    def _calculate_class_hash(self):
        sig_hash = hashlib.sha256()
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if callable(attr_value) and not attr_name.startswith("_"):
                sig = inspect.signature(attr_value)
                sig_hash.update(str(sig).encode())
        return sig_hash.hexdigest()

    @classmethod
    def public_interfaces(cls):
        methods = []
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if (callable(attr_value) and not attr_name.startswith("_")) or isinstance(attr_value, property):
                methods.append(attr_name)
        return methods

    @classmethod
    def is_method_registered(cls, method_name: str):
        return method_name in cls.public_interfaces()

    @classmethod
    def method_with_signature(cls, input_signature):
        for method_name in cls.public_interfaces():
            method = getattr(cls, method_name)
            if callable(method):
                sig = str(inspect.signature(method))
                if sig == input_signature:
                    return True
        return False

    @property
    def path(self):
        if self.host and self.owner:
            return f"{self.host}/{self.owner}/{self.resource}/{self.name}/{self.id}"
        if self.resource and self.name:
            return f"/{self.resource}/{self.name}/{self.id}"
        return f"/{self.resource}/{self.id}"

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def class_hash(self):
        return self._calculate_class_hash()

    @property
    def is_remote(self):
        return bool(self.host)