# swarmauri_core/ComponentBase.py

import hashlib
import inspect
import json
import logging
from enum import Enum
from threading import Lock
from uuid import uuid4
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import (
    Annotated,
    Any,
    ClassVar,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

logger = logging.getLogger(__name__)
T = TypeVar("T", bound="ComponentBase")

class SubclassUnion(type):
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
            logger.debug(f"No subclasses registered for resource type '{resource_type.__name__}'. Using 'Any' as a placeholder.")
            return Annotated[Any, Field(...)]
        else:
            union_type = Union[tuple(registered_classes)]
        return Annotated[union_type, Field(discriminator='type')]

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
    MODEL_REGISTRY: ClassVar[Dict[Type[BaseModel], List[Type['ComponentBase']]]] = {}
    _lock: ClassVar[Lock] = Lock()

    name: Optional[str] = None
    id: str = Field(default_factory=generate_id)
    members: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    host: Optional[str] = None
    resource: str = Field(default="ComponentBase")
    version: str = "0.1.0"
    type: Literal["ComponentBase"] = "ComponentBase"

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
        return method_name in cls.swm_public_interfaces()

    @classmethod
    def swm_method_signature(cls, input_signature):
        for method_name in cls.swm_public_interfaces():
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

    # Functional Class Methods

    @classmethod
    def register_type(cls, resource_type: Type[T], type_name: str):
        """
        Decorator to register a component class with a specific type name under a resource type.
        """
        def decorator(subclass: Type['ComponentBase']):
            if not issubclass(subclass, resource_type):
                raise TypeError(f"Registered class '{subclass.__name__}' must be a subclass of {resource_type.__name__}")
            if resource_type not in cls.TYPE_REGISTRY:
                cls.TYPE_REGISTRY[resource_type] = {}
            cls.TYPE_REGISTRY[resource_type][type_name] = subclass
            # Automatically recreate models after registering a new type
            cls.recreate_models()
            logger.info(f"Registered type '{type_name}' for resource '{resource_type.__name__}' with subclass '{subclass.__name__}'")
            return subclass
        return decorator

    @classmethod
    def register_model(cls):
        """
        Decorator to register a Pydantic model by automatically detecting resource types
        from fields that use SubclassUnion.
        """
        def decorator(model_cls: Type[BaseModel]):
            # Initialize list if not present
            if model_cls not in cls.MODEL_REGISTRY:
                cls.MODEL_REGISTRY[model_cls] = []

            # Inspect all fields to find SubclassUnion annotations
            for field_name, field in model_cls.__fields__.items():
                field_annotation = model_cls.__annotations__.get(field_name)
                if not field_annotation:
                    continue

                # Check if field uses SubclassUnion
                if cls.field_contains_subclass_union(field_annotation):
                    # Extract resource types from SubclassUnion
                    resource_types = cls.extract_resource_types_from_field(field_annotation)
                    for resource_type in resource_types:
                        if resource_type not in cls.MODEL_REGISTRY[model_cls]:
                            cls.MODEL_REGISTRY[model_cls].append(resource_type)
                            logger.info(f"Registered model '{model_cls.__name__}' for resource '{resource_type.__name__}'")
            cls.recreate_models()
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
    def field_contains_subclass_union(cls, field_annotation) -> bool:
        """
        Check if the field annotation contains a SubclassUnion.

        Parameters:
        - field_annotation: The type annotation of the field.

        Returns:
        - True if SubclassUnion is present, False otherwise.
        """
        logger.debug(f"Checking if field annotation '{field_annotation}' contains a SubclassUnion")
        if isinstance(field_annotation, type(SubclassUnion)):
            logger.debug(f"Field annotation '{field_annotation}' is directly a SubclassUnion")
            return True
        origin = get_origin(field_annotation)
        if origin is Annotated:
            args = get_args(field_annotation)
            logger.debug(f"Field annotation '{field_annotation}' is Annotated with args {args}")
            return cls.field_contains_subclass_union(args[0])
        elif origin in {list, List, dict, Dict, Union}:
            args = get_args(field_annotation)
            logger.debug(f"Field annotation '{field_annotation}' has origin '{origin.__name__}' with args {args}")
            result = any(cls.field_contains_subclass_union(arg) for arg in args)
            logger.debug(f"Field annotation '{field_annotation}' contains SubclassUnion: {result}")
            return result
        logger.debug(f"Field annotation '{field_annotation}' does not contain a SubclassUnion")
        return False


    @classmethod
    def extract_resource_types_from_field(cls, field_annotation) -> List[Type['ComponentBase']]:
        """
        Extracts all resource types from a field annotation that uses SubclassUnion.

        Parameters:
        - field_annotation: The type annotation of the field.

        Returns:
        - A list of resource type classes.
        """
        logger.debug(f"Extracting resource types from field annotation '{field_annotation}'")
        resource_types = []

        origin = get_origin(field_annotation)
        args = get_args(field_annotation)

        if origin is Annotated:
            # Extract the actual type from Annotated
            logger.debug(f"Field annotation '{field_annotation}' is Annotated")
            field_annotation = args[0]
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)

        if origin is Union:
            logger.debug(f"Field annotation '{field_annotation}' is a Union")
            for arg in args:
                if cls.field_contains_subclass_union(arg):
                    logger.debug(f"Union member '{arg}' contains a SubclassUnion")
                    resource_types.extend(cls.extract_resource_types_from_field(arg))
        elif inspect.isclass(field_annotation) and issubclass(field_annotation, SubclassUnion):
            # Assuming SubclassUnion is generic and parameterized
            logger.debug(f"Field annotation '{field_annotation}' is a subclass of SubclassUnion")
            subclass_args = get_args(field_annotation)
            if subclass_args:
                resource_type = subclass_args[0]
                logger.debug(f"Extracted resource type '{resource_type.__name__}' from SubclassUnion")
                resource_types.append(resource_type)
        elif origin in {list, List}:
            # Handle List[SubclassUnion[ResourceType]]
            item_type = args[0]
            logger.debug(f"Field annotation '{field_annotation}' is a List with item type '{item_type}'")
            resource_types.extend(cls.extract_resource_types_from_field(item_type))
        elif origin in {dict, Dict}:
            # Handle Dict[key_type, SubclassUnion[ResourceType]]
            value_type = args[1]
            logger.debug(f"Field annotation '{field_annotation}' is a Dict with value type '{value_type}'")
            resource_types.extend(cls.extract_resource_types_from_field(value_type))
        else:
            logger.debug(f"Field annotation '{field_annotation}' does not match any known patterns for SubclassUnion")
        
        logger.debug(f"Extracted resource types: {[rt.__name__ for rt in resource_types]}")
        return resource_types

    @classmethod
    def determine_new_type(cls, field_annotation, resource_type):
        """
        Determine the new type for a field based on its annotation and resource type.

        Parameters:
        - field_annotation: The original type annotation.
        - resource_type: The resource type associated with the field.

        Returns:
        - The updated type annotation incorporating SubclassUnion.
        """
        logger.debug(f"Determining new type for field annotation '{field_annotation}' with resource type '{resource_type.__name__}'")
        origin = get_origin(field_annotation)
        args = get_args(field_annotation)

        is_optional = False

        if origin is Union and type(None) in args:
            # Handle Optional and Union types
            non_none_args = [arg for arg in args if arg is not type(None)]
            logger.debug(f"Field annotation '{field_annotation}' is Optional/Union with non-None args {non_none_args}")
            if len(non_none_args) == 1:
                field_annotation = non_none_args[0]
                origin = get_origin(field_annotation)
                args = get_args(field_annotation)
                is_optional = True
                logger.debug(f"Field is Optional with single non-None type '{field_annotation}'")
            else:
                field_annotation = Union[tuple(non_none_args)]
                origin = get_origin(field_annotation)
                args = get_args(field_annotation)
                is_optional = True
                logger.debug(f"Field is Optional with multiple non-None types '{field_annotation}'")

        # Handle Annotated types by extracting the underlying type
        if origin is Annotated:
            # Extract the actual type from Annotated
            logger.debug(f"Field annotation '{field_annotation}' is Annotated")
            field_annotation = args[0]
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)

        if origin in {list, List}:
            # Handle List[SubclassUnion[ResourceType]]
            new_type = List[SubclassUnion[resource_type]]
            logger.debug(f"New type for List field: '{new_type}'")
        elif origin in {dict, Dict}:
            # Handle Dict[key_type, SubclassUnion[ResourceType]]
            key_type, value_type = args
            new_type = Dict[key_type, SubclassUnion[resource_type]]
            logger.debug(f"New type for Dict field: '{new_type}'")
        elif origin is Union:
            # Handle Union types
            union_types = []
            for arg in args:
                if cls.field_contains_subclass_union(arg):
                    union_types.append(SubclassUnion[resource_type])
                    logger.debug(f"Added SubclassUnion[{resource_type.__name__}] to Union types")
                else:
                    union_types.append(arg)
                    logger.debug(f"Added type '{arg}' to Union types")
            new_type = Union[tuple(union_types)]
            logger.debug(f"New Union type: '{new_type}'")
        else:
            # Handle non-generic types
            new_type = SubclassUnion[resource_type]
            logger.debug(f"New non-generic SubclassUnion type: '{new_type}'")

        if is_optional:
            # Include None in the Union and maintain the discriminator
            registered_classes = list(cls.TYPE_REGISTRY.get(resource_type, {}).values())
            if not registered_classes:
                # Use Any as a placeholder if no subclasses are registered
                union_type = Any
                logger.debug(f"No registered subclasses for resource type '{resource_type.__name__}'. Using 'Any' in Optional type.")
            else:
                union_type = Union[tuple(registered_classes)]
                logger.debug(f"Registered subclasses for resource type '{resource_type.__name__}': {[cls.__name__ for cls in registered_classes]}")
            union_with_none = Union[tuple([union_type, type(None)])]
            new_type = Annotated[
                union_with_none,
                Field(discriminator="type")
            ]
            logger.debug(f"Final new type with Optional: '{new_type}'")

        logger.debug(f"Determined new type for field: '{new_type}'")
        return new_type

        
    @classmethod
    def generate_models_with_fields(cls) -> Dict[Type[BaseModel], Dict[str, Any]]:
        """
        Automatically generate the models_with_fields dictionary based on registered models.

        Returns:
        - A dictionary mapping model classes to their fields and corresponding resource types.
        """
        logging.info("Starting generation of models_with_fields")

        models_with_fields = {}
        for model_cls, resource_types in cls.MODEL_REGISTRY.items():
            logging.debug(f"Processing model: {model_cls.__name__}")
            models_with_fields[model_cls] = {}

            for field_name, field in model_cls.__fields__.items():
                logging.debug(f"Processing field: {field_name}")

                field_annotation = model_cls.__annotations__.get(field_name)
                if not field_annotation:
                    logging.debug(f"Field {field_name} in model {model_cls.__name__} has no annotation, skipping.")
                    continue

                # Check if SubclassUnion is used in the field type
                if not cls.field_contains_subclass_union(field_annotation):
                    logging.debug(f"Field {field_name} does not contain SubclassUnion, skipping.")
                    continue  # Only process fields that use SubclassUnion

                # Extract all resource types from the field
                field_resource_types = cls.extract_resource_types_from_field(field_annotation)
                logging.debug(f"Extracted resource types for field {field_name}: {field_resource_types}")

                for resource_type in field_resource_types:
                    new_type = cls.determine_new_type(field_annotation, resource_type)
                    logging.debug(f"Determined new type for resource {resource_type}: {new_type}")

                    models_with_fields[model_cls][field_name] = new_type

        logging.info("Completed generation of models_with_fields")
        return models_with_fields

    @classmethod
    def recreate_models(cls):
        """
        Recreate all models based on the dynamically generated models_with_fields.
        """
        with cls._lock:
            models_with_fields = cls.generate_models_with_fields()
            for model_class, fields in models_with_fields.items():
                for field_name, new_type in fields.items():
                    if field_name in model_class.model_fields:
                        model_class.model_fields[field_name].annotation = new_type
                    else:
                        raise ValueError(f"Field '{field_name}' does not exist in model '{model_class.__name__}'")
                try:
                    model_class.model_rebuild(force=True)
                    logger.debug(f"'{model_class}' has been successfully recreated.")
                except ValidationError as ve:
                    logger.error(f"Validation error while rebuilding model '{model_class.__name__}': {ve}")
                except Exception as e:
                    logger.error(f"Error while rebuilding model '{model_class.__name__}': {e}")
            logger.info("All models have been successfully recreated.")
