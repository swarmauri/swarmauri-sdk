# swarmauri_core/ComponentBase.py

import hashlib
import inspect
import json

###########################################
# Logging
###########################################
import logging
import warnings
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
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

glogger = logging.getLogger(__name__)
glogger.setLevel(level=logging.INFO)
glogger.propagate = False
if not glogger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)
    glogger.addHandler(console_handler)

warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in v0.9.0. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)


###########################################
# Typing
###########################################

T = TypeVar("T", bound="ComponentBase")


###########################################
# Subclass Union
###########################################


class SubclassUnionMetadata:
    """
    Metadata class to hold resource type information for Annotated fields.
    """

    def __init__(self, parent_class: Type["ComponentBase"]):
        self.parent_class = parent_class


class SubclassUnion(type):
    """
    A generic class to create discriminated unions based on resource types.
    """

    def __class_getitem__(cls, parent_class: Type[T]) -> type:
        """
        Allows usage of SubclassUnion[parent_class] to get the corresponding discriminated Union.

        Parameters:
        - parent_class: The parent class of the resource (e.g., Shape, Kind).

        Returns:
        - An Annotated Union of all subclasses registered under the parent_class, with 'type' as the discriminator.
        """
        registered_classes = list(
            ComponentBase._TYPE_REGISTRY.get(parent_class, {}).values()
        )
        if not registered_classes:
            glogger.debug(
                f"No subclasses registered for parent class '{parent_class.__name__}'. Using 'Any' as a placeholder."
            )
            return Annotated[Any, Field(...), SubclassUnionMetadata(parent_class)]
        else:
            union_type = Union[tuple(registered_classes)]
        return Annotated[
            union_type, Field(discriminator="type"), SubclassUnionMetadata(parent_class)
        ]


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
    _MODEL_REGISTRY: ClassVar[Dict[Type[BaseModel], List[Type["ComponentBase"]]]] = {}
    # Class lock for model rebuilding
    _lock: ClassVar[Lock] = Lock()
    # Class type to support typing prior instantiation
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

    logger: Optional[Any] = Field(exclude=True, default=None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
        # Initialize a logger for the instance using its class name.
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Stops propagation to root
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

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
    def _swm_public_interfaces(cls):
        methods = []
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if (callable(attr_value) and not attr_name.startswith("_")) or isinstance(
                attr_value, property
            ):
                methods.append(attr_name)
        return methods

    @classmethod
    def _swm_ismethod_registered(cls, method_name: str):
        return method_name in cls.swm_public_interfaces()

    @classmethod
    def _swm_method_signature(cls, input_signature):
        for method_name in cls.swm_public_interfaces():
            method = getattr(cls, method_name)
            if callable(method):
                sig = str(inspect.signature(method))
                if sig == input_signature:
                    return True
        return False

    @property
    def _swm_path(self):
        if self.host and self.owner:
            return f"{self.host}/{self.owner}/{self.resource}/{self.name}/{self.id}"
        if self.resource and self.name:
            return f"/{self.resource}/{self.name}/{self.id}"
        return f"/{self.resource}/{self.id}"

    @property
    def _swm_isremote(self):
        return bool(self.host)

    @classmethod
    def _get_class_by_type(
        cls, parent_class: Type[T], type_name: str
    ) -> Type["ComponentBase"]:
        """
        Retrieve a component class based on its resource type and type name.

        Parameters:
        - parent_class: The base class of the resource.
        - type_name: The string identifier for the component type.

        Returns:
        - The corresponding component class.
        """
        return cls._TYPE_REGISTRY.get(parent_class, {}).get(type_name)

    @classmethod
    def _field_contains_subclass_union(cls, field_annotation) -> bool:
        """
        Check if the field annotation contains a SubclassUnion or associated SubclassUnionMetadata metadata.

        Parameters:
        - field_annotation: The type annotation of the field.

        Returns:
        - True if SubclassUnion or SubclassUnionMetadata is present, False otherwise.
        """
        glogger.debug(
            f"Checking if field annotation '{field_annotation}' contains a SubclassUnion or SubclassUnionMetadata"
        )

        origin = get_origin(field_annotation)
        args = get_args(field_annotation)

        # Check for Annotated fields
        if origin is Annotated:
            for arg in args:
                if isinstance(arg, SubclassUnionMetadata):
                    glogger.debug(
                        f"Annotated field contains SubclassUnionMetadata metadata for resource '{arg.parent_class.__name__}'"
                    )
                    return True
                if cls._field_contains_subclass_union(arg):
                    glogger.debug(f"Annotated field contains SubclassUnion in '{arg}'")
                    return True

        # Check for container types (List, Union, Dict)
        if origin in {Union, List, Dict, Set, Tuple, Optional}:
            for arg in args:
                if cls._field_contains_subclass_union(arg):
                    glogger.debug(
                        f"Container field '{field_annotation}' contains SubclassUnion in its arguments"
                    )
                    return True

        glogger.debug(
            f"Field annotation '{field_annotation}' does not contain SubclassUnion or SubclassUnionMetadata"
        )
        return False

    @classmethod
    def _extract_parent_classes_from_field(
        cls, field_annotation
    ) -> List[Type["ComponentBase"]]:
        """
        Extracts all resource types from a field annotation using SubclassUnion.

        Parameters:
        - field_annotation: The type annotation of the field.

        Returns:
        - A list of resource type classes.
        """
        glogger.debug(
            f"Extracting resource types from field annotation '{field_annotation}'"
        )
        parent_classes = []
        try:
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)

            if origin is Annotated:
                for arg in args[1:]:  # Skip the first argument which is the main type
                    if isinstance(arg, SubclassUnionMetadata):
                        parent_classes.append(arg.parent_class)
                        glogger.debug(
                            f"Found SubclassUnionMetadata metadata with resource type '{arg.parent_class.__name__}'"
                        )
                    else:
                        parent_classes.extend(
                            cls._extract_parent_classes_from_field(arg)
                        )

            elif origin in {Union, List, Dict, Set, Tuple, Optional}:
                for arg in args:
                    parent_classes.extend(cls._extract_parent_classes_from_field(arg))

            return parent_classes
        except TypeError as e:
            glogger.error(
                f"TypeError while extracting resource types from field annotation '{field_annotation}': {e}"
            )
            return parent_classes

    @classmethod
    def _determine_new_type(cls, field_annotation, parent_class):
        """
        Determine the new type for a field based on its annotation and resource type.

        Parameters:
        - field_annotation: The original type annotation.
        - parent_class: The resource type associated with the field.

        Returns:
        - The updated type annotation incorporating SubclassUnion.
        """
        glogger.debug(
            f"Determining new type for field annotation '{field_annotation}' with resource type '{parent_class.__name__}'"
        )
        try:
            origin = get_origin(field_annotation)
            args = get_args(field_annotation)

            is_optional = False

            # Handle Optional[...] (Union[..., NoneType])
            if origin is Union and type(None) in args:
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    field_annotation = non_none_args[0]
                    origin = get_origin(field_annotation)
                    args = get_args(field_annotation)
                    is_optional = True
                else:
                    # Multiple non-None types, complex Union
                    glogger.warning(
                        f"Field annotation '{field_annotation}' has multiple non-None Union types; optionality may not be preserved correctly."
                    )

            # Handle Annotated
            if origin is Annotated:
                base_type = args[0]
                glogger.debug(f"Base type for field: {base_type}")
                metadata = [
                    arg
                    for arg in args[1:]
                    if not isinstance(arg, SubclassUnionMetadata)
                ]
                # Append the new SubclassUnionMetadata
                metadata.append(SubclassUnionMetadata(parent_class))
                glogger.debug(
                    f"Preserving existing metadata and adding SubclassUnionMetadata for resource '{parent_class.__name__}'"
                )
                field_annotation = Annotated[tuple([base_type, *metadata])]

            # Construct the new type with SubclassUnion and discriminated Union
            subclass_union = SubclassUnion[parent_class]

            # Preserve Optionality if necessary
            if is_optional:
                new_type = Union[subclass_union, type(None)]
            else:
                new_type = subclass_union

            glogger.debug(f"New type for field: {new_type}")
            return new_type
        except TypeError as e:
            glogger.error(
                f"TypeError while determining new type for field annotation '{field_annotation}': {e}"
            )
            return field_annotation  # Fallback to original type if error occurs

    @classmethod
    def _generate_models_with_fields(cls) -> Dict[Type[BaseModel], Dict[str, Any]]:
        """
        Automatically generate the models_with_fields dictionary based on registered models.

        Returns:
        - A dictionary mapping model classes to their fields and corresponding resource types.
        """
        glogger.debug("Starting generation of models_with_fields")

        models_with_fields = {}
        for model_cls, resource_types in cls._MODEL_REGISTRY.items():
            logging.debug(f"Processing model: {model_cls.__name__}")
            models_with_fields[model_cls] = {}

            for field_name, field in model_cls.model_fields.items():
                logging.debug(f"Processing field: {field_name}")

                field_annotation = model_cls.__annotations__.get(field_name)
                if not field_annotation:
                    logging.debug(
                        f"Field {field_name} in model {model_cls.__name__} has no annotation, skipping."
                    )
                    continue

                # Check if SubclassUnion is used in the field type
                if not cls._field_contains_subclass_union(field_annotation):
                    logging.debug(
                        f"Field {field_name} does not contain SubclassUnion, skipping."
                    )
                    continue  # Only process fields that use SubclassUnion

                # Extract all resource types from the field
                field_resource_types = cls._extract_parent_classes_from_field(
                    field_annotation
                )
                logging.debug(
                    f"Extracted resource types for field {field_name}: {field_resource_types}"
                )

                for resource_type in field_resource_types:
                    new_type = cls._determine_new_type(field_annotation, resource_type)
                    glogger.debug(
                        f"Determined new type for resource {resource_type}: {new_type}"
                    )

                    models_with_fields[model_cls][field_name] = new_type

        glogger.info("Completed generation of models_with_fields")
        return models_with_fields

    @classmethod
    def _recreate_type_models(cls) -> Dict[Type["ComponentBase"], Dict[str, Any]]:
        """
        Generate a mapping of component types to their fields and updated type annotations.

        Returns:
        - A dictionary mapping component classes to their fields and corresponding new type annotations.
        """
        glogger.debug("Starting generation of type models for _TYPE_REGISTRY")

        type_models_with_fields = {}
        for resource_type, type_dict in cls._TYPE_REGISTRY.items():
            glogger.debug(f"Processing resource type: {resource_type.__name__}")
            for type_name, component_cls in type_dict.items():
                glogger.debug(f"Processing component class: {component_cls.__name__}")
                type_models_with_fields[component_cls] = {}

                for field_name, field in component_cls.model_fields.items():
                    glogger.debug(f"Processing field: {field_name}")

                    field_annotation = component_cls.__annotations__.get(field_name)
                    if not field_annotation:
                        glogger.debug(
                            f"Field '{field_name}' in component '{component_cls.__name__}' has no annotation, skipping."
                        )
                        continue

                    # Check if SubclassUnion is used in the field type
                    if not cls._field_contains_subclass_union(field_annotation):
                        glogger.debug(
                            f"Field '{field_name}' does not contain SubclassUnion, skipping."
                        )
                        continue  # Only process fields that use SubclassUnion

                    # Extract all resource types from the field
                    field_resource_types = cls._extract_parent_classes_from_field(
                        field_annotation
                    )
                    if not field_resource_types:
                        glogger.warning(
                            f"No resource types extracted for field '{field_name}' in component '{component_cls.__name__}'"
                        )
                        continue
                    glogger.debug(
                        f"Extracted resource types for field '{field_name}': {[rt.__name__ for rt in field_resource_types]}"
                    )

                    for resource_type_in_field in field_resource_types:
                        try:
                            new_type = cls._determine_new_type(
                                field_annotation, resource_type_in_field
                            )
                            glogger.debug(
                                f"Determined new type for resource '{resource_type_in_field.__name__}': {new_type}"
                            )
                            type_models_with_fields[component_cls][field_name] = (
                                new_type
                            )
                        except Exception as e:
                            glogger.error(
                                f"Error determining new type for field '{field_name}' in component '{component_cls.__name__}': {e}"
                            )
                            continue  # Proceed with other resource types and fields

        glogger.info("Completed generation of type models for _TYPE_REGISTRY")
        return type_models_with_fields

    @classmethod
    def _recreate_models(cls):
        """
        Recreate all models based on the dynamically generated models_with_fields and type_models_with_fields.
        """
        with cls._lock:
            # Generate field mappings for _MODEL_REGISTRY
            models_with_fields = cls._generate_models_with_fields()
            # Generate field mappings for _TYPE_REGISTRY
            type_models_with_fields = cls._recreate_type_models()

            # Combine both dictionaries
            combined_models_with_fields = {
                **models_with_fields,
                **type_models_with_fields,
            }

            for model_class, fields in combined_models_with_fields.items():
                for field_name, new_type in fields.items():
                    if field_name in model_class.model_fields:
                        original_type = model_class.model_fields[field_name].annotation
                        if original_type != new_type:
                            model_class.model_fields[field_name].annotation = new_type
                            glogger.debug(
                                f"Updated field '{field_name}' in model '{model_class.__name__}' from '{original_type}' to '{new_type}'"
                            )
                        else:
                            glogger.debug(
                                f"No change for field '{field_name}' in model '{model_class.__name__}'"
                            )
                    else:
                        glogger.error(
                            f"Field '{field_name}' does not exist in model '{model_class.__name__}'"
                        )
                        continue  # Skip to next field

                try:
                    model_class.model_rebuild(force=True)
                    glogger.debug(
                        f"'{model_class.__name__}' has been successfully recreated."
                    )
                except ValidationError as ve:
                    glogger.error(
                        f"Validation error while rebuilding model '{model_class.__name__}': {ve}"
                    )
                except Exception as e:
                    glogger.error(
                        f"Error while rebuilding model '{model_class.__name__}': {e}"
                    )
            glogger.info("All models have been successfully recreated.")

    ###############################################################
    # Yaml Support
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

    ###############################################################
    # Public Class Methods
    ###############################################################
    @classmethod
    def register_type(
        cls,
        resource_type: Union[Type[T], List[Type[T]]],
        type_name: Optional[str] = None,
    ):
        """
        Decorator to register a component class with a specific type name under one or multiple resource types,
        preventing duplicate registrations.
        """
        # Normalize resource_type to a list (if it isn’t already).
        if not isinstance(resource_type, list):
            resource_types = [resource_type]
        else:
            resource_types = resource_type

        def decorator(subclass: Type["ComponentBase"]):
            # Ensure the subclass is a subclass of at least one provided resource type.
            if not any(issubclass(subclass, rt) for rt in resource_types):
                allowed = ", ".join(rt.__name__ for rt in resource_types)
                raise TypeError(
                    f"Registered class '{subclass.__name__}' must be a subclass of one of ({allowed})"
                )
            # Resolve the type name: use provided type_name or fallback to subclass's _type or __name__
            resolved_type_name = type_name or getattr(
                subclass, "_type", subclass.__name__
            )

            # Register the subclass for each resource type.
            for rt in resource_types:
                # Canonicalize the resource type key: if one with the same name already exists, use it.
                canonical_resource_type = rt
                for existing_resource in cls._TYPE_REGISTRY.keys():
                    if existing_resource.__name__ == rt.__name__:
                        canonical_resource_type = existing_resource
                        break

                if canonical_resource_type not in cls._TYPE_REGISTRY:
                    cls._TYPE_REGISTRY[canonical_resource_type] = {}
                if resolved_type_name in cls._TYPE_REGISTRY[canonical_resource_type]:
                    glogger.info(
                        f"Type '{resolved_type_name}' for resource '{canonical_resource_type.__name__}' is already registered; skipping duplicate registration."
                    )
                    continue  # Skip duplicate registration for this resource type.
                cls._TYPE_REGISTRY[canonical_resource_type][resolved_type_name] = (
                    subclass
                )
                glogger.info(
                    f"Registered type '{resolved_type_name}' for resource '{canonical_resource_type.__name__}' with subclass '{subclass.__name__}'"
                )
            cls._recreate_models()
            return subclass

        return decorator

    @classmethod
    def register_model(cls):
        """
        Decorator to register a Pydantic model by automatically detecting resource types
        from fields that use SubclassUnion, ensuring no duplicate registrations occur.
        """

        def decorator(model_cls: Type[BaseModel]):
            # Check if any already-registered model has the same __name__.
            for registered_model in cls._MODEL_REGISTRY:
                if registered_model.__name__ == model_cls.__name__:
                    glogger.info(
                        f"Model '{model_cls.__name__}' is already registered; skipping duplicate registration."
                    )
                    return model_cls

            # Initialize a set for the model if not already present.
            cls._MODEL_REGISTRY[model_cls] = set()

            # Inspect all fields to find SubclassUnion annotations.
            for field_name, field in model_cls.model_fields.items():
                field_annotation = model_cls.__annotations__.get(field_name)
                if not field_annotation:
                    continue

                # Check if the field uses SubclassUnion.
                if cls._field_contains_subclass_union(field_annotation):
                    # Extract resource types from the field's annotation.
                    resource_types = cls._extract_parent_classes_from_field(
                        field_annotation
                    )
                    for resource_type in resource_types:
                        # Add to the set (automatically avoids duplicates).
                        if resource_type not in cls._MODEL_REGISTRY[model_cls]:
                            cls._MODEL_REGISTRY[model_cls].add(resource_type)
                            glogger.info(
                                f"Registered model '{model_cls.__name__}' for resource '{resource_type.__name__}'"
                            )
                        else:
                            glogger.debug(
                                f"Resource '{resource_type.__name__}' already registered for model '{model_cls.__name__}', skipping duplicate."
                            )
            # Convert the set back to a list if needed by downstream code.
            cls._MODEL_REGISTRY[model_cls] = list(cls._MODEL_REGISTRY[model_cls])
            cls._recreate_models()
            return model_cls

        return decorator


###########################################
# Exports
###########################################
register_model = ComponentBase.register_model
register_type = ComponentBase.register_type
