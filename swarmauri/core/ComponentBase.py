from typing import Optional, List, Literal, TypeVar, Type
from uuid import uuid4
from enum import Enum
import inspect
import hashlib
from pydantic import BaseModel, ValidationError, Field, field_validator, PrivateAttr

class ResourceTypes(Enum):
    UNIVERSAL_BASE = 'ComponentBase'
    #AGENT_API = 'AgentAPI'
    AGENT = 'Agent'
    AGENT_FACTORY = 'AgentFactory'
    CHAIN = 'Chain'
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
    #SWARM_API = 'SwarmAPI'
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
    resource: str = Field(default="BaseComponent")
    version: str = "0.1.0"
    type: Literal['ComponentBase'] = 'ComponentBase'

    @classmethod
    def __init_subclass__(cls: Type[ComponentType], **kwargs):
        super().__init_subclass__(**kwargs)
        cls.type = cls.__name__

    @classmethod
    def get_subclasses(cls) -> set:
        subclasses_dict = {cls.__name__: cls}
        for subclass in cls.__subclasses__():
            if subclass.__module__ == '__main__':
                subclasses_dict.update({subclass.__name__: subclass for subclass in subclass.get_subclasses() 
                    if subclass.__module__ == '__main__'})
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
        self._calculate_class_hash()
    
    @property
    def is_remote(self):
        return bool(self._host)
    

    @classmethod
    def public_interfaces(cls):
        methods = []
        for attr_name in dir(cls):
            # Retrieve the attribute
            attr_value = getattr(cls, attr_name)
            # Check if it's callable or a property and not a private method
            if (callable(attr_value) and not attr_name.startswith("_")) or isinstance(attr_value, property):
                methods.append(attr_name)
        return methods

    @classmethod
    def is_method_registered(cls, method_name: str):
        """
        Checks if a public method with the given name is registered on the class.
        Args:
            method_name (str): The name of the method to check.
        Returns:
            bool: True if the method is registered, False otherwise.
        """
        return method_name in cls.public_interfaces()

    @classmethod
    def method_with_signature(cls, input_signature):
        """
        Checks if there is a method with the given signature available in the class.
        
        Args:
            input_signature (str): The string representation of the method signature to check.
        
        Returns:
            bool: True if a method with the input signature exists, False otherwise.
        """
        for method_name in cls.public_interfaces():
            method = getattr(cls, method_name)
            if callable(method):
                sig = str(inspect.signature(method))
                if sig == input_signature:
                    return True
        return False

    @classmethod
    def _calculate_class_hash(cls):
        sig_hash = hashlib.sha256()
        for attr_name in dir(cls):
            if attr_name in ['classh_hash']:
                continue
            # Retrieve the attribute
            attr_value = getattr(cls, attr_name)
            if callable(attr_value) and not attr_name.startswith("_"):
                sig = inspect.signature(attr_value)
                sig_hash.update(str(sig).encode())
                print(sig_hash.hexdigest())
        return sig_hash.hexdigest()

