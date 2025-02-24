# swarmauri_base/ComponentBase.py

import hashlib
import inspect
import json

from enum import Enum
from threading import Lock
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

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator, ConfigDict

###########################################
# Logging
###########################################
import logging

glogger = logging.getLogger(__name__)
glogger.setLevel(level=logging.INFO)
glogger.propagate = False
if not glogger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    glogger.addHandler(console_handler)


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

class ComponentBase(BaseModel):
    """
    Base class for all components.
    """

    # Class-level registry mapping resource types to their type mappings
    _TYPE_REGISTRY: ClassVar[
        Dict[Type["ComponentBase"], Dict[str, Type["ComponentBase"]]]
    ] = {}
    # Model registry mapping models to their resource types
    _UNIFIED_REGISTRY: ClassVar[Dict[str, Dict[str, Any]]] = {}

    _lock: ClassVar[Lock] = Lock()
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

    ###############################################################
    # Pydantic / Class Initialization
    ###############################################################
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Dynamically update _type to the subclass's name.
        cls._type = cls.__name__
        # Change the annotation for `type` to a Literal of the subclass's name.
        cls.__annotations__["type"] = Literal[cls.__name__]
        # Set the default value for the `type` field.
        cls.type = cls.__name__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @field_validator("type")
    def set_type(cls, v, values):
        if v == "ComponentBase" and cls.__name__ != "ComponentBase":
            return cls.__name__
        return v

    # @classmethod
    # def _get_class_by_type(
    #     cls, parent_class: Type[T], type_name: str
    # ) -> Type["ComponentBase"]:
    #     """
    #     Retrieve a component class based on its resource type and type name.

    #     Parameters:
    #     - parent_class: The base class of the resource.
    #     - type_name: The string identifier for the component type.

    #     Returns:
    #     - The corresponding component class.
    #     """
    #     return cls._TYPE_REGISTRY.get(parent_class, {}).get(type_name)


    ###############################################################
    # SubclassUnion Support Methods
    ###############################################################

    @classmethod
    def _field_contains_subclass_union(cls, field_annotation) -> bool:
        """
        Check if the field annotation contains a SubclassUnion or SubclassUnionMetadata.
        """
        glogger.debug(f"Checking if field '{field_annotation}' contains SubclassUnion.")

        origin = get_origin(field_annotation)
        args = get_args(field_annotation)

        # Check for Annotated fields
        if origin is Annotated:
            for arg in args:
                if isinstance(arg, SubclassUnionMetadata):
                    glogger.debug(f"Field has SubclassUnionMetadata for {arg.parent_class.__name__}.")
                    return True
                if cls._field_contains_subclass_union(arg):
                    return True

        # Check for container types (List, Union, Dict, Set, Tuple, Optional)
        if origin in {Union, List, Dict, Set, Tuple, Optional}:
            for arg in args:
                if cls._field_contains_subclass_union(arg):
                    return True

        return False

    @classmethod
    def _extract_parent_classes_from_field(cls, field_annotation) -> List[Type["ComponentBase"]]:
        """
        Extract all parent classes from a field annotation that uses SubclassUnion.
        """
        glogger.debug(f"Extracting resource types from '{field_annotation}'.")
        parent_classes = []

        try:
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)

            if origin is Annotated:
                # The first arg is the base type, the rest are metadata
                for arg in args[1:]:
                    if isinstance(arg, SubclassUnionMetadata):
                        parent_classes.append(arg.parent_class)
                    else:
                        parent_classes.extend(cls._extract_parent_classes_from_field(arg))
            elif origin in {Union, List, Dict, Set, Tuple, Optional}:
                # Recursively check each arg
                for arg in args:
                    parent_classes.extend(cls._extract_parent_classes_from_field(arg))

            return parent_classes
        except TypeError as e:
            glogger.error(f"TypeError while extracting resource types: {e}")
            return parent_classes


    @classmethod
    def _determine_new_type(cls, field_annotation, parent_class):
        """
        Given a field_annotation and a parent_class, build a new annotation that uses SubclassUnion.
        """
        glogger.debug(f"Determining new type for '{field_annotation}' with parent '{parent_class.__name__}'")
        try:
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)

            is_optional = False

            # Handle Optional[...] or Union[..., None]
            if origin is Union and type(None) in args:
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    field_annotation = non_none_args[0]
                    origin = get_origin(field_annotation)
                    args = get_args(field_annotation)
                    is_optional = True

            # If Annotated, we preserve existing metadata
            if origin is Annotated:
                base_type = args[0]
                metadata = []
                # Filter out old SubclassUnionMetadata; we will add fresh
                for m in args[1:]:
                    if not isinstance(m, SubclassUnionMetadata):
                        metadata.append(m)
                # Add the new SubclassUnionMetadata
                metadata.append(SubclassUnionMetadata(parent_class))
                field_annotation = Annotated[tuple([base_type, *metadata])]

            # Build the actual SubclassUnion
            subclass_union = SubclassUnion[parent_class]

            # Preserve optional
            if is_optional:
                new_type = Union[subclass_union, type(None)]
            else:
                new_type = subclass_union

            return new_type
        except TypeError as e:
            glogger.error(f"TypeError in _determine_new_type: {e}")
            return field_annotation

    ###############################################################
    # Single Getter for SubclassUnion (bound in the factory below)
    ###############################################################
    @staticmethod
    def unified_subclass_getter(parent_cls: Type["ComponentBase"]) -> List[Type["ComponentBase"]]:
        """
        Returns all subtypes for the given parent_cls from the single _UNIFIED_REGISTRY.
        """
        model_name = parent_cls.__name__
        entry = ComponentBase._UNIFIED_REGISTRY.get(model_name)
        if not entry:
            return []
        # Return all the subtype classes
        return list(entry["subtypes"].values())

    ###############################################################
    # Public Decorators: register_model / register_type
    ###############################################################
    @classmethod
    def register_model(cls):
        """
        Decorator to register a base Pydantic model by name in _UNIFIED_REGISTRY.

        - If a model with the same name is already in the registry, logs a duplicate message and returns.
        - Otherwise, creates an entry with:
            {
              "model_cls": <the model class object>,
              "subtypes": {}   # initially empty, can be filled by register_type
            }
        - Finally, calls _recreate_models() to rebuild/refresh.
        """

        def decorator(model_cls: Type[BaseModel]):
            model_name = model_cls.__name__

            if model_name in cls._UNIFIED_REGISTRY:
                glogger.info(
                    f"Model '{model_name}' is already in the unified registry; skipping duplicate."
                )
                return model_cls

            # Create a new registry entry for this base model
            cls._UNIFIED_REGISTRY[model_name] = {
                "model_cls": model_cls,
                "subtypes": {},
            }
            glogger.info(f"Registered base model '{model_name}'.")

            # Optionally, you can scan the model’s fields here for SubclassUnion usage
            # and handle dynamic logic. For example:
            # for field_name, field_info in model_cls.model_fields.items():
            #     # ... detect SubclassUnion, do something ...
            #
            # But that’s optional depending on your architecture.

            cls._recreate_models()
            return model_cls

        return decorator


    @classmethod
    def register_type(
        cls,
        resource_type: Union[Type[T], List[Type[T]]],
        type_name: Optional[str] = None,
    ):
        """
        Decorator to register a subclass under one (or multiple) base models in _UNIFIED_REGISTRY.

        - resource_type: one or more base model classes (e.g. Shape, [Shape, SomeOtherClass])
        - type_name (optional): the string name to register under. If not provided,
          defaults to the subclass's own _type or __name__.

        Process:
        1. For each base model in resource_type:
           - Ensure subclass is indeed a subclass of that base model.
           - If the base model is missing from _UNIFIED_REGISTRY, auto-create an entry.
           - Check for duplicate type_name and skip if it exists.
           - Otherwise, store subclass in the "subtypes" dict for that base model.
        2. Finally, calls _recreate_models() to refresh the system.
        """

        # Normalize resource_type to a list
        if not isinstance(resource_type, list):
            resource_types = [resource_type]
        else:
            resource_types = resource_type

        def decorator(subclass: Type["ComponentBase"]):
            for rt in resource_types:
                # Check that subclass is indeed a subclass of rt
                if not issubclass(subclass, rt):
                    raise TypeError(
                        f"'{subclass.__name__}' must be a subclass of '{rt.__name__}'."
                    )

                # Determine the final name under which this subtype is stored
                final_type_name = type_name or getattr(subclass, "_type", subclass.__name__)
                base_model_name = rt.__name__

                # Ensure there is a registry entry for the base model
                if base_model_name not in cls._UNIFIED_REGISTRY:
                    cls._UNIFIED_REGISTRY[base_model_name] = {
                        "model_cls": rt,
                        "subtypes": {}
                    }
                    glogger.info(
                        f"Created new unified registry entry for base model '{base_model_name}'."
                    )

                subtypes_dict = cls._UNIFIED_REGISTRY[base_model_name]["subtypes"]

                # Check for duplicates
                if final_type_name in subtypes_dict:
                    glogger.info(
                        f"Type '{final_type_name}' already exists under '{base_model_name}'; "
                        f"skipping duplicate."
                    )
                    continue

                # Register the subtype
                subtypes_dict[final_type_name] = subclass
                glogger.info(
                    f"Registered '{subclass.__name__}' as '{final_type_name}' under '{base_model_name}'."
                )

            # Rebuild all models now that we have a new subtype
            cls._recreate_models()
            return subclass

        return decorator




    ###############################################################
    # Rebuild / Recreate Models from the Unified Registry
    ###############################################################

    @classmethod
    def _recreate_models(cls):
        """
        Recreate (or rebuild) all models from _UNIFIED_REGISTRY.
        For each registered model, we can scan its fields for SubclassUnion usage
        and automatically update field types, etc.
        """
        with cls._lock:
            for model_name, entry in cls._UNIFIED_REGISTRY.items():
                model_cls = entry["model_cls"]
                subtypes = entry["subtypes"]  # { "Circle": <class Circle>, ... }

                # 1) Optionally detect fields that use SubclassUnion to add resource types, etc.
                updated_fields = {}
                for field_name, field_info in model_cls.model_fields.items():
                    field_annotation = model_cls.__annotations__.get(field_name)
                    if not field_annotation:
                        continue
                    # If it uses SubclassUnion
                    if cls._field_contains_subclass_union(field_annotation):
                        # Extract parent classes from this field
                        parent_classes = cls._extract_parent_classes_from_field(field_annotation)
                        for pc in parent_classes:
                            # Build a new annotation that references the current subtypes
                            new_type = cls._determine_new_type(field_annotation, pc)
                            updated_fields[field_name] = new_type

                # 2) Apply updated fields
                for fname, new_type in updated_fields.items():
                    original_type = model_cls.model_fields[fname].annotation
                    if original_type != new_type:
                        model_cls.model_fields[fname].annotation = new_type
                        glogger.debug(
                            f"Updated field '{fname}' in model '{model_cls.__name__}' from '{original_type}' to '{new_type}'"
                        )

                # 3) Force a pydantic model rebuild
                try:
                    model_cls.model_rebuild(force=True)
                    glogger.debug(f"Rebuilt model '{model_cls.__name__}'.")
                except ValidationError as ve:
                    glogger.error(f"Validation error rebuilding '{model_cls.__name__}': {ve}")
                except Exception as e:
                    glogger.error(f"Error rebuilding '{model_cls.__name__}': {e}")

            glogger.info("All models have been successfully recreated from the unified registry.")

    ###############################################################
    # YAML / JSON Utilities 
    ###############################################################

    @classmethod
    def model_validate_yaml(cls, yaml_data: str):
        try:
            # Parse YAML into a Python dictionary
            yaml_content = yaml.safe_load(yaml_data)

            # Convert the dictionary to JSON and validate using Pydantic
            return cls.model_validate_json(json.dumps(yaml_content))
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML data: {e}")
        except ValidationError as e:
            raise ValueError(f"Validation failed: {e}")

    def model_dump_yaml(self, fields_to_exclude=None, api_key_placeholder=None):
        if fields_to_exclude is None:
            fields_to_exclude = []

        # Load the JSON string into a Python dictionary
        json_data = json.loads(self.json())

        # Function to recursively remove specific keys and handle api_key placeholders
        def process_fields(data, fields_to_exclude):
            if isinstance(data, dict):
                return {
                    key: (
                        api_key_placeholder
                        if key == "api_key" and api_key_placeholder is not None
                        else process_fields(value, fields_to_exclude)
                    )
                    for key, value in data.items()
                    if key not in fields_to_exclude
                }
            elif isinstance(data, list):
                return [process_fields(item, fields_to_exclude) for item in data]
            else:
                return data

        # Filter the JSON data
        filtered_data = process_fields(json_data, fields_to_exclude)

        # Convert the filtered data into YAML
        return yaml.dump(filtered_data, default_flow_style=False)

    

###########################################
# Exports
###########################################
register_model = ComponentBase.register_model
register_type = ComponentBase.register_type


###########################################
# Subclass Union
###########################################
from swarmauri_typing import UnionFactory

SubclassUnion = UnionFactory(
    bound=ComponentBase.unified_subclass_getter,
    annotation_extenders=[Field(discriminator="type")]
)

