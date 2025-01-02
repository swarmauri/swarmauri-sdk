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
from typing import Type, Dict, Any, ClassVar, List, Optional, Union, get_origin, get_args, Literal, TypeVar, Generic, Annotated

T = TypeVar("T", bound="ComponentBase")

class SubclassUnion(Generic[T], type):
    """
    A generic class to create discriminated unions based on resource types.
    """
    def __class_getitem__(cls, resource_type: Type[T]) -> type:
        """
        Allows usage of SubclassUnion[ResourceType] to get the corresponding discriminated Union.

        Parameters:
        - resource_type: The base class of the resource (e.g., Shape, Kind).

        Returns:
        - An Annotated Union of all subclasses registered under the resource_type, with 'type' as the discriminator.
        """
        registered_classes = list(ComponentBase.TYPE_REGISTRY.get(resource_type, {}).values())
        if not registered_classes:
            raise ValueError(f"No subclasses registered for resource type '{resource_type.__name__}'")
        union_type = Union[tuple(registered_classes)]
        return Annotated[union_type, Field(serialization_alias=f"SubclassUnion[{resource_type.__name__}]", discriminator='type')]

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
    TASK_MGMT_STRATEGY = "TaskMgmtStrategy"

def generate_id() -> str:
    return str(uuid4())

class ComponentBase(BaseModel):
    """
    Base class for all components.
    """
    # Class-level registry mapping resource types to their type mappings
    TYPE_REGISTRY: ClassVar[Dict[Type['ComponentBase'], Dict[str, Type['ComponentBase']]]] = {}
    # Model registry mapping models to their resource types
    MODEL_REGISTRY: ClassVar[Dict[Type[BaseModel], Type['ComponentBase']]] = {}
    _lock: ClassVar[Lock] = Lock()

    name: Optional[str] = None
    id: str = Field(default_factory=generate_id)
    members: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    host: Optional[str] = None
    resource: str = Field(default="ComponentBase")
    version: str = "0.1.0"
    type: Literal["ComponentBase"] = "ComponentBase"


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ComponentBase.__swm_register_subclass__(cls)

    @field_validator("type")
    def set_type(cls, v, values):
        if v == "ComponentBase" and cls.__name__ != "ComponentBase":
            return cls.__name__
        return v


    # Normative Class Methods
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

    # Experimental properties in support of 

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

    # Functional Class Methods

    @classmethod
    def register_type(cls, resource_type: Type[T], type_name: str):
        """
        Decorator to register a component class with a specific type name under a resource type.

        Parameters:
        - resource_type: The base class of the resource (e.g., Shape, Kind).
        - type_name: The string identifier for the component type.
        """
        def decorator(subclass: Type['ComponentBase']):
            if not issubclass(subclass, resource_type):
                raise TypeError(f"Registered class '{subclass.__name__}' must be a subclass of {resource_type.__name__}")
            if resource_type not in cls.TYPE_REGISTRY:
                cls.TYPE_REGISTRY[resource_type] = {}
            cls.TYPE_REGISTRY[resource_type][type_name] = subclass
            cls.recreate_models()
            return subclass
        return decorator

    @classmethod
    def register_model(cls, resource_type: Type[T]):
        """
        Decorator to register a Pydantic model with a resource type.

        Parameters:
        - resource_type: The base class of the resource (e.g., Shape, Kind).
        """
        def decorator(model_cls: Type[BaseModel]):
            cls.MODEL_REGISTRY[model_cls] = resource_type
            return model_cls
        return decorator

    @classmethod
    def get_class_by_type(cls, resource_type: Type[T], type_name: str) -> Type['ComponentBase']:
        """
        Retrieve a component class based on its resource type and type name.

        Parameters:
        - resource_type: The base class of the resource.
        - type_name: The string identifier for the component type.

        Returns:
        - The corresponding component class.
        """
        return cls.TYPE_REGISTRY.get(resource_type, {}).get(type_name)

    @classmethod
    def generate_models_with_fields(cls) -> Dict[Type[BaseModel], Dict[str, Any]]:
        """
        Automatically generate the models_with_fields dictionary based on registered models.

        Returns:
        - A dictionary mapping model classes to their fields and corresponding resource types.
        """
        models_with_fields = {}
        for model_cls, resource_type in cls.MODEL_REGISTRY.items():
            models_with_fields[model_cls] = {}
            for field_name, field in model_cls.__fields__.items():
                field_annotation = model_cls.__annotations__.get(field_name)
                if not field_annotation:
                    continue

                # Check if SubclassUnion is used in the field type
                origin = get_origin(field_annotation)
                args = get_args(field_annotation)

                def contains_subclass_union(tp):
                    if isinstance(tp, type(SubclassUnion)):
                        return True
                    origin_tp = get_origin(tp)
                    if origin_tp is Annotated:
                        args_tp = get_args(tp)
                        return contains_subclass_union(args_tp[0])
                    elif origin_tp in {list, List, dict, Dict, Union}:
                        return any(contains_subclass_union(arg) for arg in get_args(tp))
                    return False

                if not contains_subclass_union(field_annotation):
                    continue  # Only process fields that use SubclassUnion

                original_type = field_annotation
                origin = get_origin(original_type)
                args = get_args(original_type)

                is_optional = False

                if origin is Union and type(None) in args:
                    # Handle Optional and Union types
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if len(non_none_args) == 1:
                        original_type = non_none_args[0]
                        origin = get_origin(original_type)
                        args = get_args(original_type)
                        is_optional = True
                    else:
                        original_type = Union[tuple(non_none_args)]
                        origin = get_origin(original_type)
                        args = get_args(original_type)
                        is_optional = True

                # Handle Annotated types by extracting the underlying type
                if origin is Annotated:
                    # Extract the actual type from Annotated
                    original_type = args[0]
                    origin = get_origin(original_type)
                    args = get_args(original_type)

                if origin in {list, List}:
                    # Handle List[SubclassUnion[ResourceType]]
                    new_type = List[SubclassUnion[resource_type]]
                elif origin in {dict, Dict}:
                    # Handle Dict[key_type, SubclassUnion[ResourceType]]
                    key_type, value_type = args
                    new_type = Dict[key_type, SubclassUnion[resource_type]]
                elif origin is Union:
                    # Handle Union types
                    union_types = []
                    for arg in args:
                        if isinstance(arg, type(SubclassUnion)) and issubclass(arg, SubclassUnion):
                            union_types.append(SubclassUnion[resource_type])
                        else:
                            union_types.append(arg)
                    new_type = Union[tuple(union_types)]
                else:
                    # Handle non-generic types
                    new_type = SubclassUnion[resource_type]

                if is_optional:
                    # Include None in the Union and maintain the discriminator
                    registered_classes = list(cls.TYPE_REGISTRY.get(resource_type, {}).values())
                    union_with_none = Union[tuple(registered_classes + [type(None)])]
                    new_type = Annotated[union_with_none, Field(discriminator="type")]

                models_with_fields[model_cls][field_name] = new_type

        return models_with_fields

    @classmethod
    def recreate_models(cls):
        """
        Recreate models based on the dynamically generated models_with_fields.
        """
        with cls._lock:
            models_with_fields = cls.generate_models_with_fields()
            for model_class, fields in models_with_fields.items():
                for field_name, new_type in fields.items():
                    if field_name in model_class.model_fields:
                        model_class.model_fields[field_name].annotation = new_type
                    else:
                        raise ValueError(f"Field '{field_name}' does not exist in model '{model_class.__name__}'")
                model_class.model_rebuild(force=True)